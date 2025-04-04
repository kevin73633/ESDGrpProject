#!/usr/bin/env python3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os
import requests
import boto3
import random

app = Flask(__name__)
# Update the CORS configuration
CORS(app, 
     origins=["http://localhost:8080", "http://localhost:8081"],
     supports_credentials=True)

# Add this after_request handler for more control
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin and (origin == 'http://localhost:8080' or origin == 'http://localhost:8081'):
        # For preflight requests
        response.headers.set('Access-Control-Allow-Origin', origin)
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

# Session configuration
app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'dealshare-login-secret-key-2025')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Or 'None' with secure=True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Session lasts for 1 day

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://" + str(environ.get("DBLOGIN")) + "@localhost:3306/Project"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# OTP API URL from OutSystems
OTP_API_URL = "https://personal-bppzf7rc.outsystemscloud.com/OTPClone/rest/OTPAPICLONE/GenerateOTP"

db = SQLAlchemy(app)

def send_sms(phone_number, message):
    """
    Send SMS to any phone number using Amazon SNS
    
    Args:
        phone_number: Phone number in E.164 format (+6512345678)
        message: The text message to send
    
    Returns:
        Dictionary with success status and message ID or error
    """
    try:
        # Initialize SNS client
        sns_client = boto3.client('sns',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Format phone number if needed
        if not phone_number.startswith('+'):
            # Assuming Singapore number
            if phone_number.startswith('0'):
                phone_number = '+65' + phone_number[1:]
            else:
                phone_number = '+65' + phone_number
        
        # Send the SMS
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'DEALSHARE'  # Custom sender ID
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'  # Higher priority
                }
            }
        )
        
        return {
            "success": True,
            "message_id": response.get('MessageId')
        }
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Authentication required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'uid' not in session:
            return jsonify({
                "code": 401,
                "message": "Authentication required"
            }), 401
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

class User(db.Model):
    __tablename__ = 'user'

    uid = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    accnum = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(16), nullable=True)

    def json(self):
        dto = {
            'uid': self.uid,
            'name': self.name,
            'rating': self.rating,
            'accnum': self.accnum,
            'phone': self.phone, 
        }
        return dto

#===========================================================
# Login and Authentication Routes
#===========================================================

@app.route("/generate-otp", methods=['GET'])
def generate_otp_proxy():
    """Generate OTP by proxying the OutSystems API"""
    try:
        # Call the OutSystems API
        response = requests.get(OTP_API_URL, timeout=10)
        
        print(f"OutSystems API response: Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # Parse the JSON response
                otp_data = response.json()
                
                # Make sure we return a response with the expected format
                if 'OTP' in otp_data:
                    return jsonify(otp_data)
                else:
                    # If the response doesn't have an OTP field, wrap it
                    return jsonify({"OTP": str(otp_data)})
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                
                # Try to use the raw response text
                try:
                    # If it's just a number without JSON formatting
                    otp_value = response.text.strip()
                    return jsonify({"OTP": otp_value})
                except:
                    # Generate a fallback OTP
                    fallback_otp = str(random.randint(100000, 999999))
                    return jsonify({"OTP": fallback_otp})
        else:
            print(f"API returned non-200 status: {response.status_code}")
            # Generate a fallback OTP
            fallback_otp = str(random.randint(100000, 999999))
            return jsonify({"OTP": fallback_otp})
    
    except Exception as e:
        print(f"Error proxying OTP generation: {e}")
        # Generate a fallback OTP
        fallback_otp = str(random.randint(100000, 999999))
        return jsonify({"OTP": fallback_otp})

# # Verify user and retrieve phone number
@app.route("/verify-user", methods=['POST'])
def verify_user():
    data = request.get_json()
    uid = data.get('uid')
    
    if not uid:
        return jsonify({
            "code": 400,
            "message": "User ID is required"
        }), 400
    
    # Get user from database
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "User not found"
        }), 404
    
    # Store the user ID in session temporarily
    session['temp_uid'] = uid
    
    # Return the phone number
    return jsonify({
        "code": 200,
        "message": "User verified successfully",
        "data": {
            "phone": user.phone
        }
    })

# Generate and send OTP
@app.route("/send-otp", methods=['POST'])
def send_otp():
    """Send OTP via AWS SNS"""
    data = request.get_json()
    phone = data.get('phone')
    otp = data.get('otp')
    
    if not phone or not otp:
        return jsonify({
            "code": 400,
            "message": "Phone number and OTP are required"
        }), 400
    
    # Store OTP in session for verification later
    session['otp'] = otp
    
    # Create OTP message
    message = f"Your DealShare verification code is: {otp}. This code will expire in 10 minutes."
    
    # Development mode check - if AWS credentials not configured, log instead of sending
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        print(f"DEVELOPMENT MODE: OTP for {phone}: {otp}")
        return jsonify({
            "code": 200,
            "message": "OTP sent successfully (Development Mode)",
            "data": {
                "message_id": "dev-mode",
                "dev_otp": otp  # Only include in development
            }
        })
    
    # Send SMS
    sms_result = send_sms(phone, message)
    
    if sms_result["success"]:
        return jsonify({
            "code": 200,
            "message": "OTP sent successfully",
            "data": {
                "message_id": sms_result["message_id"]
            }
        })
    else:
        print(f"SMS sending failed: {sms_result['error']}")
        # Fall back to development mode if SMS fails
        return jsonify({
            "code": 200,  # Still return success to frontend for testing
            "message": "OTP sent successfully (Fallback Mode)",
            "data": {
                "message_id": "fallback-mode",
                "dev_otp": otp  # Only include in development
            }
        })

# Verify OTP and complete login
@app.route("/verify-otp", methods=['POST'])
def verify_otp():
    """Verify OTP and complete login"""
    data = request.get_json()
    uid = data.get('uid')
    entered_otp = data.get('otp')
    
    print(f"Verifying OTP: UID={uid}, Entered OTP={entered_otp}, Session OTP={session.get('otp')}")
    
    # Get stored OTP from session
    stored_otp = session.get('otp')
    temp_uid = session.get('temp_uid')
    
    # For debugging, add more logs
    print(f"Session contents: {session}")
    
    # Check if we have an OTP in the session
    if not stored_otp:
        print("No OTP found in session")
        return jsonify({
            "code": 400,
            "message": "No verification code found. Please request a new code."
        }), 400
    
    # Skip UID check for now to isolate the issue
    # if not temp_uid or temp_uid != uid:
    #     return jsonify({
    #         "code": 400,
    #         "message": "Invalid session"
    #     }), 400
    
    # Verify OTP
    if stored_otp != entered_otp:
        return jsonify({
            "code": 401,
            "message": "Invalid verification code"
        }), 401
    
    # OTP verified, get user from database
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    
    if not user:
        return jsonify({
            "code": 404,
            "message": "User not found"
        }), 404
    
    # Clear temporary session data
    session.pop('otp', None)
    session.pop('temp_uid', None)
    
    # Set authenticated session
    session['uid'] = user.uid
    session['name'] = user.name
    session.permanent = True
    
    print(f"User authenticated: {user.uid}, session: {session}")
    
    return jsonify({
        "code": 200,
        "message": "Login successful",
        "data": {
            "user": user.json()
        }
    })

# # Legacy login route (without OTP)
# @app.route("/login", methods=['POST'])
# def login():
#     data = request.get_json()
#     uid = data.get('uid')
    
#     user = db.session.scalar(db.select(User).filter_by(uid=uid))
    
#     if user:
#         # Print for debugging
#         print(f"User found: {user.uid}, setting session")
        
#         # Set session data
#         session['uid'] = user.uid
#         session['name'] = user.name
#         session.permanent = True
        
#         # Print session to verify
#         print(f"Session after login: {session}")
        
#         return jsonify({
#             "code": 200,
#             "data": {"user": user.json()},
#             "message": "Login successful"
#         })
    
#     return jsonify({
#         "code": 401,
#         "message": "Invalid user ID"
#     }), 401

# Check authentication status
@app.route("/check-auth", methods=['GET'])
def check_auth():
    print(f"Session in check-auth: {session}")
    print(f"UID in session: {session.get('uid')}")
    
    if 'uid' in session:
        return jsonify({
            "code": 200,
            "data": {
                "authenticated": True,
                "uid": session['uid'],
                "name": session.get('name', '')
            }
        })
    else:
        return jsonify({
            "code": 401,
            "data": {"authenticated": False},
            "message": "Not authenticated"
        }), 401

# Logout
@app.route("/logout", methods=['POST'])
def logout():
    try:
        # Clear the session
        session.clear()
        
        # Return success response
        return jsonify({
            "code": 200,
            "message": "Successfully logged out"
        }), 200
        
    except Exception as e:
        # Log the error
        print(f"Error during logout: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        return jsonify({
            "code": 500,
            "message": f"An error occurred during logout: {str(e)}"
        }), 500

#===========================================================
# User Management Routes
#===========================================================

@app.route("/user/profile", methods=['GET'])
@login_required
def get_profile():
    uid = session['uid']
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    if user:
        return jsonify({
            "code": 200,
            "data": {
                "user": user.json()
            }
        })
    return jsonify({
        "code": 404,
        "message": "User not found"
    }), 404

@app.route("/user", methods=['GET'])
def get_all():
    userlist = db.session.scalars(db.select(User)).all()
    print(userlist)
    if len(userlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "users": [user.json() for user in userlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404

@app.route("/user/<string:uid>", methods=['GET'])
def get_single_user(uid):
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    if user:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "user": user.json()
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

@app.route("/user/getAccNumFromUser/<string:uid>", methods=['GET'])
def get_single_user_Acc(uid):
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    if user:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "AccNum": user.json()["accnum"]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

@app.route("/user/getPhoneFromUser/<string:uid>", methods=['GET'])
def get_single_user_phone(uid):
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    if user:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "phone": user.json()["phone"]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

@app.route("/user/<string:uid>/rating", methods=['PUT'])
def update_user_rating(uid):
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    
    if not user:
        return jsonify(
            {
                "code": 404,
                "message": "User not found."
            }
        ), 404
    
    data = request.get_json()
    if 'rating' not in data:
        return jsonify(
            {
                "code": 400,
                "message": "Rating is required."
            }
        ), 400
    
    try:
        old_rating = user.rating
        user.rating = data['rating']
        db.session.commit()
        
        return jsonify(
            {
                "code": 200,
                "data": user.json(),
                "message": "User rating updated successfully."
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred updating the user rating. {str(e)}"
            }
        ), 500
        
if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": user service with OTP authentication...")
    app.run(host='0.0.0.0', port=5001, debug=True)

# @app.route("/order/<string:order_id>")
# def find_by_order_id(uid):
#     order = db.session.scalar(db.select(User).filter_by(order_id=order_id))
#     if order:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": order.json()
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#             "data": {
#                 "order_id": order_id
#             },
#             "message": "Order not found."
#         }
#     ), 404


# @app.route("/order", methods=['POST'])
# def create_order():
#     customer_id = request.json.get('customer_id', None)
#     order = User(customer_id=customer_id, status='NEW')

#     cart_item = request.json.get('cart_item')
#     for item in cart_item:
#         order.order_item.append(Order_Item(
#             book_id=item['book_id'], quantity=item['quantity']))

#     try:
#         db.session.add(order)
#         db.session.commit()
#     except Exception as e:
#         print("Error: {}".format(str(e)))
#         return jsonify(
#             {
#                 "code": 500,
#                 "message": "An error occurred while creating the order. " + str(e)
#             }
#         ), 500

#     return jsonify(
#         {
#             "code": 201,
#             "data": order.json()
#         }
#     ), 201


# @app.route("/order/<string:order_id>", methods=['PUT'])
# def update_order(order_id):
#     try:
#         order = db.session.scalar(db.select(Order).filter_by(order_id=order_id))
#         if not order:
#             return jsonify(
#                 {
#                     "code": 404,
#                     "data": {
#                         "order_id": order_id
#                     },
#                     "message": "Order not found."
#                 }
#             ), 404

#         # update status
#         data = request.get_json()
#         if data['status']:
#             order.status = data['status']
#             db.session.commit()
#             return jsonify(
#                 {
#                     "code": 200,
#                     "data": order.json()
#                 }
#             ), 200
#     except Exception as e:
#         print("Error: {}".format(str(e)))
#         return jsonify(
#             {
#                 "code": 500,
#                 "data": {
#                     "order_id": order_id
#                 },
#                 "message": "An error occurred while updating the order. " + str(e)
#             }
#         ), 500



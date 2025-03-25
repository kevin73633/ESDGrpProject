#!/usr/bin/env python3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

app = Flask(__name__)

# Update to include supports_credentials
CORS(app, 
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     resources={r"/*": {"origins": "http://localhost:8080"}})

# Session configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Use a strong secret key
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Or 'None' with secure=True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Session lasts for 1 day

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root:root@localhost:3306/Project"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


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

# Login route
@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    uid = data.get('uid')
    
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    
    if user:
        # Print for debugging
        print(f"User found: {user.uid}, setting session")
        
        # Set session data
        session['uid'] = user.uid
        session['name'] = user.name
        session.permanent = True
        
        # Print session to verify
        print(f"Session after login: {session}")
        
        return jsonify({
            "code": 200,
            "data": {"user": user.json()},
            "message": "Login successful"
        })
    
    return jsonify({
        "code": 401,
        "message": "Invalid user ID"
    }), 401

# Logout route
@app.route("/logout", methods=['POST'])
def logout():
    # Clear the session
    session.clear()
    return jsonify({
        "code": 200,
        "message": "Logout successful"
    })


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


# Protected route example
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
@login_required
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
@login_required
def get_single_user(uid):
    user = db.session.scalar(db.select(User).filter_by(uid=uid))
    if user:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "user": [user.json()]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404

@app.route("/user/getAccNumFromUser/<string:uid>", methods=['GET'])
@login_required
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
            "message": "There are no users."
        }
    ), 404

@app.route("/user/getPhoneFromUser/<string:uid>", methods=['GET'])
@login_required
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


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": users ...")
    app.run(host='0.0.0.0', port=5001, debug=True)

#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
from invokes import invoke_http
import os
import json
import boto3
import uuid
from datetime import datetime
import amqp_lib
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Define microservice URLs
DEAL_SERVICE_URL = "http://deal:5020"
PRODUCT_SERVICE_URL = "http://product:5005"
USER_SERVICE_URL = "http://user:5001"
PAYMENT_SERVICE_URL = "http://payment:5031"

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

# AMQP Configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_EXCHANGE = os.environ.get('RABBITMQ_EXCHANGE', 'deal_events')

def send_sms(phone_number, message):
    return {
            "success": True,
            "message_id": 000
        }
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
                    'StringValue': 'DEALSVC'  # Custom sender ID
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

@app.route("/report_user", methods=['POST'])
def report_user():
    """
    Report a user by orchestrating the entire user report flow
    """
    # Step 1: Get deal information
    dealid = request.json['dealId']
    currentuserid = request.json['UserID']
    reporteduserid = request.json['ReportedUserID']

    # Step 3: Get buyer information
    user_result = invoke_http(f"{USER_SERVICE_URL}/user/{currentuserid}", method="GET")
    if user_result["code"] != 200:return jsonify({"code": 404,"message": f"Buyer {currentuserid} not found."}), 404
    user_data = user_result["data"]["user"]

    # Get buyer phone number (assuming you've added the endpoint in user.py)
    user_phone_result = invoke_http(f"{USER_SERVICE_URL}/user/getPhoneFromUser/{currentuserid}", method="GET")
    user_phone = None
    if user_phone_result["code"] == 200:
        user_phone = user_phone_result["data"]["phone"]


    notification_payload = None
    # Step 6: Create notification payload with all relevant information
    notification_payload = {
        "event_type": "user_reported",
        "timestamp": datetime.now().isoformat(),
        "deal_id": dealid,
        "buyer": {
            "id": user_data["uid"],
            "name": user_data["name"],
            "phone": user_phone
        },
    }
    
    # Step 7: Send notifications via AMQP
    amqp_lib.publish_message(
        routing_key="user.reported",
        message=notification_payload,
        exchange_name=RABBITMQ_EXCHANGE,
        hostname=RABBITMQ_HOST
    )
    
    # Step 8: Send SMS notifications
    sms_results = {}
    if user_phone:
        buyer_message = f"Your report against user {user_data['name']} has been received. Deal ID: {dealid}"
        sms_results["buyer_sms"] = send_sms(user_phone, buyer_message)
    
    # Return success response with combined data
    return jsonify({
        "code": 200,
        "message": "User reported successfully",
        "data": {
            "notifications": {
                "amqp_sent": True,
                "sms_results": sms_results
            }
        }
    })


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": report user composite service ...")
    app.run(host='0.0.0.0', port=5300, debug=True)
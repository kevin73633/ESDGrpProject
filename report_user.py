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
from flasgger import Swagger

load_dotenv()

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Add Swagger configuration
app.config['SWAGGER'] = {
    'title': 'User Report API',
    'version': "1.0",
    'openapi': "3.0.2",
    'description': 'API for handling user reporting workflow across multiple microservices',
    'specs': [
        {
            'endpoint': 'ReportUserAPI',
            'route': '/ReportUserAPI.json',
            'rule_filter': lambda rule: True,  # all in
            'model_filter': lambda tag: True,  # all in
        }
    ],
    'specs_route': "/apidocs/"
}
swagger = Swagger(app)

# Define microservice URLs
DEAL_SERVICE_URL = "http://deal:5020"
USER_SERVICE_URL = "http://user:5001"
PRODUCT_SERVICE_URL = "http://product:5005"
PAYMENT_SERVICE_URL = "http://payment:5031"
CHAT_SERVICE_URL = "http://chat:5087"
CHATGPT_SERVICE_URL = "http://chatgpt:5002"
REPORTLOG_SERVICE_URL = "http://reportLog:5004"
RATING_SERVICE_POST_URL = "https://personal-nzmfqiqp.outsystemscloud.com/RatingAPI_REST/rest/v1/updateuserrating"
RATING_SERVICE_GET_URL = "https://personal-nzmfqiqp.outsystemscloud.com/RatingAPI_REST/rest/v1/userRating/RatedID/?RatedID="

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
    # """
    # Report a user by orchestrating the entire user report flow
    # """
    """
    Report a user for inappropriate behavior
    ---
    tags:
      - User Reporting
    summary: Submit a user report and perform necessary actions
    description: Process a user report, analyze chat for harmful content, update ratings if needed, and handle refunds if required
    requestBody:
      description: User report details
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - dealId
              - Reason
              - UserID
              - ReportedUserID
            properties:
              dealId:
                type: string
                description: ID of the deal associated with the report
              Reason:
                type: string
                description: Reason for reporting the user
              UserID:
                type: string
                description: ID of the user submitting the report
              ReportedUserID:
                type: string
                description: ID of the user being reported
            example:
              dealId: "11111111"
              Reason: "Scam Behavior"
              UserID: "12345678"
              ReportedUserID: "22345678"
    responses:
      200:
        description: User report processed successfully
      404:
        description: Deal, chat, or user not found
      500:
        description: Server error or processing failure
    """
    # Step 1: Get deal information
    
    dealid = request.json['dealId']
    reason = request.json['Reason']
    currentuserid = request.json['UserID']
    reporteduserid = request.json['ReportedUserID']

    deal_result = invoke_http(f"{DEAL_SERVICE_URL}/deal/{dealid}", method="GET")
    if deal_result["code"] != 200:return jsonify({"code": 404,"message": f"Deal {dealid} not found."}), 404
    deal_data = deal_result["data"]["deal"]


    chat_result = invoke_http(f"{CHAT_SERVICE_URL}/chat/getmessagebetween/{dealid}", method="GET")
    if chat_result["code"] != 200:return jsonify({"code": 404,"message": f"chat in {dealid} not found."}), 404
    chat_data = chat_result["data"]["messages"]

    chatgpt_result = invoke_http(f"{CHATGPT_SERVICE_URL}/analyze", method="POST", json={"message": chat_data})
    if chatgpt_result["code"] != 200:return jsonify({"code": 404,"message": f"chat in {dealid} not found."}), 404
    chatgpt_data = chatgpt_result["data"]['is_harmful']

    reportLog_post_payload = {
        "UserID": currentuserid,
        "ReportedUserID": reporteduserid,
        "Reason": reason,
        "Status": chatgpt_data
    }
    reportLog_post_result = invoke_http(
        f"{REPORTLOG_SERVICE_URL}/reportLog",
        method="POST",
        json=reportLog_post_payload
    )
    if reportLog_post_result["code"] != 200:
        return jsonify({
            "code": 404,
            "message": f"Rating failed: {reportLog_post_result['error']}"
        }), 404
    
    payment_result_string = None
    # refund deal if reported
    if (deal_data['status'] == 1 or deal_data['status'] == 3):
        # Get buyer account number
        user_account_result = invoke_http(f"{USER_SERVICE_URL}/user/getAccNumFromUser/{deal_data["buyerid"]}", method="GET")
        if user_account_result["code"] != 200:return jsonify({"code": 404,"message": f"Buyer account information not found."}), 404
        user_account = user_account_result["data"]["AccNum"]

        # Step 2: Get product details
        product_result = invoke_http(f"{PRODUCT_SERVICE_URL}/products/{deal_data['productid']}", method="GET")
        if product_result["code"] != 200:return jsonify({"code": 404,"message": f"Product {deal_data['productid']} not found."}), 404
        product_data = product_result["data"]["product"]

        # Step 4: Process payment (escrow)
        payment_payload = {
            "accnum": user_account,
            "amount": product_data["price"]
        }
        
        payment_result = invoke_http(
            f"{PAYMENT_SERVICE_URL}/payment/refund",
            method="POST",
            json=payment_payload
        )
        if payment_result["code"] != 200:
            return jsonify({
                "code": payment_result["code"],
                "message": f"Payment failed: {payment_result['message']}"
            }), payment_result["code"]
        payment_result_string = payment_result["transaction"]
        # implement compensating transaction here (refund) and set status to -1

    update_deal_payload = {"status": -1}
    update_deal_result = invoke_http(
        f"{DEAL_SERVICE_URL}/deal/{dealid}/status",
        method="PUT",
        json=update_deal_payload
    )
    if chatgpt_data == False:
        return jsonify({
            "code": 200,
            "message": "User report not harmful",
            "payment" : payment_result_string,
            "data": {
                "is_harmful": chatgpt_data
            }
        })
    # Step 5: Post rating to the rating service
    rating_post_payload = {
        "CreatedAt": datetime.now().isoformat(),
        "RaterID": currentuserid,
        "RatedID": reporteduserid,
        "DealID": dealid,
        "RatingScore": 0,
        "RatingType": "report"
    }
    rating_post_result = invoke_http(
        f"{RATING_SERVICE_POST_URL}",
        method="POST",
        json=rating_post_payload
    )
    if rating_post_result["Success"] != True:
        return jsonify({
            "code": 404,
            "message": f"Rating failed: {rating_post_result['ErrorMessage']}"
        }), 404
    # Step 6: Get all ratings for the seller
    rating_get_result = invoke_http(
        f"{RATING_SERVICE_GET_URL}{reporteduserid}",
        method="GET"
    )
    if rating_get_result["Result"]["Success"] != True:
        return jsonify({
            "code": 404,
            "message": f"Rating failed: {rating_get_result['ErrorMessage']}"
        }), 404
    # Calculate average rating
    ratings = rating_get_result["Rating"]
    total_score = sum(rating["RatingScore"] for rating in ratings)
    average_rating = total_score / len(ratings) if ratings else 0
    # Step 7: Update seller rating
    update_seller_rating_payload = {"rating": average_rating}
    update_seller_rating_result = invoke_http(
        f"{USER_SERVICE_URL}/user/{reporteduserid}/rating",
        method="PUT",
        json=update_seller_rating_payload
    )
    
    
    
    
    
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
        "reporter": {
            "id": currentuserid,
            "phone": user_phone
        },
        "reported": {
            "id": reporteduserid,
        },
    }
    
    # Step 7: Send notifications via AMQP
    amqp_lib.publish_message(
        routing_key="user.reported.notification",
        message=notification_payload,
        exchange_name=RABBITMQ_EXCHANGE,
        hostname=RABBITMQ_HOST
    )
    
    
    # Return success response with combined data
    return jsonify({
        "code": 200,
        "message": "User reported successfully",
        "data": {
            "reported_user": reporteduserid,
            "reporter_user": currentuserid,
            "deal_id": dealid,
            "report_status": chatgpt_data,
            "report_reason": reason,
            "notifications": {
                "amqp_sent": True
            }
        }
    })


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": report user composite service ...")
    app.run(host='0.0.0.0', port=5300, debug=True)
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
DEAL_SERVICE_URL = "http://localhost:5020"
PRODUCT_SERVICE_URL = "http://localhost:5005"
USER_SERVICE_URL = "http://localhost:5001"
PAYMENT_SERVICE_URL = "http://localhost:5031"

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')

# AMQP Configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_EXCHANGE = os.environ.get('RABBITMQ_EXCHANGE', 'deal_events')

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

@app.route("/verify_deal/<string:dealid>", methods=['POST'])
def verify_deal(dealid):
    """
    Confirm a deal by orchestrating the entire deal confirmation flow
    """
    # Step 1: Get deal information
    deal_result = invoke_http(f"{DEAL_SERVICE_URL}/deal/{dealid}", method="GET")
    
    if deal_result["code"] != 200:
        return jsonify({
            "code": 404,
            "message": f"Deal {dealid} not found."
        }), 404
    
    deal_data = deal_result["data"]["deal"]
    
    # Step 2: Get product details
    product_result = invoke_http(f"{PRODUCT_SERVICE_URL}/products/{deal_data['productid']}", method="GET")
    
    if product_result["code"] != 200:
        return jsonify({
            "code": 404,
            "message": f"Product {deal_data['productid']} not found."
        }), 404
    
    product_data = product_result["data"]["product"]
    
    # Step 3: Get buyer information
    seller_result = invoke_http(f"{USER_SERVICE_URL}/user/{deal_data['sellerid']}", method="GET")
    
    if seller_result["code"] != 200:
        return jsonify({
            "code": 404,
            "message": f"Buyer {deal_data['sellerid']} not found."
        }), 404
    
    seller_data = seller_result["data"]["user"]
    
    # Get buyer account number
    seller_account_result = invoke_http(
        f"{USER_SERVICE_URL}/user/getAccNumFromUser/{deal_data['sellerid']}", 
        method="GET"
    )
    
    if seller_account_result["code"] != 200:
        return jsonify({
            "code": 404,
            "message": f"Buyer account information not found."
        }), 404
    
    seller_account = seller_account_result["data"]["AccNum"]
    
    # Get buyer phone number (assuming you've added the endpoint in user.py)
    buyer_phone_result = invoke_http(
        f"{USER_SERVICE_URL}/user/getPhoneFromUser/{deal_data['sellerid']}", 
        method="GET"
    )
    
    buyer_phone = None
    if buyer_phone_result["code"] == 200:
        buyer_phone = buyer_phone_result["data"]["phone"]
    
    # Get seller information
    seller_result = invoke_http(f"{USER_SERVICE_URL}/user/{deal_data['sellerid']}", method="GET")
    
    seller_data = None
    seller_phone = None
    if seller_result["code"] == 200:
        seller_data = seller_result["data"]["user"]
        
        # Get seller phone
        seller_phone_result = invoke_http(
            f"{USER_SERVICE_URL}/user/getPhoneFromUser/{deal_data['sellerid']}", 
            method="GET"
        )
        
        if seller_phone_result["code"] == 200:
            seller_phone = seller_phone_result["data"]["phone"]
    
    # Step 4: Process payment (escrow)
    payment_payload = {
        "accnum": seller_account,
        "amount": product_data["price"]
    }
    
    payment_result = invoke_http(
        f"{PAYMENT_SERVICE_URL}/payment/release",
        method="POST",
        json=payment_payload
    )
    
    if payment_result["code"] != 200:
        return jsonify({
            "code": payment_result["code"],
            "message": f"Payment failed: {payment_result['message']}"
        }), payment_result["code"]
    
    # Step 5: Update deal status to confirmed (assuming status code 2 = confirmed)
    update_deal_payload = {
        "status": 2  # Confirmed status
    }
    
    update_deal_result = invoke_http(
        f"{DEAL_SERVICE_URL}/deal/{dealid}/status",
        method="PUT",
        json=update_deal_payload
    )
    
    if update_deal_result["code"] != 200:
        # Payment was successful but deal status update failed
        # We should implement compensating transaction here (refund)
        return jsonify({
            "code": 500,
            "message": f"Deal status update failed: {update_deal_result['message']}",
            "payment_result": payment_result
        }), 500
    
    # Step 6: Create notification payload with all relevant information
    notification_payload = {
        "event_type": "deal_confirmed",
        "timestamp": datetime.now().isoformat(),
        "deal_id": dealid,
        "product": {
            "id": product_data["productid"],
            "title": product_data["title"],
            "price": product_data["price"]
        },
        "buyer": {
            "id": seller_data["uid"],
            "name": seller_data["name"],
            "phone": buyer_phone
        },
        "seller": {
            "id": deal_data["sellerid"],
            "phone": seller_phone
        },
        "payment": {
            "transaction_id": payment_result.get("transaction", {}).get("transaction_id", ""),
            "amount": product_data["price"],
            "status": "escrow"
        }
    }
    
    # Step 7: Send notifications via AMQP
    amqp_lib.publish_message(
        routing_key="deal.confirmed",
        message=notification_payload,
        exchange_name=RABBITMQ_EXCHANGE,
        hostname=RABBITMQ_HOST
    )
    
    # Step 8: Send SMS notifications
    sms_results = {}
    if buyer_phone:
        buyer_message = f"Your reservation of {product_data['title']} for ${product_data['price']} has been confirmed. Deal ID: {dealid}"
        sms_results["buyer_sms"] = send_sms(buyer_phone, buyer_message)
    
    if seller_phone:
        seller_message = f"Your product {product_data['title']} has been reserved for ${product_data['price']}. Deal ID: {dealid}"
        sms_results["seller_sms"] = send_sms(seller_phone, seller_message)
    
    # Return success response with combined data
    return jsonify({
        "code": 200,
        "message": "Deal confirmed successfully",
        "data": {
            "deal": update_deal_result["data"],
            "product": product_data,
            "payment": payment_result["transaction"],
            "notifications": {
                "amqp_sent": True,
                "sms_results": sms_results
            }
        }
    })


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": confirm deal composite service ...")
    app.run(host='0.0.0.0', port=5200, debug=True)
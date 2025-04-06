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
    'title': 'Deal Verification API',
    'version': "1.0",
    'openapi': "3.0.2",
    'description': 'API for verifying deals, processing payments, and updating ratings',
    'specs': [
        {
            'endpoint': 'VerifyDealAPI',
            'route': '/VerifyDealAPI.json',
            'rule_filter': lambda rule: True,  # all in
            'model_filter': lambda tag: True,  # all in
        }
    ],
    'specs_route': "/apidocs/"
}
swagger = Swagger(app)

# Define microservice URLs
DEAL_SERVICE_URL = "http://deal:5020"
PRODUCT_SERVICE_URL = "http://product:5005"
USER_SERVICE_URL = "http://user:5001"
PAYMENT_SERVICE_URL = "http://payment:5031"
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
        "success" : True,
        "message_id" : 000
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

@app.route("/verify_deal/<string:dealid>", methods=['POST'])
def verify_deal(dealid):
    """
    Verify a deal by processing payment, updating ratings, and changing deal status
    ---
    tags:
      - Deal Verification
    parameters:
      - in: path
        name: dealid
        required: true
        schema:
          type: string
        description: ID of the deal to verify
    requestBody:
      description: Rating information
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - rating
            properties:
              rating:
                type: integer
                description: Rating score given by the buyer to the seller
                minimum: 1
                maximum: 5
            example:
              rating: 5
    responses:
      200:
        description: Deal verified successfully
      404:
        description: Deal, product, or user not found
      500:
        description: Server error, payment failure, or deal status update failed
    """
    rating = request.json['rating']
    # Step 1: Get deal information
    deal_result = invoke_http(f"{DEAL_SERVICE_URL}/deal/{dealid}", method="GET")
    if deal_result["code"] != 200:return jsonify({"code": 404,"message": f"Deal {dealid} not found."}), 404
    deal_data = deal_result["data"]["deal"]
    
    # Step 2: Get product details
    product_result = invoke_http(f"{PRODUCT_SERVICE_URL}/products/{deal_data['productid']}", method="GET")
    if product_result["code"] != 200:return jsonify({"code": 404,"message": f"Product {deal_data['productid']} not found."}), 404
    product_data = product_result["data"]["product"]
    
    # Step 3: Get seller information
    user_result = invoke_http(f"{USER_SERVICE_URL}/user/{deal_data["sellerid"]}", method="GET")
    if user_result["code"] != 200:return jsonify({"code": 404,"message": f"Buyer {deal_data["sellerid"]} not found."}), 404
    user_data = user_result["data"]["user"]

    # Step 4: Get seller account number
    user_account_result = invoke_http(f"{USER_SERVICE_URL}/user/getAccNumFromUser/{deal_data["sellerid"]}", method="GET")
    if user_account_result["code"] != 200:return jsonify({"code": 404,"message": f"Buyer account information not found."}), 404
    user_account = user_account_result["data"]["AccNum"]

    # Step 5: Get seller phone number
    user_phone_result = invoke_http(f"{USER_SERVICE_URL}/user/getPhoneFromUser/{deal_data["sellerid"]}", method="GET")
    user_phone = None
    if user_phone_result["code"] == 200:
        user_phone = user_phone_result["data"]["phone"]

    # Step 6: Process payment (release)
    payment_payload = {
        "accnum": user_account,
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
    
    payment_result_string = payment_result["transaction"]
    # Step 7: Post rating to the rating service
    rating_post_payload = {
        "CreatedAt": datetime.now().isoformat(),
        "RaterID": deal_data["buyerid"],
        "RatedID": deal_data["sellerid"],
        "DealID": dealid,
        "RatingScore": rating,
        "RatingType": "verify"
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
    # Step 8: Get all ratings for the seller
    rating_get_result = invoke_http(
        f"{RATING_SERVICE_GET_URL}{deal_data["sellerid"]}",
        method="GET"
    )
    if rating_get_result["Result"]["Success"] != True:
        return jsonify({
            "code": 404,
            "message": f"Rating failed: {rating_get_result['ErrorMessage']}"
        }), 404
   
    # Step 9: Create notification payload with all relevant information
    notification_payload = {
        "event_type": "deal_verified",
        "timestamp": datetime.now().isoformat(),
        "deal_id": dealid,
        "rating" : rating_post_payload,
        "product": {
            "id": product_data["productid"],
            "title": product_data["title"],
            "price": product_data["price"]
        },
        "buyer": {
            "id": user_data["uid"],
            "name": user_data["name"],
            "rating": user_data["rating"],
            "phone": user_phone
        },
        "payment": {
            "transaction_id": payment_result.get("transaction", {}).get("transaction_id", ""),
            "amount": product_data["price"],
            "status": "release"
        }
    }
    
    # Step 10: Send notifications via AMQP
    amqp_lib.publish_message(
        routing_key="deal.verified.notification",
        message=notification_payload,
        exchange_name=RABBITMQ_EXCHANGE,
        hostname=RABBITMQ_HOST
    )
    
    # Step 11: Send SMS notifications
    sms_results = {}
    if user_phone:
        buyer_message = f"Your purchase/sale of {product_data['title']} for ${product_data['price']} has been verified. Deal ID: {dealid}"
        sms_results["buyer_sms"] = send_sms(user_phone, buyer_message)


    # Calculate average rating
    ratings = rating_get_result["Rating"]
    total_score = sum(rating["RatingScore"] for rating in ratings)
    average_rating = total_score / len(ratings) if ratings else 0
    # Step 12: Update seller rating
    update_seller_rating_payload = {"rating": average_rating}
    update_seller_rating_result = invoke_http(
        f"{USER_SERVICE_URL}/user/{deal_data["sellerid"]}/rating",
        method="PUT",
        json=update_seller_rating_payload
    )
    # Step 13: Update deal status to verified
    update_deal_payload = {}
    if (deal_data['status'] == 3):
        update_deal_payload = {"status": 4}
    update_deal_result = invoke_http(
        f"{DEAL_SERVICE_URL}/deal/{dealid}/status",
        method="PUT",
        json=update_deal_payload
    )
    
    
    # Step 14: Mark all other deals of the same product as closed (-2)
    all_deals_result = invoke_http(f"{DEAL_SERVICE_URL}/deal/get_deal_with_product/{deal_data['productid']}", method="GET")
    if all_deals_result["code"] == 200:
        for other_deal in all_deals_result["data"]:
            if other_deal["dealid"] != dealid and other_deal["status"] != -2 and other_deal["status"] < 4:
                close_payload = {"status": -2}
                invoke_http(
                    f"{DEAL_SERVICE_URL}/deal/{other_deal['dealid']}/status",
                    method="PUT",
                    json=close_payload
                )


    if update_deal_result["code"] != 200:
        # Payment was successful but deal status update failed
        # We should implement compensating transaction here (refund)
        return jsonify({
            "code": 500,
            "message": f"Deal status update failed: {update_deal_result['message']}"
        }), 500
    # Return success response with combined data
    return jsonify({
        "code": 200,
        "message": "Deal verified successfully",
        "data": {
            "deal": update_deal_result["data"],
            "product": product_data,
            "ratingPayload": rating_post_payload,
            "finalUserRating" : user_data['rating'],
            "payment": payment_result_string,
            "notifications": {
                "amqp_sent": True,
                "sms_results": sms_results
            }
        }
    })
    
if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": confirm deal composite service ...")
    app.run(host='0.0.0.0', port=5200, debug=True)
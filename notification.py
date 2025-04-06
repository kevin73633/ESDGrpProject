#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import boto3
import pika
import time
import amqp_lib
from flasgger import Swagger 

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Add Swagger configuration
app.config['SWAGGER'] = {
    'title': 'Notification Service API',
    'version': "1.0",
    'openapi': "3.0.2",
    'description': 'Notification service for processing and distributing event messages',
    'specs': [
        {
            'endpoint': 'NotificationAPI',
            'route': '/NotificationAPI.json',
            'rule_filter': lambda rule: True,  # all in
            'model_filter': lambda tag: True,  # all in
        }
    ],
    'specs_route': "/apidocs/"
}
swagger = Swagger(app)

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-southeast-1')

# AMQP Configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_EXCHANGE = os.environ.get('RABBITMQ_EXCHANGE', 'deal_events')
RABBITMQ_QUEUE1 = 'deal_confirmation_queue'
RABBITMQ_QUEUE2 = 'deal_verification_queue'
RABBITMQ_QUEUE3 = 'user_report_queue'


def send_sms(phone_number, message):
    """
    Send SMS to any phone number using Amazon SNS
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
                    'StringValue': 'DEALSVC'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        
        print(f"SMS sent to {phone_number}, MessageId: {response.get('MessageId')}")
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

def process_notification(ch, method, properties, body):
    """
    Process notifications from AMQP
    """
    try:
        # Parse the message body
        notification = json.loads(body)
        print(f"Received notification: {method.routing_key}")
        
        event_type = notification.get('event_type')
        
        # Handle different event types
        if event_type == 'deal_confirmed':
            # Deal confirmation notification
            buyer_phone = notification.get('buyer', {}).get('phone')
            product_title = notification.get('product', {}).get('title')
            product_price = notification.get('product', {}).get('price')
            deal_id = notification.get('deal_id')
            
            if buyer_phone:
                message = f"Your purchase of {product_title} for ${product_price} has been confirmed. Deal ID: {deal_id}"
                send_sms(buyer_phone, message)
                
            # Also notify seller
            seller_phone = notification.get('seller', {}).get('phone')
            if seller_phone:
                message = f"Your product {product_title} has been reserved for ${product_price}. Deal ID: {deal_id}"
                send_sms(seller_phone, message)
        elif event_type == 'deal_verified':
            # Deal confirmation notification
            buyer_phone = notification.get('buyer', {}).get('phone')
            product_title = notification.get('product', {}).get('title')
            product_price = notification.get('product', {}).get('price')
            deal_id = notification.get('deal_id')
            
            if buyer_phone:
                message = f"Your purchase/sale of {product_title} for ${product_price} has been verified. Deal ID: {deal_id}"
                send_sms(buyer_phone, message)
        elif event_type == 'user_reported':
            # Deal confirmation notification
            reporter_phone = notification.get('reporter', {}).get('phone')
            reporteduserid = notification.get('reported', {}).get('id')
            deal_id = notification.get('deal_id')
            
            if reporter_phone:
                message = f"Your report against user {reporteduserid} has been received. Deal ID: {deal_id}"
                send_sms(reporter_phone, message)
                
        # Log the notification
        print(f"Processed {event_type} notification")
        
    except Exception as e:
        print(f"Error processing notification: {str(e)}")

@app.route("/health", methods=['GET'])
def health_check():
    # """Health check endpoint"""
    """
    Health check endpoint
    ---
    tags:
      - Service Health
    summary: Check if the notification service is running
    description: Simple endpoint to verify the notification service is operational
    responses:
      200:
        description: Service is healthy
       
    """
    return jsonify({"status": "healthy"}), 200

def start_consumer():
    """Start consuming messages from the notification queue"""
    print(f"Starting notification consumer on queue {RABBITMQ_QUEUE1}...")
    amqp_lib.start_consuming(
        hostname=RABBITMQ_HOST,
        exchange_name=RABBITMQ_EXCHANGE,
        exchange_type="topic",
        queue_name=RABBITMQ_QUEUE1,
        callback=process_notification
    )
    print(f"Starting notification consumer on queue {RABBITMQ_QUEUE2}...")
    amqp_lib.start_consuming(
        hostname=RABBITMQ_HOST,
        exchange_name=RABBITMQ_EXCHANGE,
        exchange_type="topic",
        queue_name=RABBITMQ_QUEUE2,
        callback=process_notification
    )
    print(f"Starting notification consumer on queue {RABBITMQ_QUEUE3}...")
    amqp_lib.start_consuming(
        hostname=RABBITMQ_HOST,
        exchange_name=RABBITMQ_EXCHANGE,
        exchange_type="topic",
        queue_name=RABBITMQ_QUEUE3,
        callback=process_notification
    )

if __name__ == '__main__':
    # Start the notification consumer in a separate thread
    import threading
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    print("This is flask for " + os.path.basename(__file__) + ": notification service ...")
    app.run(host='0.0.0.0', port=5075, debug=True)
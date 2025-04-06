from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from invokes import invoke_http
import os
from os import environ
from flasgger import Swagger

app = Flask(__name__)

CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Add Swagger configuration
app.config['SWAGGER'] = {
    'title': 'Payment Service API',
    'version': "1.0",
    'openapi': "3.0.2",
    'description': 'API for processing escrow payments, releases, and refunds',
    'specs': [
        {
            'endpoint': 'PaymentAPI',
            'route': '/PaymentAPI.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'specs_route': "/apidocs/"
}
swagger = Swagger(app)

# Define microservice URLs 
ACCOUNT_SERVICE_URL = "http://account:5030"
PAYMENT_RECORD_SERVICE_URL = "http://paymentrecord:5032"

# Define the escrow account number as a constant
ESCROW_ACCOUNT = '0000000000000001'


@app.route("/payment/escrow", methods=['POST'])
def process_escrow_payment():
    # """
    # Process buyer escrow payment (Scenario 1)
    
    # Expected request body:
    # {
    #     "accnum": "1234123412341234",
    #     "amount": 100
    # }
    # """
    """
    Process buyer escrow payment
    ---
    tags:
      - Payment Operations
    summary: Transfer funds from buyer to escrow account
    description: Processes payment from a buyer's account to the escrow account
    requestBody:
      description: Buyer payment details
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - accnum
              - amount
            properties:
              accnum:
                type: string
                description: Account number of the buyer
              amount:
                type: number
                description: Payment amount
            example:
              accnum: "1234123412341234"
              amount: 100
    responses:
      200:
        description: Payment processed and recorded successfully
      400:
        description: Invalid request - missing required fields
      500:
        description: Server error
    """
    data = request.get_json()
    
    if not data:
        return jsonify(
            {
                "code": 400,
                "message": "Invalid JSON input: missing body"
            }
        ), 400
        
    # Check if required fields are in the request body
    required_fields = ['accnum', 'amount']
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "code": 400,
                    "message": f"Invalid JSON input: missing '{field}'"
                }
            ), 400
    
    # Step 1: Call Account microservice to transfer funds
    account_payload = {
        "accnum": data['accnum'],
        "amount": data['amount']
    }
    
    # Make request to account service for escrow using invoke_http
    account_result = invoke_http(
        f"{ACCOUNT_SERVICE_URL}/account/escrow", 
        method="POST",
        json=account_payload
    )
    
    # Check if the account operation was successful
    if account_result["code"] != 200:
        return jsonify(account_result), account_result["code"]
    
    # Step 2: Create payment record using the account response
    payment_record_payload = {
        "accnum_from": account_result.get("accnum_from"),
        "accnum_to": account_result.get("accnum_to"),
        "status": account_result.get("status"),
        "txnamt": account_result.get("amount")
    }
    
    # Make request to payment record service using invoke_http
    payment_record_result = invoke_http(
        f"{PAYMENT_RECORD_SERVICE_URL}/paymentrecord/create",
        method="POST",
        json=payment_record_payload
    )
    
    # Return the combined response
    return jsonify(
        {
            "code": 200,
            "message": "Payment processed and recorded successfully",
            "transaction": account_result,
            "payment_record": payment_record_result.get("data")
        }
    )


@app.route("/payment/release", methods=['POST'])
def process_release_payment():
    # """
    # Process release of funds from escrow to seller (Scenario 2)
    
    # Expected request body:
    # {
    #     "accnum": "5234123412341234",
    #     "amount": 100
    # }
    # """
    """
    Release funds from escrow to seller
    ---
    tags:
      - Payment Operations
    summary: Transfer funds from escrow to seller
    description: Releases funds from the escrow account to the seller's account
    requestBody:
      description: Seller account details
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - accnum
              - amount
            properties:
              accnum:
                type: string
                description: Account number of the seller
              amount:
                type: number
                description: Amount to release
            example:
              accnum: "5234123412341234"
              amount: 100
    responses:
      200:
        description: Payment released and recorded successfully
      400:
        description: Invalid request - missing required fields
      500:
        description: Server error
    """
    data = request.get_json()
    
    if not data:
        return jsonify(
            {
                "code": 400,
                "message": "Invalid JSON input: missing body"
            }
        ), 400
        
    # Check if required fields are in the request body
    required_fields = ['accnum', 'amount']
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "code": 400,
                    "message": f"Invalid JSON input: missing '{field}'"
                }
            ), 400
    
    # Step 1: Call Account microservice to release funds
    account_payload = {
        "accnum": data['accnum'],
        "amount": data['amount']
    }
    
    # Make request to account service for fund release using invoke_http
    account_result = invoke_http(
        f"{ACCOUNT_SERVICE_URL}/account/release", 
        method="POST",
        json=account_payload
    )
    
    # Check if the account operation was successful
    if account_result["code"] != 200:
        return jsonify(account_result), account_result["code"]
    
    # Step 2: Create payment record using the account response
    payment_record_payload = {
        "accnum_from": account_result.get("accnum_from"),
        "accnum_to": account_result.get("accnum_to"),
        "status": account_result.get("status"),
        "txnamt": account_result.get("amount")
    }
    
    # Make request to payment record service using invoke_http
    payment_record_result = invoke_http(
        f"{PAYMENT_RECORD_SERVICE_URL}/paymentrecord/create",
        method="POST",
        json=payment_record_payload
    )
    
    # Return the combined response
    return jsonify(
        {
            "code": 200,
            "message": "Payment released and recorded successfully",
            "transaction": account_result,
            "payment_record": payment_record_result.get("data")
        }
    )


@app.route("/payment/refund", methods=['POST'])
def process_refund_payment():
    # """
    # Process refund of funds from escrow back to buyer (Scenario 3)
    
    # Expected request body:
    # {
    #     "accnum": "1234123412341234",
    #     "amount": 100
    # }
    # """
    """
    Refund funds from escrow to buyer
    ---
    tags:
      - Payment Operations
    summary: Transfer funds from escrow back to buyer
    description: Refunds funds from the escrow account back to the buyer's account
    requestBody:
      description: Buyer account details for refund
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - accnum
              - amount
            properties:
              accnum:
                type: string
                description: Account number of the buyer
              amount:
                type: number
                description: Amount to refund
            example:
              accnum: "1234123412341234"
              amount: 100
    responses:
      200:
        description: Payment refunded and recorded successfully
      400:
        description: Invalid request - missing required fields
      500:
        description: Server error
    """
    data = request.get_json()
    
    if not data:
        return jsonify(
            {
                "code": 400,
                "message": "Invalid JSON input: missing body"
            }
        ), 400
        
    # Check if required fields are in the request body
    required_fields = ['accnum', 'amount']
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "code": 400,
                    "message": f"Invalid JSON input: missing '{field}'"
                }
            ), 400
    
    # Step 1: Call Account microservice to refund funds
    account_payload = {
        "accnum": data['accnum'],
        "amount": data['amount']
    }
    
    # Make request to account service for fund refund using invoke_http
    account_result = invoke_http(
        f"{ACCOUNT_SERVICE_URL}/account/release", 
        method="POST",
        json=account_payload
    )
    
    # Check if the account operation was successful
    if account_result["code"] != 200:
        return jsonify(account_result), account_result["code"]
    
    # Step 2: Create payment record using the account response
    payment_record_payload = {
        "accnum_from": account_result.get("accnum_from"),
        "accnum_to": account_result.get("accnum_to"),
        "status": account_result.get("status"),
        "txnamt": account_result.get("amount")
    }
    
    # Make request to payment record service using invoke_http
    payment_record_result = invoke_http(
        f"{PAYMENT_RECORD_SERVICE_URL}/paymentrecord/create",
        method="POST",
        json=payment_record_payload
    )
    
    # Return the combined response
    return jsonify(
        {
            "code": 200,
            "message": "Payment refunded and recorded successfully",
            "transaction": account_result,
            "payment_record": payment_record_result.get("data")
        }
    )

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": payment composite service ...")
    app.run(host='0.0.0.0', port=5031, debug=True)
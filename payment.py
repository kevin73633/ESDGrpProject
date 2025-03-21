from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from invokes import invoke_http
import os
from os import environ

app = Flask(__name__)

CORS(app)

# Define microservice URLs 
ACCOUNT_SERVICE_URL = "http://localhost:5001"
PAYMENT_RECORD_SERVICE_URL = "http://localhost:5002"

# Define the escrow account number as a constant
ESCROW_ACCOUNT = '0000000000000001'


@app.route("/payment/escrow", methods=['POST'])
def process_escrow_payment():
    """
    Process buyer escrow payment (Scenario 1)
    
    Expected request body:
    {
        "accnum": "1234123412341234",
        "amount": 100
    }
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
    """
    Process release of funds from escrow to seller (Scenario 2)
    
    Expected request body:
    {
        "accnum": "5234123412341234",
        "amount": 100
    }
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

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": payment composite service ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
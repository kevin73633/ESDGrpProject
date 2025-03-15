#!/usr/bin/env python3
#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/Project"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Account(db.Model):
    __tablename__ = 'account'

    accnum = db.Column(db.String(255), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)

    def json(self):
        dto = {
            'accnum': self.accnum,
            'amount': self.amount,
        }

        # dto['order_item'] = []
        # for oi in self.order_item:
        #     dto['order_item'].append(oi.json())

        return dto

ESCROW_ACCOUNT = '0000000000000001'

@app.route("/account", methods=['GET'])
def get_all():
    acclist = db.session.scalars(db.select(Account)).all()
    print(acclist)
    if len(acclist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "accounts": [account.json() for account in acclist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no accounts."
        }
    ), 404

@app.route("/account/<string:accnum>", methods=['GET'])
def get_single_accnum(accnum):
    account = db.session.scalar(db.select(Account).filter_by(accnum=accnum))
    
    if account:
        return jsonify(
            {
                "code": 200,
                "data": account.json()  
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": f"Account '{accnum}' does not exist."
        }
    ), 404

@app.route("/account/escrow", methods=['POST'])
def escrow_funds():
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
    
    buyer_accnum = data['accnum']
    amount = data['amount']
    
    # Validate amount
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify(
            {
                "code": 400,
                "message": "Amount must be a positive number"
            }
        ), 400
    
    # Begin transaction
    try:
        # Get buyer account
        buyer_account = db.session.query(Account).filter_by(accnum=buyer_accnum).with_for_update().first()
        if not buyer_account:
            return jsonify(
                {
                    "code": 404,
                    "message": f"Buyer account '{buyer_accnum}' not found."
                }
            ), 404
        
        # Get escrow account
        escrow_account = db.session.query(Account).filter_by(accnum=ESCROW_ACCOUNT).with_for_update().first()
        if not escrow_account:
            return jsonify(
                {
                    "code": 404,
                    "message": f"Escrow account '{ESCROW_ACCOUNT}' not found."
                }
            ), 404
        
        # Check if buyer has sufficient funds
        if buyer_account.amount < amount:
            return jsonify(
                {
                    "code": 400,
                    "message": "Insufficient funds in buyer account",
                    "accnum_from": buyer_accnum,
                    "accnum_to": ESCROW_ACCOUNT,
                    "status": "unsuccessful"
                }
            ), 400
        
        # Update balances
        buyer_account.amount -= amount
        escrow_account.amount += amount
        
        # Commit the transaction
        db.session.commit()
        
        # Return success response
        return jsonify(
            {
                "code": 200,
                "message": "Funds successfully transferred to escrow",
                "accnum_from": buyer_accnum,
                "accnum_to": ESCROW_ACCOUNT,
                "amount": amount,
                "status": "successful"
            }
        )
        
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred: {str(e)}",
                "accnum_from": buyer_accnum,
                "accnum_to": ESCROW_ACCOUNT,
                "status": "unsuccessful"
            }
        ), 500
    
@app.route("/account/release", methods=['POST'])
def release_funds():
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
    
    seller_accnum = data['accnum']
    amount = data['amount']
    
    # Validate amount
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify(
            {
                "code": 400,
                "message": "Amount must be a positive number"
            }
        ), 400
    
    # Begin transaction
    try:
        # Get escrow account
        escrow_account = db.session.query(Account).filter_by(accnum=ESCROW_ACCOUNT).with_for_update().first()
        if not escrow_account:
            return jsonify(
                {
                    "code": 404,
                    "message": f"Escrow account '{ESCROW_ACCOUNT}' not found."
                }
            ), 404
        
        # Get seller account
        seller_account = db.session.query(Account).filter_by(accnum=seller_accnum).with_for_update().first()
        if not seller_account:
            return jsonify(
                {
                    "code": 404,
                    "message": f"Seller account '{seller_accnum}' not found."
                }
            ), 404
        
        # Check if escrow has sufficient funds
        if escrow_account.amount < amount:
            return jsonify(
                {
                    "code": 400,
                    "message": "Insufficient funds in escrow account",
                    "accnum_from": ESCROW_ACCOUNT,
                    "accnum_to": seller_accnum,
                    "status": "unsuccessful"
                }
            ), 400
        
        # Update balances
        escrow_account.amount -= amount
        seller_account.amount += amount
        
        # Commit the transaction
        db.session.commit()
        
        # Return success response
        return jsonify(
            {
                "code": 200,
                "message": "Funds successfully released from escrow",
                "accnum_from": ESCROW_ACCOUNT,
                "accnum_to": seller_accnum,
                "amount": amount,
                "status": "successful"
            }
        )
        
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred: {str(e)}",
                "accnum_from": ESCROW_ACCOUNT,
                "accnum_to": seller_accnum,
                "status": "unsuccessful"
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
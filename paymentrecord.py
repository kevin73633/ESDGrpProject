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


class PaymentRecord(db.Model):
    __tablename__ = 'paymentrecord'

    txnid = db.Column(db.String(64), primary_key=True)
    accnum_from = db.Column(db.String(255), nullable=False)
    accnum_to = db.Column(db.String(255), nullable=False)
    txnamt = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(64), nullable=False)

    def json(self):
        dto = {
            'txnid': self.txnid,
            'accnum_from': self.accnum_from,
            'accnum_to': self.accnum_to,
            'txnamt': self.txnamt,
            'status': self.status,
        }

        # dto['order_item'] = []
        # for oi in self.order_item:
        #     dto['order_item'].append(oi.json())

        return dto

@app.route("/paymentrecord", methods=['GET'])
def get_all():
    payreclist = db.session.scalars(db.select(PaymentRecord)).all()
    print(payreclist)
    if len(payreclist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "payment records": [paymentrecord.json() for paymentrecord in payreclist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no payment records."
        }
    ), 404

@app.route("/paymentrecord/<string:txnid>", methods=['GET'])
def find_by_txnid(txnid):
    """Get a specific payment record by transaction ID"""
    payment_record = db.session.query(PaymentRecord).filter_by(txnid=txnid).first()
    if payment_record:
        return jsonify(
            {
                "code": 200,
                "data": payment_record.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": f"Payment record with ID '{txnid}' not found."
        }
    ), 404

@app.route("/paymentrecord/create", methods=['POST'])
def create_payment_record():
    """
    Create a new payment record based on a completed transaction
    
    Expected request body:
    {
        "accnum_from": "1234123412341234",
        "accnum_to": "0000000000000001",
        "status": "successful",
        "txnamt": 100
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
    required_fields = ['accnum_from', 'accnum_to', 'status', 'txnamt']
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "code": 400,
                    "message": f"Invalid JSON input: missing '{field}'"
                }
            ), 400
    
    try:
        # Get the highest current txnid from the database
        highest_txn = db.session.query(PaymentRecord).order_by(PaymentRecord.txnid.desc()).first()
        
        if highest_txn:
            # If we have existing transactions, increment the highest ID
            last_id = int(highest_txn.txnid)
            new_txnid = str(last_id + 1)
        else:
            new_txnid = "1234"
    
    # Create the new payment record
        new_record = PaymentRecord(
            txnid=new_txnid,
            accnum_from=data['accnum_from'],
            accnum_to=data['accnum_to'],
            txnamt=data['txnamt'],
            status=data['status']
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify(
            {
                "code": 201,
                "message": "Payment record created successfully",
                "data": new_record.json()
            }
        ), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred creating the payment record: {str(e)}"
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
#!/usr/bin/env python3
#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

#!/usr/bin/env python3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

from sqlalchemy import or_
from flasgger import Swagger

app = Flask(__name__)

CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

app.config['SWAGGER'] = {
    'title': 'Deal API',
    'version': "1.0",
    'openapi': "3.0.2",
    'description': 'API for managing deals between buyers and sellers',
    'specs': [
        {
            'endpoint': 'DealAPI',
            'route': '/DealAPI.json',
            'rule_filter': lambda rule: True,  # all in
            'model_filter': lambda tag: True,  # all in
        }
    ],
    'specs_route': "/apidocs/"
}
swagger = Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://" + str(environ.get("DBLOGIN")) + "@localhost:3306/Project"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Deal(db.Model):
    __tablename__ = 'deal'

    dealid = db.Column(db.String(64), primary_key=True)
    buyerid = db.Column(db.String(64), nullable=False)
    sellerid = db.Column(db.String(64), nullable=False)
    productid = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def json(self):
        dto = {
            'dealid': self.dealid,
            'buyerid': self.buyerid,
            'sellerid': self.sellerid,
            'productid': self.productid,
            'status': self.status,
        }
        return dto


@app.route("/deal", methods=['GET'])
def get_all():
    """
    Get all deals
    ---
    tags:
      - Deals
    responses:
      200:
        description: Returns all deals
    
      404:
        description: No deals found
        
    """
    deallist = db.session.scalars(db.select(Deal)).all()
    print(deallist)
    if len(deallist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "deals": [deal.json() for deal in deallist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no deals."
        }
    ), 404
@app.route("/get_deals_with_user/<string:userid>", methods=['GET'])
def get_deals_with_user(userid):
    """
    Get all deals for a specific user
    ---
    tags:
      - Deals
    parameters:
      - in: path
        name: userid
        required: true
        schema:
          type: string
        description: ID of the user (as buyer or seller)
    responses:
      200:
        description: Returns all deals involving the specified user
        
      404:
        description: No deals found for the user
        
    """
    
    deallist = db.session.scalars(db.select(Deal).filter(or_(Deal.sellerid==userid, Deal.buyerid==userid))).all()
    print(deallist)
    if len(deallist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "deals": [deal.json() for deal in deallist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no deals."
        }
    ), 404
@app.route("/get_deal_with_product/<string:productid>", methods=['GET'])
def get_deal_with_product(productid):
    """
    Get deal for a specific product
    ---
    tags:
      - Deals
    parameters:
      - in: path
        name: productid
        required: true
        schema:
          type: string
        description: ID of the product
    responses:
      200:
        description: Returns the deal associated with the specified product
        
      404:
        description: No deal found for the product
        
    """
    deal = db.session.scalar(db.select(Deal).filter_by(productid=productid))
    if deal:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "deal": deal.json()
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no deal."
        }
    ), 404
@app.route("/deal/<string:dealid>", methods=['GET'])
def get_single_deal(dealid):
    """
    Get a specific deal by ID
    ---
    tags:
      - Deals
    parameters:
      - in: path
        name: dealid
        required: true
        schema:
          type: string
        description: ID of the deal to retrieve
    responses:
      200:
        description: Returns the specified deal
        
      404:
        description: Deal not found
        
    """
    deal = db.session.scalar(db.select(Deal).filter_by(dealid=dealid))
    if deal:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "deal": deal.json()
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no deal."
        }
    ), 404
#
# New endpoint to update deal status
# deal statuses
# -1 = reported deal, closed
# 0 = unconfirmed both sides
# 1 = confirmed and paid buyer side
# 2 = confirmed seller side
# 3 = confirmed both sides
# 4 = verified both sides, closed
@app.route("/deal/<string:dealid>/status", methods=['PUT'])
def update_deal_status(dealid):
    """
    Update deal status
    ---
    tags:
      - Deals
    parameters:
      - in: path
        name: dealid
        required: true
        schema:
          type: string
        description: ID of the deal to update
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
              - status
            properties:
              status:
                type: integer
                description: |
                  New status for the deal:
                  -1 = reported deal, closed
                  0 = unconfirmed both sides
                  1 = confirmed and paid buyer side
                  2 = confirmed seller side
                  3 = confirmed both sides
                  4 = verified both sides, closed
    responses:
      200:
        description: Deal status updated successfully
        
      400:
        description: Bad request - missing status
        
      404:
        description: Deal not found
        
      500:
        description: Server error
        
    """
    deal = db.session.scalar(db.select(Deal).filter_by(dealid=dealid))
    
    if not deal:
        return jsonify(
            {
                "code": 404,
                "message": "Deal not found."
            }
        ), 404
    
    data = request.get_json()
    if 'status' not in data:
        return jsonify(
            {
                "code": 400,
                "message": "Status is required."
            }
        ), 400
    
    try:
        old_status = deal.status
        deal.status = data['status']
        db.session.commit()
        
        return jsonify(
            {
                "code": 200,
                "data": deal.json(),
                "message": "Deal status updated successfully."
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred updating the deal status. {str(e)}"
            }
        ), 500

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": deals ...")
    app.run(host='0.0.0.0', port=5020, debug=True)
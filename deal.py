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

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/Project"
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
    
@app.route("/deal/<string:dealid>", methods=['GET'])
def get_single_deal(dealid):
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

# New endpoint to update deal status
@app.route("/deal/<string:dealid>/status", methods=['PUT'])
def update_deal_status(dealid):
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
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

        # dto['order_item'] = []
        # for oi in self.order_item:
        #     dto['order_item'].append(oi.json())

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

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": deals ...")
    app.run(host='0.0.0.0', port=5020, debug=True)

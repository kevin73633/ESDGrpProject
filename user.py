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


class User(db.Model):
    __tablename__ = 'user'

    uid = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    cardnum = db.Column(db.String(64), nullable=False)

    def json(self):
        dto = {
            'uid': self.uid,
            'name': self.name,
            'rating': self.rating,
            'cardnum': self.cardnum,
        }

        # dto['order_item'] = []
        # for oi in self.order_item:
        #     dto['order_item'].append(oi.json())

        return dto




@app.route("/user", methods=['GET'])
def get_all():
    userlist = db.session.scalars(db.select(User)).all()
    print(userlist)
    if len(userlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "users": [user.json() for user in userlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404


# @app.route("/order/<string:order_id>")
# def find_by_order_id(uid):
#     order = db.session.scalar(db.select(User).filter_by(order_id=order_id))
#     if order:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": order.json()
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#             "data": {
#                 "order_id": order_id
#             },
#             "message": "Order not found."
#         }
#     ), 404


# @app.route("/order", methods=['POST'])
# def create_order():
#     customer_id = request.json.get('customer_id', None)
#     order = User(customer_id=customer_id, status='NEW')

#     cart_item = request.json.get('cart_item')
#     for item in cart_item:
#         order.order_item.append(Order_Item(
#             book_id=item['book_id'], quantity=item['quantity']))

#     try:
#         db.session.add(order)
#         db.session.commit()
#     except Exception as e:
#         print("Error: {}".format(str(e)))
#         return jsonify(
#             {
#                 "code": 500,
#                 "message": "An error occurred while creating the order. " + str(e)
#             }
#         ), 500

#     return jsonify(
#         {
#             "code": 201,
#             "data": order.json()
#         }
#     ), 201


# @app.route("/order/<string:order_id>", methods=['PUT'])
# def update_order(order_id):
#     try:
#         order = db.session.scalar(db.select(Order).filter_by(order_id=order_id))
#         if not order:
#             return jsonify(
#                 {
#                     "code": 404,
#                     "data": {
#                         "order_id": order_id
#                     },
#                     "message": "Order not found."
#                 }
#             ), 404

#         # update status
#         data = request.get_json()
#         if data['status']:
#             order.status = data['status']
#             db.session.commit()
#             return jsonify(
#                 {
#                     "code": 200,
#                     "data": order.json()
#                 }
#             ), 200
#     except Exception as e:
#         print("Error: {}".format(str(e)))
#         return jsonify(
#             {
#                 "code": 500,
#                 "data": {
#                     "order_id": order_id
#                 },
#                 "message": "An error occurred while updating the order. " + str(e)
#             }
#         ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5001, debug=True)

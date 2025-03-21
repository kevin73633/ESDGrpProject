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


class Chat(db.Model):
    __tablename__ = 'chat'
    messageid = db.Column(db.String(64), primary_key=True)
    senderid = db.Column(db.String(64), nullable=False)
    receiverid = db.Column(db.String(64), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    sentat = db.Column(db.String(64), nullable=False)

    def json(self):
        dto = {
            'messageid': self.messageid,
            'senderid': self.senderid,
            'receiverid': self.receiverid,
            'message': self.message,
            'sentat': self.sentat,
        }

        # dto['order_item'] = []
        # for oi in self.order_item:
        #     dto['order_item'].append(oi.json())

        return dto




@app.route("/chat", methods=['GET'])
def get_all():
    messages = db.session.scalars(db.select(Chat)).all()
    print(messages)
    if len(messages):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "messages": [message.json() for message in messages]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no messages."
        }
    ), 404

@app.route("/chat/getmessagebetween/<string:senderid>/<string:receiverid>", methods=['GET'])
def getChatBetween(senderid, receiverid):
    messages = db.session.scalars(db.select(Chat).filter_by(senderid=senderid).filter_by(receiverid=receiverid).order_by(Chat.sentat))
    print(messages)
    if messages:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "messages": [message.json() for message in messages]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no messages."
        }
    ), 404

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": chats ...")
    app.run(host='0.0.0.0', port=5001, debug=True)

#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os
import uuid
from flasgger import Swagger

app = Flask(__name__)

app.config['SWAGGER'] = {
    'title': 'Chat API',
    'version': "1.0",
    'openapi': "3.0.2",
    'description': 'API for managing chat messages between users',
    'specs': [
        {
            'endpoint': 'ChatAPI',
            'route': '/ChatAPI.json',
            'rule_filter': lambda rule: True,  # all in
            'model_filter': lambda tag: True,  # all in
        }
    ],
    'specs_route': "/apidocs/"
}
swagger = Swagger(app)

CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://" + str(environ.get("DBLOGIN")) + "@localhost:3306/Project"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Chat(db.Model):
    __tablename__ = 'chat'
    messageid = db.Column(db.String(64), primary_key=True)
    senderid = db.Column(db.String(64), nullable=False)
    receiverid = db.Column(db.String(64), nullable=False)
    dealid = db.Column(db.String(64), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    sentat = db.Column(db.String(64), nullable=False)

    def json(self):
        dto = {
            'messageid': self.messageid,
            'senderid': self.senderid,
            'receiverid': self.receiverid,
            'dealid': self.dealid,
            'message': self.message,
            'sentat': self.sentat,
        }

        # dto['order_item'] = []
        # for oi in self.order_item:
        #     dto['order_item'].append(oi.json())

        return dto


@app.route("/chat", methods=['GET'])
def get_all():
    """
    Get all chat messages
    ---
    tags:
      - Chat
    responses:
      200:
        description: Returns all chat messages
        
      404:
        description: No messages found
    """
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

@app.route("/chat/getmessagebetween/<string:dealid>", methods=['GET'])
def getChatBetween(dealid):
    """
    Get all chat messages for a specific deal
    ---
    tags:
      - Chat
    parameters:
      - in: path
        name: dealid
        required: true
        schema:
          type: string
        description: ID of the deal to get messages for
    responses:
      200:
        description: Returns all messages for the specified deal
        
      404:
        description: No messages found for the deal
       
    """
    # Your existing implementation remains the same
    messages = db.session.scalars(db.select(Chat).filter_by(dealid=dealid).order_by(Chat.sentat))
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
    
@app.route("/chat/send", methods=['POST'])
def send_message():
    """
    Send a new chat message
    ---
    tags:
      - Chat
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
              - senderid
              - receiverid
              - dealid
              - message
            properties:
              senderid:
                type: string
                description: ID of the user sending the message
              receiverid:
                type: string
                description: ID of the user receiving the message
              dealid:
                type: string
                description: ID of the deal associated with the chat
              message:
                type: string
                description: Content of the message
              sentat:
                type: string
                description: Timestamp when the message was sent (optional, defaults to current time)
    responses:
      201:
        description: Message sent successfully
        
      400:
        description: Missing required fields
        
      500:
        description: Server error
        
    """
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug: log received data
        
        # Check required fields
        required_fields = ['senderid', 'receiverid', 'message', 'dealid']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")  # Debug
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Generate a unique message ID
        message_id = str(uuid.uuid4())
        
        # Format the datetime properly for MySQL
        if 'sentat' in data:
            try:
                # Parse the ISO format with Z
                if data['sentat'].endswith('Z'):
                    dt = datetime.fromisoformat(data['sentat'].replace('Z', '+00:00'))
                else:
                    dt = datetime.fromisoformat(data['sentat'])
                # Format to MySQL compatible format
                sent_at = dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If parsing fails, use current time
                sent_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            # Get current timestamp if not provided
            sent_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Creating message with ID: {message_id}")  # Debug
        
        # Store message data in a dictionary before creating the database object
        message_data = {
            "messageid": message_id,
            "senderid": data['senderid'],
            "receiverid": data['receiverid'],
            "dealid": data['dealid'],
            "message": data['message'],
            "sentat": sent_at
        }
        
        # Create new message from the dictionary
        new_message = Chat(**message_data)
        
        # Save to database
        try:
            db.session.add(new_message)
            db.session.commit()
            print("Message saved successfully")  # Debug
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error: {str(db_error)}")  # Debug
            raise db_error
        
        # Return success response with the message data (not the SQLAlchemy object)
        return jsonify({
            "code": 201,
            "data": {
                "message": message_data
            },
            "message": "Message sent successfully."
        }), 201
        
    except Exception as e:
        # Log the error
        print(f"Error sending message: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace
        
        # Return error response
        return jsonify({
            "code": 500,
            "message": f"An error occurred while sending the message: {str(e)}"
        }), 500
              
if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": chats ...")
    app.run(host='0.0.0.0', port=5087, debug=True)
#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

CORS(app)

# Connect to the Project database
app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root:root@localhost:3306/Project"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# Get OpenAI API Key from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not found in environment variables or .env file")

db = SQLAlchemy(app)

# Define the ChatGPT moderation model
class ChatGPT(db.Model):
    __tablename__ = 'chatgpt'

    chatgpt_id = db.Column(db.String(64), primary_key=True)
    chat_id = db.Column(db.String(64), nullable=False)
    chat_content = db.Column(db.Text, nullable=False)
    buyer_id = db.Column(db.String(64), nullable=False)
    seller_id = db.Column(db.String(64), nullable=False)
    report_id = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(20), nullable=False)  # 'safe', 'unsafe', 'indeterminate'
    content_categories = db.Column(db.Text, nullable=True)  # JSON string
    severity_level = db.Column(db.String(10), nullable=True)  # 'low', 'medium', 'high'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    def json(self):
        return {
            'status': self.status
        }

def analyze_chat_with_openai(chat_content):
    """
    Analyze chat content using OpenAI API to detect inappropriate content.
    Returns a dict with analysis results.
    """
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    prompt = f"""
    Analyze the following chat content for inappropriate material. 
    Classify it as 'safe', 'unsafe', or 'indeterminate'.
    If it's 'unsafe' or 'indeterminate', identify the categories of concern 
    (e.g., hate_speech, harassment, sexual_content, violence, etc.) and provide a severity level (low, medium, high).
    
    Return your analysis as JSON with the following structure:
    {{
        "status": "safe/unsafe/indeterminate",
        "content_categories": ["category1", "category2"],
        "severity_level": "low/medium/high"
    }}
    
    Chat content to analyze: {chat_content}
    """
    
    data = {
        "model": "gpt-4",  # Use the appropriate model
        "messages": [
            {"role": "system", "content": "You are an AI content moderation assistant. Respond only with the requested JSON format."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"].strip()
        
        # Parse the JSON response
        try:
            analysis = json.loads(assistant_message)
            return analysis
        except json.JSONDecodeError:
            # Fallback if we don't get valid JSON
            return {
                "status": "indeterminate",
                "content_categories": ["parse_error"],
                "severity_level": "low"
            }
            
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return {
            "status": "indeterminate",
            "content_categories": ["api_error"],
            "severity_level": "low"
        }

def generate_chatgpt_id():
    """Generate a unique ChatGPT ID with a format like CGP00001"""
    # Get the highest ID number currently in the database
    highest_id = db.session.query(db.func.max(ChatGPT.chatgpt_id)).scalar()
    
    if not highest_id or not highest_id.startswith('CGP'):
        # No records yet, start with 00001
        return 'CGP00001'
    
    # Extract the numeric part
    try:
        num = int(highest_id[3:])
        # Increment and format to 5 digits
        return f'CGP{(num+1):05d}'
    except ValueError:
        # If there's an issue with the format, generate a timestamp-based ID
        return f'CGP{int(time.time())}'

@app.route("/chatgpt/report", methods=['POST'])
def report_chat():
    """
    Endpoint to analyze reported chat content for inappropriate material.
    This specifically handles when a buyer or seller reports a chat.
    """
    
    # Check if request contains the required data
    data = request.get_json()
    if not data:
        return jsonify({
            "code": 400,
            "message": "Invalid JSON data in request"
        }), 400
    
    # Extract required parameters
    chat_id = data.get('chat_id')
    chat_content = data.get('chat_content')
    buyer_id = data.get('buyer_id')
    seller_id = data.get('seller_id')
    report_id = data.get('report_id')
    
    # Validate required parameters
    if not all([chat_id, chat_content, buyer_id, seller_id]):
        return jsonify({
            "code": 400,
            "message": "Missing required parameters: chat_id, chat_content, buyer_id, seller_id"
        }), 400
    
    # Check if this chat has already been moderated
    existing_moderation = db.session.scalar(
        db.select(ChatGPT).filter_by(chat_id=chat_id)
    )
    
    if existing_moderation:
        return jsonify({
            "code": 200,
            "data": {
                "status": existing_moderation.status
            },
            "message": "This chat has already been analyzed"
        })
    
    # Analyze chat content with OpenAI
    analysis_result = analyze_chat_with_openai(chat_content)
    
    # Create a new moderation record
    chatgpt_id = generate_chatgpt_id()
    
    # Handle content categories as JSON string
    content_categories_json = None
    if 'content_categories' in analysis_result and analysis_result['content_categories']:
        content_categories_json = json.dumps(analysis_result['content_categories'])
    
    moderation = ChatGPT(
        chatgpt_id=chatgpt_id,
        chat_id=chat_id,
        chat_content=chat_content,
        buyer_id=buyer_id,
        seller_id=seller_id,
        report_id=report_id,
        status=analysis_result.get('status', 'indeterminate'),
        content_categories=content_categories_json,
        severity_level=analysis_result.get('severity_level')
    )
    
    try:
        db.session.add(moderation)
        db.session.commit()
        
        # Prepare response based on moderation result
        status = moderation.status
        response_message = "The chat content is appropriate."
        
        if status == 'unsafe':
            severity = moderation.severity_level or 'unknown'
            categories = []
            if moderation.content_categories:
                try:
                    categories = json.loads(moderation.content_categories)
                except:
                    categories = []
                    
            category_text = ", ".join(categories) if categories else "inappropriate content"
            response_message = f"The chat content contains {category_text} of {severity} severity."
            
        elif status == 'indeterminate':
            response_message = "The chat content could not be clearly classified."
        
        return jsonify({
            "code": 201,
            "data": {
                "status": status
            },
            "message": response_message
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"An error occurred while analyzing chat content: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": ChatGPT chat moderation service ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
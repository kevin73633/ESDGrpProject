#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

def analyze_with_openai(message):
    """
    Use OpenAI's GPT-4 model to analyze message content
    Returns True if harmful content is detected, False otherwise
    """
    try:
        print(f"Sending message to OpenAI: {message}")
        
        # Create a structured prompt with clear guidelines for content moderation
        # Modified to work without the response_format parameter
        response = client.chat.completions.create(
            model="gpt-4",  # Specifically using gpt-4
            messages=[
                {"role": "system", "content": "You are an advanced content moderation system. Your ONLY job is to determine if a message is inappropriate, harmful, or offensive. Return TRUE if the message falls into ANY of these categories:\n\n1) INSULTS: direct name-calling, personal attacks, or derogatory language (e.g., 'idiot', 'stupid', 'loser')\n2) THREATS: explicit or implied threats of violence, harm, or intimidation\n3) HATE SPEECH: content targeting identity characteristics like race, gender, religion, etc.\n4) HARASSMENT: bullying, intimidation, or repeated unwanted aggression\n5) SELF-HARM: content promoting, encouraging, or expressing intent to harm oneself\n6) SEXUAL CONTENT: explicit, unwanted, or inappropriate sexual content\n7) VIOLENT CONTENT: glorification or detailed descriptions of violence\n\nReturn FALSE only if the message is completely free of the above issues. Be especially careful with insults - even mild insults should be classified as inappropriate."},
                {"role": "user", "content": f"Message to moderate: \"{message}\"\n\nDetermine if this message is inappropriate, harmful, or offensive according to the guidelines. Respond with ONLY a JSON object in this exact format: {{\"is_harmful\": true}} or {{\"is_harmful\": false}}. Do not include any other text, explanation, or formatting."}
            ],
            temperature=0  # Use 0 temperature for consistent results
        )
        
        # Extract the response text
        result_text = response.choices[0].message.content
        print(f"OpenAI content response: {result_text}")
        
        # Parse JSON response - handle both JSON and plain text responses
        try:
            # First try to parse as JSON
            result_json = json.loads(result_text)
            is_harmful = result_json.get("is_harmful", False)
        except json.JSONDecodeError:
            # If not valid JSON, look for true/false in the text
            print("JSON parsing failed, falling back to text analysis")
            result_lower = result_text.lower()
            is_harmful = "true" in result_lower or "harmful: true" in result_lower
            
        print(f"Parsed is_harmful value: {is_harmful}")
        
        return is_harmful
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Log the full error for debugging
        import traceback
        traceback.print_exc()
        
        # For debugging purposes, return False to identify API errors separately
        # Change this back to True in production
        return False

@app.route("/analyze", methods=['POST'])
def analyze_message():
    """
    Endpoint to analyze chat message content using OpenAI
    Expects JSON with a 'message' field
    Returns JSON with 'is_harmful' boolean
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            "code": 400,
            "message": "Bad request. 'message' field is required."
        }), 400
    
    message = data['message']
    print(f"Analyzing message: {message}")
    
    # Use OpenAI API for analysis
    is_harmful = analyze_with_openai(message)
    print(f"Message analyzed by OpenAI API: {'harmful' if is_harmful else 'not harmful'}")
    
    return jsonify({
        "code": 200,
        "data": {
            "is_harmful": is_harmful
        }
    })

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": OpenAI-powered chat content analyzer ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
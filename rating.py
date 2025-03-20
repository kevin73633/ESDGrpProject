from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# OutSystems API Base URL
BASE_URL = "https://personal-nzmfqiqp.outsystemscloud.com/RatingAPI_REST/rest/v1"

# Endpoint URLs
GET_RATING_URL = f"{BASE_URL}/rating/"
UPDATE_USER_RATING_URL = f"{BASE_URL}/updateuserrating"
GET_USER_RATING_URL = f"{BASE_URL}/userRating/RatedID/"


@app.route("/rating", methods=["GET"])
def get_all_ratings():
    """Fetch all ratings from OutSystems API."""
    try:
        response = requests.get(GET_RATING_URL)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/updateuserrating", methods=["POST"])
def update_user_rating():
    """Send user rating data to OutSystems API."""
    try:
        data = request.json
        input_match_id = request.args.get("InputMatchID")
        if not input_match_id:
            return jsonify({"error": "InputMatchID query parameter is required"}), 400

        response = requests.post(
            f"{UPDATE_USER_RATING_URL}?InputMatchID={input_match_id}", json=data
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/userRating/<int:RatedID>", methods=["GET"])
def get_user_rating(RatedID):
    """Fetch ratings for a specific user from OutSystems API."""
    try:
        response = requests.get(f"{GET_USER_RATING_URL}?RatedID={RatedID}")
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)

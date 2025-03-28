from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import environ

app = Flask(__name__)
CORS(app,
     origins=["http://localhost:8080"],  # Your Vue.js frontend URL
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Change to MySQL connection with your specific credentials
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("dbURL") or "mysql+mysqlconnector://" + str(environ.get("DBLOGIN")) + "@localhost:3306/reportlog"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ReportLog Model
class ReportLog(db.Model):
    __tablename__ = 'ReportLog'

    ReportID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UserID = db.Column(db.Integer, nullable=False)
    ReportedUserID = db.Column(db.Integer, nullable=False)
    Reason = db.Column(db.String(225), nullable=False)
    Status = db.Column(db.String(50), nullable=False, default="Pending")

    def json(self):
        return {
            "ReportID": self.ReportID,
            "CreatedAt": self.CreatedAt.strftime("%Y-%m-%d %H:%M:%S"),
            "UserID": self.UserID,
            "ReportedUserID": self.ReportedUserID,
            "Reason": self.Reason,
            "Status": self.Status
        }

@app.route("/reportLog", methods=["POST"])
def create_report_log():
    """Create a new report log entry."""
    try:
        data = request.json
        new_report = ReportLog(
            UserID=data["UserID"],
            ReportedUserID=data["ReportedUserID"],
            Reason=data["Reason"],
            Status=data.get("Status", "Pending")
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({"code": 201, "message": "Report created successfully", "data": new_report.json()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": "An error occurred while creating the report", "error": str(e)}), 500

@app.route("/reportLog/<int:ReportID>", methods=["GET"])
def get_report_log(ReportID):
    """Retrieve a report log entry by ReportID."""
    try:
        report = db.session.get(ReportLog, ReportID)
        if report:
            return jsonify({"code": 200, "data": report.json()}), 200
        return jsonify({"code": 404, "message": "Report not found"}), 404
    except Exception as e:
        return jsonify({"code": 500, "message": "An error occurred while fetching the report", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
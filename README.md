
# README.md

## 📦 Deal Sharing Marketplace Platform
A peer-to-peer product deal sharing platform supporting secure escrow payments, dispute resolution, real-time messaging, and intelligent chat moderation.

---

## 🚀 Installation & Setup

### 📁 Prerequisites
Ensure the following are installed:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Node.js & npm](https://nodejs.org/) (for frontend)
- Python 3.9+ (if editing backend)

### 📥 Clone and Setup
1. Clone the repository (USE BRANCH NAMED "FINAL"):
   ```bash
   gh repo clone kevin73633/ESDGrpProject
   cd ESDGrpProject
   ```

2. Ensure [.env ZIP file](https://drive.google.com/uc?export=download&id=12C7zfxj35Ur3vrYaL2-EwXqTwY6sYxcN) is downloaded and extracted.  
   📌 **IMPORTANT:** The `.env` file is inside the ZIP archive — make sure it stays named `.env` after extraction!  
   🔐 **Note:** You must be logged into an SMU Google account to access the file.  
   > 💡 **Mac users**: use `DBLOGIN=root:root`  
   > 💡 **Windows users**: use `DBLOGIN=root`



   ```env
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=UTYN...
   AWS_REGION=ap-southeast-1
   RABBITMQ_HOST=localhost
   RABBITMQ_EXCHANGE=deal_events
   DBLOGIN=root:root
   OPENAI_API_KEY=sk-proj-...
   ```

3. Import the database schema into MySQL using:
   ```bash
   mysql -u root -p < proj.sql
   ```

4. 🚫 **Important:** Remove all other Docker containers before running (MAINLY kong and RabbitMQ, WONT WORK OTHERWISE!!!):
   ```bash
   docker compose up -d --build
   ```

5. Launch the frontend:
   ```bash
   cd frontend
   npm install
   npm run serve
   ```

6. Access the platform at:
   - [http://localhost:8080/login](http://localhost:8080/login)

### 🧪 Test Credentials
- **User 1 (Seller):**
  - Username: `12345678`
- **User 2 (Buyer):**
  - Username: `22345678`
- **User 3 (Seller):**
  - Username: `32345678`
- **User 4 (Buyer):**
  - Username: `42345678`


7. [Demo Youtube Link](https://youtu.be/BOxkQd_93y8) <- test the three user scenarios used in this video demo
---

## 🧠 Technologies Used

| Category       | Tech Stack                                 |
|----------------|---------------------------------------------|
| Frontend       | Vue.js 3, Bootstrap, Axios                  |
| Backend        | Python (Flask), MySQL                      |
| Microservices  | Docker, Flask REST APIs                    |
| Messaging      | RabbitMQ (AMQP), AWS SNS                   |
| Rating Engine  | OutSystems REST API                        |
| Moderation     | OpenAI ChatGPT API                         |
| Gateway        | Kong API Gateway                           |
| Documentation  | Swagger (OpenAPI Spec)                     |

---

## 📚 Key Features
- 🔐 Escrow payment system (Confirm Deal)
- ✅ Post-exchange fund release and rating (Verify Deal)
- 🚩 Intelligent chat moderation with reporting (Report User)
- 💬 Real-time AMQP messaging + SMS alerts
- 🧾 RESTful microservices (Chat, Product, Deal, Rating, etc.)

---

## 📄 API Documentation
You can explore the RESTful API documentation using Swagger UI, make sure up to Step 4 is completed!!!! :

🔗 View Swagger API Docs

^^ REPLACE temp with a port number below to view swagger api doc for that api ^^
[Account API](http://localhost:5030/apidocs)
[Chat API](http://localhost:5087/apidocs)
[ChatGPT API (Wrapper)](http://localhost:5002/apidocs)
[Deal API](http://localhost:5020/apidocs)
[Notification API](http://localhost:5075/apidocs)
[Paymentrecord API](http://localhost:5032/apidocs)
[Product API](http://localhost:5005/apidocs)
[Rating API (Built on OutSystems)](https://personal-nzmfqiqp.outsystemscloud.com/RatingAPI_REST/rest/v1/)
[Report Log API](http://localhost:5004/apidocs)
[User API](http://localhost:5001/apidocs)
[Confirm Deal API](http://localhost:5100/apidocs)
[Verify Deal API](http://localhost:5200/apidocs)
[Report User API](http://localhost:5300/apidocs)
[Payment API](http://localhost:5031/apidocs)

---

## 📅 Additional Notes
- ChatGPT moderation API: [OpenAI Docs](https://platform.openai.com/docs/api-reference)
- SMS Notifications: [AWS SNS Docs](https://docs.aws.amazon.com/sns/index.html)
- Rating calculations powered by OutSystems APIs

For detailed technical flow and diagrams, refer to `G5T1 Report.docx` and presentation slides.

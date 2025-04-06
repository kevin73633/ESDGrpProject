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
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. Ensure `.env` file is configured with your AWS credentials, OpenAI key, and database login:
   ```env
   AWS_ACCESS_KEY_ID=AKIA...
   AWS_SECRET_ACCESS_KEY=UTYN...
   AWS_REGION=ap-southeast-1
   RABBITMQ_HOST=localhost
   RABBITMQ_EXCHANGE=deal_events
   DBLOGIN=root:root
   OPENAI_API_KEY=sk-proj-...
   ```

3. Launch backend services with Docker Compose:
   ```bash
   docker compose up -d --build
   ```

4. Launch the frontend:
   ```bash
   cd frontend
   npm install
   npm run serve
   ```

5. Access the platform at:
   - [http://localhost:8080/login](http://localhost:8080/login)

### 🧪 Test Credentials
- **User 1 (Buyer):**
  - Username: `12345678`
  - Password: `user1`
- **User 2 (Seller):**
  - Username: `22345678`
  - Password: `user2`

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
- ✅ Post-exchange fund release and rating (Verify Receipt)
- 🚩 Intelligent chat moderation with reporting (Report Chat)
- 💬 Real-time AMQP messaging + SMS alerts
- 🧾 RESTful microservices (Chat, Product, Deal, Rating, etc.)

---

## 📄 API Documentation
You can explore the RESTful API documentation using Swagger UI:

🔗 [View Swagger API Docs](http://localhost:5300/apidocs)

---

## 🧠 Contributors (G5T1)
- **Dessy**: ChatGPT microservice, Swagger, Report & Slides
- **Kirthi**: Notification microservice
- **Kevin**: User, Product, Deal, Chat microservices
- **Kai Zhe**: Rating microservice, OutSystems integration, Report
- **Precia**: Frontend development, API integration
- **Shamel**: Payment, Account, PaymentRecord microservices, Kong config

---

## 📅 Additional Notes
- ChatGPT moderation API: [OpenAI Docs](https://platform.openai.com/docs/api-reference)
- SMS Notifications: [AWS SNS Docs](https://docs.aws.amazon.com/sns/index.html)
- Rating calculations powered by OutSystems APIs

For detailed technical flow and diagrams, refer to `G5T1 Report.docx` and presentation slides.

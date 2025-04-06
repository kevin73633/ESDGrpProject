
# README.md

## 📦 Deal Sharing Marketplace Platform
A peer-to-peer product deal sharing platform supporting secure escrow payments, dispute resolution, real-time messaging, and intelligent chat moderation.

---

## 🚀 Installation & Setup

### 📁 Prerequisites
Ensure the following are installed:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Optional (for development): Python 3.9+, Node.js (if editing frontend)

### 📥 Clone and Setup
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. Ensure `.env` file is configured with your AWS credentials and other environment variables:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=ap-southeast-1
   RABBITMQ_HOST=rabbitmq
   RABBITMQ_EXCHANGE=deal_events
   ```

3. Launch with Docker Compose:
   ```bash
   docker compose up -d --build
   ```

4. Access the frontend via:
   - [http://localhost:8080/login](http://localhost:8080/login)

### 🧪 Test Credentials
- **User 1 (Buyer):**
  - Username: `12345678`
- **User 2 (Seller):**
  - Username: `22345678`

---

## 🧠 Technologies Used

| Category | Tech Stack |
|----------|------------|
| Frontend | Vue.js 3, Bootstrap |
| Backend | Python (Flask), MySQL |
| Microservices | Docker, Flask REST APIs |
| Messaging | RabbitMQ (AMQP), AWS SNS |
| Rating Engine | OutSystems REST API Integration |
| Moderation | OpenAI ChatGPT API (chat analysis) |
| Gateway | Kong API Gateway |
| Docs | Swagger (OpenAPI Spec) |

---

## 📚 Key Features
- 🔐 Escrow payment system (Confirm Deal)
- ✅ Post-exchange fund release and rating (Verify Receipt)
- 🚩 Intelligent chat moderation with reporting (Report Chat)
- 💬 Real-time AMQP messaging + SMS alerts
- 🧾 RESTful microservices (Chat, Product, Deal, Rating, etc.)

---

## 📖 API Documentation

You can explore the RESTful API documentation using Swagger UI:

🔗 [View Swagger API Docs](http://localhost:5300/apidocs)

---

## 🧠 Contributors (G5T1)
- Dessy (ChatGPT microservice, Swagger, Docs)
- Kirthi (Notification service)
- Kevin (User, Product, Deal, Chat microservices)
- Kai Zhe (Rating microservice, OutSystems, Docs)
- Precia (Frontend, API integration)
- Shamel (Payment, Account, PaymentRecord, Kong)

---

## 📄 Additional Notes
- ChatGPT moderation API: [OpenAI Docs](https://platform.openai.com/docs/api-reference)
- SMS Notifications: [AWS SNS Docs](https://docs.aws.amazon.com/sns/index.html)
- OutSystems Rating API used for user credibility calculation.

For more details, refer to the included `G5T1 Report.docx` and presentation slides.

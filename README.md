# Truevoice – Voice Verification API

TrueVoice is a **serverless voice verification system** that uses:

* **Whisper (OpenAI)** → verifies users spoke the correct challenge phrase.
* **SpeechBrain ECAPA-TDNN** → extracts embeddings for speaker verification.
* **FastAPI** → RESTful API endpoints.
* **SQLite (local)** or **S3 (AWS)** → store enrollments.

It’s designed for **low-cost serverless scaling** via **AWS Lambda + API Gateway**.


## ✨ Features

* 🔐 **JWT Authentication** for secure endpoints.
* 🗣 **Liveness Detection** (Whisper ensures phrase spoken matches challenge).
* 🎙 **Speaker Verification** using SpeechBrain ECAPA-TDNN embeddings.
* 📦 **Containerized with Docker** for portability.
* ⚡ **Serverless Deployment** on AWS Lambda + API Gateway (HTTP API).
* 🧪 **CI/CD with GitHub Actions** (pytest → build Docker → push ECR → update Lambda).


## 📂 Project Structure

```
.
├── app/
│   └── main.py              # FastAPI app with endpoints
├── tests/
│   └── test_app.py          # Pytest unit tests
├── Dockerfile               # Build container image for Lambda
├── requirements.txt         # Dependencies
├── .github/
│   └── workflows/
│       └── deploy.yml       # CI/CD pipeline
└── README.md
```

---

## 🛠 Setup (Local Development)

### 1. Clone repo

```bash
git clone https://github.com/<your-username>/truevoice.git
cd truevoice
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run locally

```bash
uvicorn app.main:app --reload --port 8000
```

Open Swagger docs: 👉 `http://127.0.0.1:8000/docs`

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 🚀 Deployment on AWS Lambda + API Gateway

### 1. **Build Docker Image**

```bash
docker build -t truevoice .
```

### 2. **Tag & Push to AWS ECR**

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com

docker tag truevoice:latest <account_id>.dkr.ecr.<region>.amazonaws.com/truevoice-lambda:latest
docker push <account_id>.dkr.ecr.<region>.amazonaws.com/truevoice-lambda:latest
```

### 3. **Deploy to Lambda**

```bash
aws lambda update-function-code \
  --function-name truevoice-lambda \
  --image-uri <account_id>.dkr.ecr.<region>.amazonaws.com/truevoice-lambda:latest
```

### 4. **Expose with API Gateway (HTTP API)**

* Create an **HTTP API Gateway**.
* Integrate it with your Lambda function.
* Deploy and note your public URL.


## 🔄 CI/CD (GitHub Actions)

Every push to `main`:

1. Runs **pytest**.
2. Builds Docker image.
3. Pushes to **ECR**.
4. Updates **Lambda** function automatically.

Workflow: `.github/workflows/deploy.yml`


## 🔑 Environment Variables

Set in **AWS Lambda → Configuration → Environment Variables**:

* `JWT_SECRET` → secret key for JWT auth
* `OPENAI_API_KEY` → OpenAI API key for Whisper


## 📌 API Endpoints

* `POST /token` → Get JWT token
* `POST /enroll` → Enroll new speaker voice
* `POST /verify` → Verify speaker against enrollment

See:

* `docs/postman_collection.json` (Postman collection)
* `docs/openapi.yaml` (Swagger spec)

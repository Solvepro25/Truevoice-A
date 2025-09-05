# TrueVoice API

TrueVoice is a voice verification API built with FastAPI. It uses OpenAI Whisper for speech-to-text and embeddings for voice enrollment and verification.

## Features
- 🎤 Voice enrollment and verification with challenge text
- 🔑 JWT authentication for all endpoints
- 🐳 Docker + docker-compose setup
- ✅ CI with GitHub Actions (pytest)
- 📜 Swagger/OpenAPI spec (`collection.yaml`)

## Requirements
- Python 3.10+
- OpenAI API key

## Running Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

## Running With Docker
docker-compose up --build

The service will run on http://localhost:8000

## Endpoints
- POST /token → Generate JWT token
- POST /enroll → Enroll a voice sample
- POST /verify → Verify a voice sample

## Authentication
Get a token with:
```bash
curl -X POST http://localhost:8000/token -F "user_id=user123"

Then use toke in your request
```make file
Authorization: Bearer <your_token>

## Running Tests
```bash
pytest

## Deployment (Azure App Service with Docker)
1. Push your repo to GitHub
2. Create an Azure App Service
3. Choose Docker Container and connect your GitHub repo
4. Add environment variables:
- OPENAI_API_KEY
- JWT_SECRET
5. Deploy 🚀

## OpenAPI Collection
Import collection.yaml into Postman or Swagger UI.



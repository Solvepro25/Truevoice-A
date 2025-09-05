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

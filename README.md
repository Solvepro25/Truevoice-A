# 🎙️ TrueVoice – Voice Biometric Verification API

TrueVoice is a **voice authentication API** that combines:

* **SpeechBrain ECAPA-TDNN** → for **speaker verification** (accent & voice identity).
* **Whisper** → for **liveness detection** (ensuring user actually speaks the prompted phrase).
* **Noise reduction** → powered by SpeechBrain **Spectral Mask Enhancement**.

This ensures secure, fast, and reliable **voice-based user authentication** for applications across **finance, health, education, and government services**.

---

## 🚀 Features

* 🔊 **Speaker Verification** – Identify & verify users based on their unique voiceprint.
* 🗣️ **Liveness Check** – Ensure users speak a prompted phrase live (not a replay attack).
* 🎧 **Noise Reduction** – Clean audio before processing for better accuracy.
* 📜 **REST API Endpoints** – Exposed via FastAPI with Swagger/OpenAPI docs.
* 🧪 **Unit Tests** – Pytest suite with pre-cached SpeechBrain models.
* 📦 **Dockerized** – Ready for cloud deployment (Azure, AWS, GCP).
* 📑 **Docs Included** – Postman collection (`postman_collection.json`) and Swagger (`collection.yaml`).

---

## 📂 Project Structure

```
truevoice-api/
├── app/
│   └── main.py               # FastAPI app with endpoints
├── tests/
│   └── test_app.py           # Unit tests for endpoints
├── pretrained_models/        # Cached models (via CI)
├── Dockerfile                # Container build file
├── docker-compose.yml        # Local development runner
├── requirements.txt          # Python dependencies
├── postman_collection.json   # Postman API collection
├── collection.yaml           # Swagger/OpenAPI spec
├── .github/workflows/ci.yml  # GitHub Actions CI pipeline
└── README.md                 # Documentation
```

---

## ⚙️ Installation

### 1. Clone Repo

```bash
git clone https://github.com/your-username/truevoice-api.git
cd truevoice-api
```

### 2. Create Virtual Env & Install Deps

```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run API Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Open docs at:

* Swagger → [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc → [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests

```bash
pytest -v --disable-warnings
```

✅ CI will **cache SpeechBrain models** to avoid repeated downloads.

---

## 🐳 Running with Docker

### Build & Run

```bash
docker build -t truevoice .
docker run -p 8000:8000 truevoice
```

### Using Docker Compose

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

### 🔹 Health Check

```
GET /health
```

Response:

```json
{ "status": "ok" }
```

### 🔹 Enroll User Voice

```
POST /enroll/{user_id}
```

Upload `.wav` file (16kHz mono).
Stores voice embedding for future verification.

### 🔹 Verify User Voice

```
POST /verify/{user_id}
```

Upload `.wav` file.
Checks if voice matches enrolled profile.

### 🔹 Liveness Check

```
POST /liveness
```

Input: audio file + expected phrase.
Verifies phrase spoken matches prompt (anti-replay).

---

## 📑 API Documentation

* **Swagger/OpenAPI** → [`collection.yaml`](./collection.yaml)
* **Postman Collection** → [`postman_collection.json`](./postman_collection.json)

Import into Postman to test endpoints easily.

---

## ☁️ Deployment

### Deploy on **Azure App Service with Docker**

1. Push repo to GitHub.
2. Ensure Dockerfile is present.
3. Run:

```bash
az login
az webapp up --sku B1 --name truevoice-api --runtime "DOCKER|python:3.10"
```

### Deploy on **AWS ECS / Fargate**

1. Push Docker image to ECR.
2. Create ECS service with Fargate task.
3. Map port 8000 → Application Load Balancer.

---

## 🔒 Security Notes

* Use **HTTPS** in production.
* Rotate enrolled voiceprints periodically.
* Store embeddings securely (encrypted).

---

## 📌 Roadmap

* [ ] Multi-language accent training support
* [ ] Voice activity detection (VAD) optimization
* [ ] Integration with OAuth2 / JWT auth
* [ ] Analytics dashboard for verification logs

---

## 👨‍💻 Contributing

1. Fork repo
2. Create feature branch (`git checkout -b feature/foo`)
3. Commit changes (`git commit -m "Add foo"`)
4. Push branch (`git push origin feature/foo`)
5. Open PR 🚀

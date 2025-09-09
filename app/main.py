# app/main.py
import os
import json
import boto3
import tempfile
import shutil
import numpy as np
import datetime
import torch
import torchaudio
from fastapi import FastAPI, UploadFile, Form, HTTPException
from speechbrain.pretrained import EncoderClassifier
import httpx
from mangum import Mangum

# --- Config ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
AWS_BUCKET = os.getenv("S3_BUCKET", "truevoice-users")

s3_client = boto3.client("s3")

# --- Load SpeechBrain model once (cold start optimization) ---
speaker_model = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/ecapa"
)

# --- Utils ---
async def transcribe_audio(audio_path: str) -> str:
    """Send audio to Whisper for transcription (liveness check)."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": open(audio_path, "rb")}
    data = {"model": "whisper-1"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, files=files, data=data)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Whisper failed: {resp.text}")
    return resp.json()["text"]

def preprocess_audio(audio_path: str):
    """Load audio + apply noise reduction."""
    waveform, sr = torchaudio.load(audio_path)
    # Simple noise reduction: voice activity detection (VAD)
    try:
        waveform = torchaudio.functional.vad(waveform, sample_rate=sr)
    except Exception:
        pass  # fallback if VAD fails
    return waveform, sr

def compute_embedding(audio_path: str) -> np.ndarray:
    """Compute ECAPA-TDNN embedding with SpeechBrain."""
    waveform, sr = preprocess_audio(audio_path)
    with torch.no_grad():
        emb = speaker_model.encode_batch(waveform)
    return emb.squeeze().cpu().numpy()

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

def save_embedding_to_s3(user_id: str, embedding: np.ndarray):
    obj_key = f"{user_id}.json"
    s3_client.put_object(
        Bucket=AWS_BUCKET,
        Key=obj_key,
        Body=json.dumps({
            "user_id": user_id,
            "embedding": embedding.tolist(),
            "created_at": datetime.datetime.utcnow().isoformat()
        })
    )

def load_embedding_from_s3(user_id: str) -> np.ndarray:
    obj_key = f"{user_id}.json"
    try:
        resp = s3_client.get_object(Bucket=AWS_BUCKET, Key=obj_key)
        data = json.loads(resp["Body"].read())
        return np.array(data["embedding"], dtype=np.float32)
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="User not enrolled")

# --- FastAPI app ---
app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/enroll")
async def enroll(user_id: str = Form(...), challenge_text: str = Form(...), audio: UploadFile = Form(...)):
    tmpdir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmpdir, audio.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        transcript = await transcribe_audio(audio_path)
        if transcript.strip().lower() != challenge_text.strip().lower():
            raise HTTPException(status_code=400, detail="Challenge mismatch")

        embedding = compute_embedding(audio_path)
        save_embedding_to_s3(user_id, embedding)
        return {"message": f"Enrollment successful for {user_id}"}
    finally:
        shutil.rmtree(tmpdir)

@app.post("/verify")
async def verify(user_id: str = Form(...), challenge_text: str = Form(...), audio: UploadFile = Form(...)):
    tmpdir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmpdir, audio.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        transcript = await transcribe_audio(audio_path)
        if transcript.strip().lower() != challenge_text.strip().lower():
            raise HTTPException(status_code=400, detail="Challenge mismatch")

        new_embedding = compute_embedding(audio_path)
        stored_embedding = load_embedding_from_s3(user_id)

        sim = cosine_similarity(new_embedding, stored_embedding)
        return {
            "user_id": user_id,
            "similarity": sim,
            "verified": sim > 0.75
        }
    finally:
        shutil.rmtree(tmpdir)

# --- Lambda Handler ---
handler = Mangum(app)  # 👈 entrypoint for API Gateway

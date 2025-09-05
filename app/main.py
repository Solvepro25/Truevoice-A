# app/main.py
import os
import shutil
import tempfile
import jwt
import datetime
from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
import httpx
import numpy as np
import torchaudio
from speechbrain.pretrained import EncoderClassifier, SpectralMaskEnhancement

# --- Config ---
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# --- DB setup ---
Base = declarative_base()
engine = create_engine("sqlite:///truevoice.db")
SessionLocal = sessionmaker(bind=engine)


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    embedding = Column(String)  # stored as bytes
    created_at = Column(DateTime)


Base.metadata.create_all(bind=engine)

# --- Auth ---
security = HTTPBearer()


class TokenData(BaseModel):
    user_id: str


def create_access_token(
    data: dict, expires_delta: Optional[datetime.timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (
        expires_delta
        or datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# --- Load Models (once at startup) ---
speaker_model = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/ecapa"
)

denoiser = SpectralMaskEnhancement.from_hparams(
    source="speechbrain/mtl-mimic-voicebank", savedir="pretrained_models/denoiser"
)


# --- Utilities ---
async def transcribe_audio(audio_path: str) -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": open(audio_path, "rb")}
    data = {"model": "whisper-1"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data)
    if response.status_code != 200:
        raise HTTPException(
            status_code=500, detail=f"Whisper failed: {response.text}"
        )
    return response.json()["text"]


def compute_embedding(audio_path: str) -> np.ndarray:
    # Load audio
    signal, fs = torchaudio.load(audio_path)

    # Denoise
    enhanced = denoiser.enhance_batch(signal)

    # Extract embedding
    embedding = speaker_model.encode_batch(enhanced)
    return embedding.squeeze().detach().cpu().numpy()


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


# --- FastAPI app ---
app = FastAPI()


@app.post("/token")
def login(user_id: str = Form(...)):
    access_token = create_access_token(data={"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/enroll")
async def enroll(
    user_id: str = Form(...),
    challenge_text: str = Form(...),
    audio: UploadFile = Form(...),
    token: dict = Depends(verify_token),
):
    db = SessionLocal()
    tmpdir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmpdir, audio.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        transcript = await transcribe_audio(audio_path)
        if transcript.strip().lower() != challenge_text.strip().lower():
            raise HTTPException(status_code=400, detail="Challenge mismatch")

        embedding = compute_embedding(audio_path)
        db.add(
            Enrollment(
                user_id=user_id,
                embedding=embedding.tobytes(),
                created_at=datetime.datetime.utcnow(),
            )
        )
        db.commit()
        return {"message": "Enrollment successful"}
    finally:
        shutil.rmtree(tmpdir)


@app.post("/verify")
async def verify(
    user_id: str = Form(...),
    challenge_text: str = Form(...),
    audio: UploadFile = Form(...),
    token: dict = Depends(verify_token),
):
    db = SessionLocal()
    tmpdir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmpdir, audio.filename)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        transcript = await transcribe_audio(audio_path)
        if transcript.strip().lower() != challenge_text.strip().lower():
            raise HTTPException(status_code=400, detail="Challenge mismatch")

        new_embedding = compute_embedding(audio_path)
        enrollments = (
            db.query(Enrollment).filter(Enrollment.user_id == user_id).all()
        )
        if not enrollments:
            raise HTTPException(status_code=404, detail="No enrollment found")

        sims = [
            cosine_similarity(
                new_embedding, np.frombuffer(e.embedding, dtype=np.float64)
            )
            for e in enrollments
        ]
        return {"verified": max(sims) > 0.75, "similarity": max(sims)}
    finally:
        shutil.rmtree(tmpdir)

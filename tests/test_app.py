# tests/test_app.py
import io
import pytest
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app, create_access_token

client = TestClient(app)

@pytest.fixture
def token():
    return create_access_token({"sub": "user123"})

def make_wav_bytes(duration_sec=1.0, samplerate=16000, freq=440.0):
    """Generate a sine wave WAV in memory."""
    t = np.linspace(0, duration_sec, int(samplerate * duration_sec), endpoint=False)
    data = 0.1 * np.sin(2 * np.pi * freq * t)
    buf = io.BytesIO()
    sf.write(buf, data, samplerate, format="WAV")
    buf.seek(0)
    return buf

def test_token_generation():
    res = client.post("/token", data={"user_id": "user123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

@patch("app.main.transcribe_audio", return_value="hello world")
def test_enroll_and_verify(mock_transcribe, token):
    # --- Enroll user ---
    wav_file = make_wav_bytes()
    files = {"audio": ("test.wav", wav_file, "audio/wav")}
    data = {"user_id": "user123", "challenge_text": "hello world"}
    res = client.post(
        "/enroll",
        headers={"Authorization": f"Bearer {token}"},
        data=data,
        files=files,
    )
    assert res.status_code == 200
    assert res.json()["message"] == "Enrollment successful"

    # --- Verify user ---
    wav_file2 = make_wav_bytes(freq=450.0)  # slightly different wave
    files2 = {"audio": ("test2.wav", wav_file2, "audio/wav")}
    data2 = {"user_id": "user123", "challenge_text": "hello world"}
    res2 = client.post(
        "/verify",
        headers={"Authorization": f"Bearer {token}"},
        data=data2,
        files=files2,
    )
    assert res2.status_code == 200
    body = res2.json()
    assert "verified" in body
    assert "similarity" in body

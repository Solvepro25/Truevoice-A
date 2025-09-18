# app/main.py
import sys
import os
from fastapi import FastAPI
from mangum import Mangum

# --- Add EFS path for heavy dependencies ---
# AWS Lambda will mount your EFS at /mnt/efs
efs_path = "/mnt/efs/python"
if os.path.exists(efs_path):
    sys.path.append(efs_path)

# ✅ Now safe to import ML libraries (they will load from EFS)
try:
    import torch
    import whisper
    import speechbrain
except ImportError:
    # In case local dev doesn’t have EFS, avoid crashing
    print("⚠️ ML dependencies not found (Torch/Whisper/Speechbrain). Running in lightweight mode.")

# --- Internal imports ---
from app.routes import enrollment, challenge, health, token, verification
from app.db import Base, engine
from app.models import Enrollment, VerificationLog

# --- DB setup ---
Base.metadata.create_all(bind=engine)

# --- FastAPI app ---
app = FastAPI(title="Voice Verification API")

# Routers
app.include_router(enrollment.router, prefix="/api", tags=["Enrollment"])
app.include_router(challenge.router, prefix="/api", tags=["Challenge"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(token.router, prefix="/api", tags=["Token"])
app.include_router(verification.router, prefix="/api", tags=["Verification"])

# ✅ Lambda entrypoint
handler = Mangum(app)

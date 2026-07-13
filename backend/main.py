from fastapi import FastAPI, UploadFile, File
import os
import uuid
import shutil
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# ✅ AUDIO IMPORTS
from backend.analysis.audio import (
    extract_audio,
    transcribe_audio,
    analyze_speech
)

# ✅ VISUAL IMPORT
from backend.analysis.visual import analyze_gaze

# ✅ FEEDBACK IMPORT (LOCAL SCORING)
from backend.analysis.feedback import (
    score_speaking,
    score_gaze
)

# ✅ AI SERVICE
from backend.services import ai_client

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Speaking Coach v2")

# === CORS ===
# Comma-separated list so the deployed frontend origin can be added without a
# code change: CORS_ORIGINS=https://myapp.vercel.app
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# === DIRECTORIES ===
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Backend is running clean ✅"}


@app.get("/health")
def health():
    """Tells you at a glance whether the AI key is actually loaded."""
    return {
        "status": "ok",
        "ai_provider": "groq",
        "ai_configured": ai_client.is_configured(),
        "model": ai_client.MODEL,
    }


@app.get("/debug/models")
def debug_models():
    """Enumerates models available to the current Groq key."""
    try:
        models = ai_client.list_models()
        return {"count": len(models), "models": models}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload")
def upload_video(file: UploadFile = File(...)):
    # Deliberately sync (`def`, not `async def`): every step below — ffmpeg,
    # Whisper, MediaPipe, the Groq call — is blocking and CPU-bound. As `async def`
    # it ran on the event loop and starved everything else, including the socket
    # under the Groq SDK, which then timed out. `def` makes FastAPI run it in a
    # threadpool instead, so the loop stays free to serve other requests.
    file_path = None
    audio_path = None

    try:
        # --- Generate ID ---
        video_id = str(uuid.uuid4())

        # --- Safe filename ---
        filename = file.filename or "uploaded_video.mp4"

        # --- Save File ---
        file_path = os.path.join(UPLOAD_DIR, f"{video_id}_{filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("✅ Video saved")

        # --- AUDIO PIPELINE ---
        audio_path = extract_audio(file_path)
        logger.info("🎧 Audio extracted")

        transcript, duration = transcribe_audio(audio_path)
        logger.info("📝 Transcription complete")

        speech_metrics = analyze_speech(transcript, duration)
        logger.info("📊 Speech analysis done")

        # --- VISUAL PIPELINE ---
        visual_metrics = analyze_gaze(file_path)
        logger.info("👀 Gaze analysis done")

        # --- COMBINE METRICS ---
        metrics = {
            **speech_metrics,
            **visual_metrics
        }

        # --- SAFE ACCESS ---
        wpm = metrics.get("wpm", 0)
        filler_count = metrics.get("filler_count", 0)
        gaze_percent = metrics.get("camera_facing_percentage", 0)

        # --- SCORING ---
        speaking_score = score_speaking(wpm, filler_count)
        gaze_score = score_gaze(gaze_percent)

        overall_score = round(
            speaking_score * 0.6 + gaze_score * 0.4,
            2
        )

        # --- AI FEEDBACK (falls back to rule-based coach if Groq is down) ---
        feedback = ai_client.get_ai_feedback(metrics)

        # --- RESPONSE ---
        return {
            "status": "success",
            "video_id": video_id,
            "filename": filename,
            "transcript": transcript,
            "duration": duration,
            "metrics": metrics,
            "scores": {
                "speaking_score": speaking_score,
                "gaze_score": gaze_score,
                "overall_score": overall_score
            },
            "ai_feedback": {
                "summary": "Here’s a quick evaluation of your speaking performance.",
                "source": feedback["source"],
                "details": feedback["points"]
            }
        }

    except Exception as e:
        logger.exception("❌ Upload failed")
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        # Don't leak the video and extracted .wav — on a container the disk is
        # ephemeral and small, and we have no reason to keep them after analysis.
        for path in (file_path, audio_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as e:
                    logger.warning("Could not remove %s: %s", path, e)

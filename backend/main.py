from fastapi import FastAPI, UploadFile, File
import os
import uuid
import shutil
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
from backend.services.ai_client import get_ai_feedback

app = FastAPI(title="AI Speaking Coach v2")

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # --- Generate ID ---
        video_id = str(uuid.uuid4())

        # --- Safe filename ---
        filename = file.filename or "uploaded_video.mp4"

        # --- Save File ---
        file_path = os.path.join(UPLOAD_DIR, f"{video_id}_{filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("✅ Video saved")

        # --- AUDIO PIPELINE ---
        audio_path = extract_audio(file_path)
        print("🎧 Audio extracted")

        transcript, duration = transcribe_audio(audio_path)
        print("📝 Transcription complete")

        speech_metrics = analyze_speech(transcript, duration)
        print("📊 Speech analysis done")

        # --- VISUAL PIPELINE ---
        visual_metrics = analyze_gaze(file_path)
        print("👀 Gaze analysis done")

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

        # --- AI FEEDBACK ---
        feedback = get_ai_feedback(metrics)

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
                "details": feedback
            }
        }

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }
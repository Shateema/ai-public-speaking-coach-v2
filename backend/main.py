from fastapi import FastAPI, UploadFile, File
import os
import uuid
import shutil

# ✅ AUDIO IMPORTS
from backend.analysis.audio import (
    extract_audio,
    transcribe_audio,
    analyze_speech
)

# ✅ VISUAL IMPORT
from backend.analysis.visual import analyze_gaze

app = FastAPI(title="AI Speaking Coach v2")

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

        # --- Save File ---
        file_path = os.path.join(UPLOAD_DIR, f"{video_id}_{file.filename}")

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

        # --- COMBINE ---
        metrics = {
            **speech_metrics,
            **visual_metrics
        }

        return {
            "status": "success",
            "video_id": video_id,
            "filename": file.filename,
            "transcript": transcript,
            "duration": duration,
            "metrics": metrics
        }

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }
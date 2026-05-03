from fastapi import FastAPI, UploadFile, File
import os
import uuid
import shutil

app = FastAPI(title="AI Speaking Coach v2")

# === DIRECTORIES ===
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Backend is running clean ✅"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # Generate unique ID
    video_id = str(uuid.uuid4())

    # Create safe file path
    file_path = os.path.join(UPLOAD_DIR, f"{video_id}_{file.filename}")

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "success",
        "video_id": video_id,
        "filename": file.filename,
        "saved_path": file_path
    }
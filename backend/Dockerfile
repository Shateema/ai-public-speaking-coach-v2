# Build context is the repo root:  docker build -f backend/Dockerfile .
FROM python:3.11-slim

# ffmpeg    — backend/analysis/audio.py shells out to it to strip the audio track.
# libgl1    — opencv-contrib-python (mediapipe's required opencv) links against libGL.
# libportaudio2 — `import mediapipe` transitively imports sounddevice, which fails
#                 at import time without PortAudio. Omit it and the app won't boot.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
        libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the Whisper weights into the image so the first request doesn't stall on
# a ~150MB download (containers start with an empty cache).
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', compute_type='int8')"

COPY backend/ ./backend/

EXPOSE 8000

# Render (and most PaaS) inject $PORT; default to 8000 for local docker compose.
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

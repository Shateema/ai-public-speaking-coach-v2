# Backend image. Used by docker compose locally and by Hugging Face Spaces,
# which requires the Dockerfile at the repo root and runs it as UID 1000.

FROM python:3.11-slim

# ffmpeg        — backend/analysis/audio.py shells out to it to strip the audio track.
# libgl1        — opencv-contrib-python (mediapipe's required opencv) links against libGL.
# libportaudio2 — `import mediapipe` transitively imports sounddevice, which fails at
#                 import time without PortAudio. Omit it and the app won't boot.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
        libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces runs containers as a non-root user with UID 1000. Create it and own
# /app up front — Docker would otherwise create WORKDIR as root, and the app
# needs to write backend/uploads at runtime.
RUN useradd -m -u 1000 user && mkdir -p /app && chown -R user:user /app

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/.cache/huggingface \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Bake the Whisper weights into the image so the first request doesn't stall on a
# ~150MB download. Runs as `user` so the cache lands in $HF_HOME, readable at runtime.
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', compute_type='int8')"

COPY --chown=user:user backend/ ./backend/

# HF Spaces expects 7860. $PORT lets other hosts (or compose) override it.
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]

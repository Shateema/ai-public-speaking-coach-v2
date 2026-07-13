---
title: AI Speaking Coach
emoji: 🎤
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 🎤 AI Speaking Coach v2

An end-to-end AI-powered speaking coach that analyzes video recordings and delivers feedback on speech pace, filler words, and eye contact — powered by Groq (Llama 3.3), faster-whisper, and MediaPipe.

> The YAML block above configures the Hugging Face Space. It's ignored by GitHub
> and by everything else — leave it in place.

---

## Quick start

Requires **Python 3.11+**, **Node 18+**, and **ffmpeg on PATH**.

```bash
git clone <repo-url>
cd ai-public-speaking-coach-v2

cp .env.example .env          # then paste your Groq key into .env
```

**Terminal 1 — backend:**
```bash
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm install
npm run dev
```

- Frontend → http://localhost:5173
- Backend → http://127.0.0.1:8000
- Is the AI key loaded? → http://127.0.0.1:8000/health

> **No API key?** The app still runs. It falls back to a rule-based coach and the
> UI labels the result "Basic feedback". Get a free key at
> [console.groq.com/keys](https://console.groq.com/keys) for real AI coaching.

### Or with Docker

If you have Docker, this replaces everything above — no venv, no ffmpeg install:

```bash
cp .env.example .env
docker compose up
```

Same URLs. The first build takes a few minutes (it bakes in the Whisper model).

---

## Architecture

```
┌─────────────────────┐     POST /upload      ┌────────────────────────┐
│   Frontend          │ ────────────────────▶ │   Backend              │
│   React 19 + Vite   │                       │   FastAPI · port 8000  │
│   port 5173         │ ◀──────────────────── │                        │
└─────────────────────┘     JSON results      └──────────┬─────────────┘
                                                         │ Groq SDK
                                                         ▼
                                              ┌────────────────────────┐
                                              │  Groq API              │
                                              │  llama-3.3-70b         │
                                              └────────────────────────┘
```

### Analysis pipeline (per upload)

```
Video file
   │
   ├─▶ ffmpeg          → extract WAV audio
   ├─▶ faster-whisper  → transcribe → WPM + filler word count
   ├─▶ MediaPipe       → frame sampling → eye-contact %
   └─▶ Groq / Llama 3.3 → 3 actionable coaching bullet points
                          (falls back to rule-based coach on any failure)
```

Uploaded videos and extracted audio are deleted as soon as analysis finishes.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, CSS Modules |
| Backend | FastAPI, Python 3.11, uvicorn |
| AI | Groq `llama-3.3-70b-versatile` (`groq` SDK) |
| Speech | faster-whisper (base model, int8) |
| Vision | MediaPipe FaceMesh, OpenCV |
| Audio extraction | ffmpeg |

---

## Environment variables

Backend — root `.env` (see [`.env.example`](.env.example)):

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | — | Groq key. Omit to use rule-based feedback. |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Any model from `GET /debug/models`. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins. |

Frontend — `frontend/.env` (see [`frontend/.env.example`](frontend/.env.example)):

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_URL` | `http://127.0.0.1:8000` | Backend base URL. |

Neither `.env` is committed.

---

## API Reference

### `POST /upload`

Upload a video for full analysis. **Request:** `multipart/form-data`, field `file`.

```json
{
  "status": "success",
  "video_id": "uuid",
  "filename": "my-video.mp4",
  "transcript": "Full transcribed text...",
  "duration": 120.5,
  "metrics": {
    "word_count": 270,
    "wpm": 135,
    "filler_count": 5,
    "camera_facing_percentage": 72.0
  },
  "scores": {
    "speaking_score": 78,
    "gaze_score": 70,
    "overall_score": 75.2
  },
  "ai_feedback": {
    "summary": "Here's a quick evaluation of your speaking performance.",
    "source": "ai",
    "details": [
      "Your pace of 135 WPM is ideal — keep it there.",
      "Cut the 5 filler words by pausing instead.",
      "Hold eye contact past 72% to look more confident."
    ]
  }
}
```

`ai_feedback.source` is `"ai"` (Groq) or `"rule-based"` (fallback). The UI shows a
"Basic feedback" note for the latter.

### `GET /health`

```json
{ "status": "ok", "ai_provider": "groq", "ai_configured": true, "model": "llama-3.3-70b-versatile" }
```

`ai_configured: false` means `GROQ_API_KEY` is missing — check this first if you
get basic feedback instead of AI coaching.

### `GET /debug/models`

Lists every model your Groq key can reach.

---

## Scoring

| Metric | Weight | Logic |
|---|---|---|
| Speaking score | 60% | Penalizes WPM outside 100–180, filler words > 5 |
| Gaze score | 40% | Tiered: ≥75% → 90, ≥50% → 70, ≥30% → 50, else 30 |
| Overall score | — | `speaking × 0.6 + gaze × 0.4` |

---

## Deployment (free)

Backend → **Hugging Face Spaces** (Docker). Frontend → **Vercel** (static).
Both are free tiers, no credit card.

Whisper + MediaPipe need ~1.5GB RAM, which rules out most free hosts (Render's
free tier caps at 512MB and OOMs on the first upload). A free HF Space gets
2 vCPU and 16GB, so it fits comfortably.

### 1. Backend → Hugging Face Space

1. Create a Space at [huggingface.co/new-space](https://huggingface.co/new-space):
   **SDK = Docker**, template **Blank**, hardware **CPU basic (free)**.
2. Push this repo to the Space (it's a git remote):
   ```bash
   git remote add space https://huggingface.co/spaces/<user>/<space-name>
   git push space main
   ```
3. In the Space → **Settings → Variables and secrets**, add:
   - Secret `GROQ_API_KEY` = your Groq key
   - Variable `CORS_ORIGINS` = your Vercel URL (set after step 2 below)
4. Wait for the build, then check `https://<user>-<space-name>.hf.space/health`.
   `ai_configured: true` means the image booted and the key loaded.

The root [`Dockerfile`](Dockerfile) already targets port 7860 and runs as UID 1000,
which is what Spaces requires. Free Spaces sleep after 48h idle and wake on the
next request.

### 2. Frontend → Vercel

1. **New Project** → import this repo → set **Root Directory** to `frontend`.
2. Add env var `VITE_API_URL` = your Space URL (`https://<user>-<space-name>.hf.space`).
3. Deploy, then go back and set `CORS_ORIGINS` on the Space to your Vercel URL —
   without it the browser blocks every upload.

---

## Project Structure

```
ai-public-speaking-coach-v2/
├── backend/
│   ├── main.py                  # FastAPI app: /upload, /health, /debug/models
│   ├── analysis/
│   │   ├── audio.py             # ffmpeg extraction, Whisper transcription, WPM/fillers
│   │   ├── visual.py            # MediaPipe gaze detection
│   │   └── feedback.py          # Scoring + rule-based coach (AI fallback)
│   └── services/
│       └── ai_client.py         # Groq call + fallback logic
├── frontend/
│   └── src/components/
│       ├── VideoUpload.jsx      # Drag & drop upload zone
│       ├── ResultsDashboard.jsx # Results layout
│       └── ScoreRing.jsx        # Animated SVG score ring
├── docker-compose.yml           # One-command local dev
├── Dockerfile                   # Backend image (compose + HF Spaces)
└── requirements.txt
```

---

## Known Notes

- faster-whisper `base` is used for speed. Swap to `small` or `medium` for better accuracy.
- Gaze detection uses a nose-position heuristic (MediaPipe landmark #1). Works best with a front-facing camera at desk distance.
- Filler-word counting is substring-based, so "like" also matches inside "likely".

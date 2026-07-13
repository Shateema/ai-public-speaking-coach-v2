# 🎤 AI Speaking Coach v2

An end-to-end AI-powered speaking coach that analyzes video recordings and delivers feedback on speech pace, filler words, and eye contact — powered by Groq (Llama 3.3), faster-whisper, and MediaPipe.

---

## Quick start

```bash
git clone <repo-url>
cd ai-public-speaking-coach-v2

cp .env.example .env          # then paste your Groq key into .env
docker compose up
```

- Frontend → http://localhost:5173
- Backend → http://127.0.0.1:8000
- Is the AI key loaded? → http://127.0.0.1:8000/health

That's it — Docker brings its own Python, ffmpeg, and Node.

> **No API key?** The app still runs. It falls back to a rule-based coach and the
> UI labels the result "Basic feedback". Get a free key at
> [console.groq.com/keys](https://console.groq.com/keys) for real AI coaching.

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

## Running without Docker

Requires **Python 3.11+**, **Node 18+**, and **ffmpeg on PATH**.

```bash
# Backend (terminal 1, from repo root)
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend (terminal 2)
cd frontend
npm install
npm run dev
```

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

## Deployment

Backend → **Render** (Docker). Frontend → **Vercel** (static).

### Backend on Render

1. Push to GitHub, then in Render: **New → Blueprint**, point at this repo.
   [`render.yaml`](render.yaml) is picked up automatically.
2. Set `GROQ_API_KEY` in the Render dashboard (it is deliberately not in the repo).
3. Set `CORS_ORIGINS` to your Vercel URL, e.g. `https://your-app.vercel.app`.

> ⚠️ **The free 512MB instance will not work.** Whisper and MediaPipe together
> need ~1.5GB and the container OOMs on the first upload. `render.yaml` requests
> the Standard plan.

### Frontend on Vercel

1. **New Project** → import the repo → set **Root Directory** to `frontend`.
2. Add env var `VITE_API_URL` = your Render URL (e.g. `https://speakcoach-api.onrender.com`).
3. Deploy. [`frontend/vercel.json`](frontend/vercel.json) handles the Vite build config.

---

## Project Structure

```
ai-public-speaking-coach-v2/
├── backend/
│   ├── Dockerfile
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
├── render.yaml                  # Backend deploy blueprint
└── requirements.txt
```

---

## Known Notes

- faster-whisper `base` is used for speed. Swap to `small` or `medium` for better accuracy.
- Gaze detection uses a nose-position heuristic (MediaPipe landmark #1). Works best with a front-facing camera at desk distance.
- Filler-word counting is substring-based, so "like" also matches inside "likely".

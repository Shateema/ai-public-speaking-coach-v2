# 🎤 AI Speaking Coach v2

An end-to-end AI-powered speaking coach that analyzes video recordings and delivers real-time feedback on speech pace, filler words, and eye contact — powered by Google Gemini, faster-whisper, and MediaPipe.

---

## Architecture

```
┌─────────────────────┐     POST /upload      ┌──────────────────────┐
│   Frontend          │ ──────────────────── ▶ │   Backend            │
│   React 19 + Vite   │                         │   FastAPI · port 8000│
│   port 5173         │ ◀ ────────────────────  │                      │
└─────────────────────┘     JSON results        └──────────┬───────────┘
                                                            │ POST /generate-feedback
                                                            ▼
                                                 ┌──────────────────────┐
                                                 │   AI Engine          │
                                                 │   FastAPI · port 8001│
                                                 │   Google Gemini API  │
                                                 └──────────────────────┘
```

### Analysis pipeline (per upload)

```
Video file
   │
   ├─▶ ffmpeg          → extract WAV audio
   ├─▶ faster-whisper  → transcribe → WPM + filler word count
   ├─▶ MediaPipe       → frame sampling → eye-contact %
   └─▶ Gemini 2.5 Flash → 3 actionable coaching bullet points
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Vanilla CSS Modules |
| Backend | FastAPI, Python 3.11, uvicorn |
| AI Engine | FastAPI microservice, Google Gemini 2.5 Flash (`google-genai`) |
| Speech | faster-whisper (base model, int8) |
| Vision | MediaPipe FaceMesh, OpenCV |
| Audio extraction | ffmpeg |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- ffmpeg installed and on PATH
- A Google Gemini API key → [Get one here](https://aistudio.google.com/apikey)

---

## Setup & Running

### 1. Clone the repo

```bash
git clone <repo-url>
cd ai-speaking-coach-v2
```

### 2. Backend

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install fastapi uvicorn python-multipart faster-whisper opencv-python mediapipe

# Run backend (from repo root)
uvicorn backend.main:app --reload
# → http://127.0.0.1:8000
```

### 3. AI Engine

```bash
# In a separate terminal, activate the same (or a dedicated) venv
venv\Scripts\activate

# Install AI engine dependencies
pip install fastapi uvicorn python-dotenv google-genai

# Set your API key
# Create ai_engine/.env with:
# GEMINI_API_KEY=your_key_here

# Run AI engine (from repo root)
cd ai_engine
uvicorn main:app --reload --port 8001
# → http://127.0.0.1:8001
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## API Reference

### Backend — `POST /upload`

Upload a video file for full analysis.

**Request:** `multipart/form-data` with field `file`

**Response:**
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
    "details": "• You speak at a good pace...\n• Reduce filler words...\n• Improve eye contact..."
  }
}
```

### AI Engine — `POST /generate-feedback`

Called internally by the backend. Accepts metrics JSON, returns Gemini-generated coaching text.

### AI Engine — `GET /health`

Returns `{ "status": "ok", "model": "gemini-2.5-flash" }`

### AI Engine — `GET /list-models`

Debug endpoint — lists all Gemini models accessible via your API key.

---

## Scoring

| Metric | Weight | Logic |
|---|---|---|
| Speaking score | 60% | Penalizes WPM outside 100–180, filler words > 5 |
| Gaze score | 40% | Tiered: ≥75% → 90, ≥50% → 70, ≥30% → 50, else 30 |
| Overall score | — | `speaking × 0.6 + gaze × 0.4` |

---

## Project Structure

```
ai-speaking-coach-v2/
├── backend/
│   ├── main.py                  # FastAPI app, /upload endpoint
│   ├── analysis/
│   │   ├── audio.py             # ffmpeg extraction, Whisper transcription, WPM/fillers
│   │   ├── visual.py            # MediaPipe gaze detection
│   │   ├── feedback.py          # Scoring functions
│   │   └── ai_coach.py          # Direct Gemini helper (standalone)
│   └── services/
│       └── ai_client.py         # HTTP client → AI engine
├── ai_engine/
│   └── main.py                  # Gemini microservice (port 8001)
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── VideoUpload.jsx         # Drag & drop upload zone
│           ├── ResultsDashboard.jsx    # Bento grid results layout
│           └── ScoreRing.jsx           # Animated SVG score ring
└── requirements.txt
```

---

## Environment Variables

Create `ai_engine/.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

---

## Known Notes

- The backend CORS is configured for `http://localhost:5173` only. Update `allow_origins` in `backend/main.py` for other environments.
- faster-whisper `base` model is used for speed. Swap to `small` or `medium` for higher transcription accuracy.
- Gaze detection uses a nose-position heuristic (MediaPipe landmark #1). Works best with a front-facing camera at desk distance.
- `gemini-1.5-flash` is deprecated — the AI engine uses `gemini-2.5-flash` (stable).

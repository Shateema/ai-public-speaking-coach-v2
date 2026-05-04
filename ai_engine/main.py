from fastapi import FastAPI, Request
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

app = FastAPI(title="AI Speaking Coach - AI Engine")

# ✅ No http_options / api_version override.
# google-genai SDK internally uses v1beta, which is where all current
# Gemini models live. Forcing "v1" causes 404 for any non-trivial model.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ gemini-2.5-flash — current stable model (gemini-1.5-flash is deprecated)
MODEL = "gemini-2.5-flash"


# --- Health check ---
@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


# --- Debug: list all models visible to this API key ---
@app.get("/list-models")
def list_models():
    """
    Enumerates models available via the current API key + SDK version.
    Use this to verify which model names are valid before hardcoding one.
    """
    try:
        models = [m.name for m in client.models.list()]
        return {"count": len(models), "models": models}
    except Exception as e:
        return {"error": str(e)}


# --- Main feedback endpoint ---
@app.post("/generate-feedback")
async def generate_feedback(request: Request):
    try:
        data = await request.json()

        prompt = f"""
You are a professional public speaking coach.
Analyze the following speaking performance data and give 3 short, 
specific, and actionable feedback points.

- Words per minute (WPM): {data.get('wpm', 'N/A')}
- Filler words used: {data.get('filler_count', 'N/A')}
- Eye contact with camera: {data.get('camera_facing_percentage', 'N/A')}%

Respond with exactly 3 bullet points. Be direct and practical.
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        return {"feedback": response.text}

    except Exception as e:
        print("❌ AI ERROR:", str(e))
        return {"feedback": "AI feedback failed.", "error": str(e)}

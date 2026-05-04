"""
ai_coach.py — Direct Gemini feedback (standalone, not used in main pipeline).
Uses google-genai SDK (google-genai>=1.0), NOT the deprecated google-generativeai.
"""
import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

# ✅ No api_version override — SDK defaults to v1beta (required for current models)
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"


def generate_ai_feedback(metrics: dict, transcript: str) -> dict:
    prompt = f"""
You are a professional public speaking coach.

Analyze the following speech metrics and transcript.

METRICS:
{json.dumps(metrics, indent=2)}

TRANSCRIPT:
{transcript[:2000]}

Return ONLY valid JSON in this exact format (no markdown, no extra text):

{{
  "summary": "2 sentence overall feedback",
  "strengths": ["...", "...", "..."],
  "weaknesses": ["...", "...", "..."],
  "action_plan": ["...", "...", "..."]
}}

Be specific, constructive, and practical.
"""

    try:
        response = _client.models.generate_content(model=MODEL, contents=prompt)
        text = response.text.strip()

        # Strip markdown code fences if model wraps JSON in them
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        return json.loads(text)

    except Exception as e:
        print("❌ AI COACH ERROR:", str(e))
        return {
            "summary": "AI feedback unavailable. Showing basic feedback.",
            "strengths": [],
            "weaknesses": [],
            "action_plan": [],
        }

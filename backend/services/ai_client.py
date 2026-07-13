"""
ai_client.py — Groq-backed coaching feedback, with a rule-based fallback.

If GROQ_API_KEY is missing or the API call fails for any reason, we fall back to
the deterministic coach in backend.analysis.feedback so the app stays useful
without a key. Callers can tell the two apart via the "source" field.
"""
import os
import logging

from dotenv import load_dotenv
from groq import Groq

from backend.analysis.feedback import generate_feedback

load_dotenv()

logger = logging.getLogger(__name__)

# Get a key at https://console.groq.com/keys
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


def _get_client():
    """Build the Groq client lazily so a missing key doesn't break import."""
    global _client

    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.startswith("PASTE_"):
            raise RuntimeError("GROQ_API_KEY is not set")
        # Explicit timeout: a stalled request should degrade to the rule-based
        # coach quickly rather than leave the user staring at a spinner.
        _client = Groq(api_key=api_key, timeout=30.0, max_retries=2)

    return _client


def is_configured():
    """True if a usable-looking key is present. Used by /health."""
    try:
        _get_client()
        return True
    except RuntimeError:
        return False


def list_models():
    return [m.id for m in _get_client().models.list().data]


def _build_prompt(metrics):
    return f"""
You are a professional public speaking coach.
Analyze the following speaking performance data and give 3 short,
specific, and actionable feedback points.

- Words per minute (WPM): {metrics.get('wpm', 'N/A')}
- Filler words used: {metrics.get('filler_count', 'N/A')}
- Eye contact with camera: {metrics.get('camera_facing_percentage', 'N/A')}%

Respond with exactly 3 bullet points. Be direct and practical.
"""


def _to_points(text):
    """Split the model's bullet-point reply into a clean list of points."""
    points = [
        line.lstrip("-*•0123456789. ").strip()
        for line in text.splitlines()
        if line.strip()
    ]
    return [p for p in points if p]


def get_ai_feedback(metrics):
    """
    Returns {"source": "ai" | "rule-based", "points": [str, ...]}.

    Never raises: any Groq failure degrades to rule-based coaching.
    """
    try:
        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": _build_prompt(metrics)}],
        )
        points = _to_points(response.choices[0].message.content)

        if not points:
            raise ValueError("Groq returned an empty response")

        return {"source": "ai", "points": points}

    except Exception as e:
        logger.warning("Groq feedback failed, using rule-based coach: %s", e)
        return {"source": "rule-based", "points": generate_feedback(metrics)}

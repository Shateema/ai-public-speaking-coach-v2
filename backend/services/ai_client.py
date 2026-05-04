import requests

def get_ai_feedback(metrics):
    try:
        response = requests.post(
            "http://127.0.0.1:8001/generate-feedback",
            json={
                "wpm": metrics["wpm"],
                "filler_count": metrics["filler_count"],
                "camera_facing_percentage": metrics["camera_facing_percentage"]
            },
            timeout=20
        )

        return response.json().get("feedback", "No feedback generated.")

    except Exception as e:
        print("AI ERROR:", str(e))
        return "AI feedback unavailable."
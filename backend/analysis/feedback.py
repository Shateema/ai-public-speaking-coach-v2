def score_speaking(wpm, filler_count):
    score = 100

    # Ideal WPM: 120–160
    if wpm < 100:
        score -= 20
    elif wpm > 180:
        score -= 20

    # Filler penalty
    if filler_count > 10:
        score -= 30
    elif filler_count > 5:
        score -= 15

    return max(score, 0)


def score_gaze(camera_facing_percentage):
    if camera_facing_percentage >= 75:
        return 90
    elif camera_facing_percentage >= 50:
        return 70
    elif camera_facing_percentage >= 30:
        return 50
    else:
        return 30


def generate_feedback(metrics):
    feedback = []

    wpm = metrics.get("wpm", 0)
    filler_count = metrics.get("filler_count", 0)
    gaze = metrics.get("camera_facing_percentage", 0)

    # --- SPEECH SPEED ---
    if wpm > 180:
        feedback.append("You are speaking too fast. Try slowing down to improve clarity.")
    elif wpm < 100:
        feedback.append("You are speaking too slowly. Add more energy and pacing.")
    else:
        feedback.append("Your speaking pace is well balanced.")

    # --- FILLERS ---
    if filler_count > 10:
        feedback.append("You use filler words frequently. Practice pausing instead of saying 'um' or 'uh'.")
    elif filler_count > 5:
        feedback.append("Reduce filler words to sound more confident.")
    else:
        feedback.append("Good control of filler words.")

    # --- EYE CONTACT ---
    if gaze < 30:
        feedback.append("Maintain better eye contact with the camera to build connection.")
    elif gaze < 60:
        feedback.append("Improve consistency in eye contact.")
    else:
        feedback.append("Good eye contact. You appear engaged and confident.")

    return feedback
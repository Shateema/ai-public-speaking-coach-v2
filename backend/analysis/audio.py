import os
import subprocess
from faster_whisper import WhisperModel

# Load model once (IMPORTANT)
model = WhisperModel("base", compute_type="int8")


def extract_audio(video_path):
    # splitext, not .replace(".mp4", ...) — the uploader accepts MOV/AVI/WEBM too,
    # and for those a naive replace would leave audio_path == video_path.
    audio_path = os.path.splitext(video_path)[0] + ".wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0 or not os.path.exists(audio_path):
        raise RuntimeError(
            f"ffmpeg failed to extract audio (exit {result.returncode}). "
            f"Is ffmpeg installed and on PATH?\n{result.stderr[-500:]}"
        )

    return audio_path


def transcribe_audio(audio_path):
    segments, info = model.transcribe(audio_path)

    transcript = " ".join([segment.text for segment in segments])
    duration = info.duration

    return transcript, duration


def analyze_speech(transcript, duration):
    words = transcript.split()
    word_count = len(words)

    wpm = 0
    if duration > 0:
        wpm = round(word_count / (duration / 60), 2)

    fillers = ["um", "uh", "like", "you know"]
    filler_count = sum(transcript.lower().count(f) for f in fillers)

    return {
        "word_count": word_count,
        "wpm": wpm,
        "filler_count": filler_count
    }
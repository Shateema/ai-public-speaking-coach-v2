import subprocess
from faster_whisper import WhisperModel

# Load model once (IMPORTANT)
model = WhisperModel("base", compute_type="int8")


def extract_audio(video_path):
    audio_path = video_path.replace(".mp4", ".wav")

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
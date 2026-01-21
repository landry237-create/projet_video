"""import subprocess
import os

def generate_subtitles(video_path: str) -> str:
    #output_srt = video_path.replace(".mp4", ".srt")
    output_srt = video_path.with_suffix(".srt")

    # Whisper tiny
    cmd = [
        "whisper",
        video_path,
        "--model", "tiny",
        "--output_format", "srt",
        "--output_dir", os.path.dirname(video_path)
    ]

    subprocess.run(cmd, check=True)
    return output_srt
"""


"""import subprocess
from pathlib import Path

def generate_subtitles(video_path: Path) -> str | None:
    output_srt = video_path.with_suffix(".srt")

    try:
        subprocess.run(
            [
                "whisper",
                str(video_path),
                "--model", "tiny",
                "--output_format", "srt",
                "--output_dir", str(video_path.parent)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return str(output_srt)

    except Exception:
        return None


"""

import subprocess
import os

from faster_whisper import WhisperModel


def generate_subtitles(audio_path: str, output_path: str, model_size="small"):
    """
    Génère des sous-titres SRT à partir d'un fichier audio WAV.
    Compatible Windows + Python 3.12 + GPU/CPU.
    """

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio introuvable : {audio_path}")

    # Charge le modèle
    model = WhisperModel(model_size, device="cpu")  # change to "cuda" si tu as GPU

    segments, info = model.transcribe(audio_path)

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(segments, start=1):
            start = format_srt_time(segment.start)
            end = format_srt_time(segment.end)
            text = segment.text.strip()

            f.write(f"{idx}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")

    return output_path


def format_srt_time(seconds: float):
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

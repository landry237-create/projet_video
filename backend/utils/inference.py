import subprocess
import os
import whisper


def transcribe_audio_to_srt(audio_path: str, output_path: str, model_size="small"):
    """
    Transcrit la parole en sous-titres (.srt) avec Whisper.
    Fonctionne parfaitement pour les vidéos FR, EN, etc.
    """

    if not os.path.exists(audio_path):
        raise FileNotFoundError("Audio introuvable pour la transcription.")

    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)

    segments = result["segments"]

    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()

            f.write(f"{i+1}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")

    return output_path


def format_timestamp(seconds: float):
    """Convertit un timestamp en format SRT."""
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

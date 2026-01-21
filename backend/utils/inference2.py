
"""

utils/inference.py

Ce module doit contenir toute la logique IA :

détection d’animaux

détection de langage

transcription / sous-titres

traitement image par image

👉 Il centralise toute l'intelligence, pour que main.py reste léger.

"""



import random


def detect_language(audio_path: str):
    """Simulation de détection de langue."""
    langues = ["fr", "en", "es", "ar", "sw"]
    return random.choice(langues)


def detect_animals(frames_dir: str):
    """Simulation de détection d'animaux dans les frames."""
    animaux = ["lion", "éléphant", "girafe", "zèbre", "aucun"]
    return random.choice(animaux)


def generate_subtitles(audio_path: str, output_path: str):
    """Génère un .srt simple pour éviter les bugs."""
    contenu = """1
00:00:00,000 --> 00:00:03,000
Analyse terminée. Sous-titre généré automatiquement.

"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(contenu)

    return output_path


def full_inference(video_path: str, work_dir: str):
    """Pipeline complet stable."""

    audio = f"{work_dir}/audio.wav"
    srt = f"{work_dir}/subtitles.srt"

    langage = detect_language(audio)
    animal = detect_animals(work_dir)
    generate_subtitles(audio, srt)

    return {
        "langue": langage,
        "animal_detecte": animal,
        "subtitles_file": srt
    }


"""

utils/video_utils.py

Ce module gère :

chargement vidéo

conversion

extraction d’images

🔥 downscale sans bug (FFmpeg)

extraction audio

découpage vidéo en frames

👉 Il s’occupe du traitement vidéo, pas du machine learning.

"""



import subprocess
import os
import cv2


def downscale_video(input_path: str, output_path: str, max_width=1280):
    """Downscale propre et sans bug via FFmpeg."""

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Fichier introuvable : {input_path}")

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"scale='min({max_width},iw)':-2",
        "-preset", "fast",
        "-y",
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if not os.path.exists(output_path):
        raise RuntimeError("Erreur : impossible de créer la vidéo réduite.")

    return output_path


def extract_audio(input_path: str, output_audio: str):
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vn", "-ac", "1", "-ar", "16000",
        "-y", output_audio
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_audio


def extract_frames(input_path: str, output_dir: str, step=20):
    """Extrait une image toutes les X frames."""

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(input_path)
    idx = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if idx % step == 0:
            cv2.imwrite(f"{output_dir}/frame_{saved}.jpg", frame)
            saved += 1

        idx += 1

    cap.release()
    return saved

import os
from pathlib import Path
from backend.app.config import settings

def get_upload_path(filename: str) -> Path:
    """Retourne le chemin de upload"""
    return settings.UPLOADS_DIR / filename

def get_work_dir(file_id: str) -> Path:
    """Retourne le répertoire de travail"""
    work_dir = settings.DATA_DIR / file_id.replace(".", "_")
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir

def clean_filename(filename: str) -> str:
    """Nettoie le nom du fichier"""
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename

def file_exists(path: Path) -> bool:
    """Vérifie si le fichier existe"""
    return path.exists() and path.is_file()

def get_file_size(path: Path) -> int:
    """Retourne la taille du fichier en bytes"""
    return path.stat().st_size if path.exists() else 0

def ensure_dirs():
    os.makedirs(settings.VIDEO_INPUT_DIR, exist_ok=True)
    os.makedirs(settings.VIDEO_OUTPUT_DIR, exist_ok=True)

def save_temp_video(video_id: str, file):
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(settings.VIDEO_INPUT_DIR, f"{video_id}{ext}")

    with open(save_path, "wb") as f:
        f.write(file.file.read())

    return save_path

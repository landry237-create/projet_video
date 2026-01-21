from pathlib import Path
from typing import ClassVar

class Settings:
    """Configuration centralisée"""
    
    # Type annotations avec ClassVar
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent.parent
    UPLOADS_DIR: ClassVar[Path] = BASE_DIR / "uploads"
    DATA_DIR: ClassVar[Path] = BASE_DIR / "backend" / "data"
    VIDEOS_STORAGE_DIR: ClassVar[Path] = DATA_DIR / "videos"
    
    # Créer les répertoires au démarrage
    def __init__(self):
        self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.VIDEOS_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Répertoires créés:")
        print(f"   UPLOADS_DIR: {self.UPLOADS_DIR}")
        print(f"   DATA_DIR: {self.DATA_DIR}")
        print(f"   VIDEOS_STORAGE_DIR: {self.VIDEOS_STORAGE_DIR}")
    
    # API Settings
    API_PREFIX: ClassVar[str] = "/api"
    API_VERSION: ClassVar[str] = "v1"
    MAX_FILE_SIZE: ClassVar[int] = 500 * 1024 * 1024  # 500 MB


# Instance unique
settings = Settings()

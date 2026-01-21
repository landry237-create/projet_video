from fastapi import APIRouter
from backend.app.config import settings
from backend.services.json_storage import JSONStorage

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Initialiser le stockage
storage = JSONStorage(str(settings.VIDEOS_STORAGE_DIR))

@router.get("/videos")
async def get_dashboard_videos():
    """Liste les vidéos pour le dashboard"""
    videos = storage.get_all_videos()
    return videos

@router.get("/stats")
async def get_stats():
    """Statistiques du dashboard"""
    return storage.get_stats()

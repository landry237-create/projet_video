"""
API FastAPI - Service de Fusion Vidéo
Reçoit les webhooks du pipeline et fusionne vidéo + sous-titres
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles

from merger import VideoMerger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video Merger Service",
    description="Fusionne vidéo downscalée + sous-titres VTT",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", "/app/uploads"))
OUTPUTS_DIR = Path(os.getenv("OUTPUTS_DIR", "/app/outputs"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Créer les répertoires
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Initialiser le merger
merger = VideoMerger(output_dir=str(OUTPUTS_DIR))

# Modèles
class MergeRequest(BaseModel):
    """Requête pour fusionner vidéo + sous-titres"""
    video_path: str
    subtitles_path: str
    output_filename: Optional[str] = None
    encoding: str = "libx264"
    preset: str = "fast"

class MergeWebhook(BaseModel):
    """Webhook depuis le pipeline (après downscale + subtitles)"""
    session_id: str
    video_id: str
    video_path: str
    subtitles_path: str
    metadata: Optional[dict] = None

# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
async def health_check():
    """Vérifier la santé du service"""
    return {
        "status": "healthy",
        "service": "video-merger",
        "timestamp": datetime.now().isoformat(),
        "uploads_dir": str(UPLOADS_DIR),
        "outputs_dir": str(OUTPUTS_DIR)
    }

# ============================================
# MERGE ENDPOINT
# ============================================
@app.post("/merge")
async def merge_video(request: MergeRequest, background_tasks: BackgroundTasks):
    """
    API pour fusionner vidéo + sous-titres
    
    Example:
    ```json
    {
        "video_path": "/data/video_downscaled.mp4",
        "subtitles_path": "/data/video.vtt",
        "output_filename": "final_video.mp4",
        "encoding": "libx264",
        "preset": "fast"
    }
    ```
    """
    try:
        merge_id = str(uuid.uuid4())[:8]
        
        # Vérifier les fichiers
        if not Path(request.video_path).exists():
            raise HTTPException(status_code=404, detail=f"Vidéo non trouvée: {request.video_path}")
        
        if not Path(request.subtitles_path).exists():
            raise HTTPException(status_code=404, detail=f"Sous-titres non trouvés: {request.subtitles_path}")
        
        # Chemin de sortie
        output_filename = request.output_filename or f"merged_{merge_id}.mp4"
        output_path = OUTPUTS_DIR / output_filename
        
        logger.info(f"🎬 Fusion lancée - ID: {merge_id}")
        
        # Exécuter la fusion
        result = merger.merge_video_with_subtitles(
            video_path=request.video_path,
            subtitles_path=request.subtitles_path,
            output_path=str(output_path),
            encoding=request.encoding,
            preset=request.preset
        )
        
        if result["status"] == "success":
            return {
                "merge_id": merge_id,
                "status": "success",
                "output_path": str(output_path),
                "file_size_mb": result.get("file_size_mb"),
                "download_url": f"/download/{output_filename}",
                "message": "Fusion réussie"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Erreur inconnue"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# WEBHOOK ENDPOINT (depuis le pipeline)
# ============================================
@app.post("/webhook/merge")
async def webhook_merge(webhook: MergeWebhook, background_tasks: BackgroundTasks):
    """
    Webhook appelé par le pipeline après génération des sous-titres
    
    Le pipeline envoie:
    - Vidéo downscalée
    - Fichier VTT générés
    - Métadonnées
    """
    try:
        logger.info(f"📨 Webhook reçu: {webhook.session_id}")
        
        # Valider les fichiers
        if not Path(webhook.video_path).exists():
            return {"status": "error", "message": f"Vidéo non trouvée: {webhook.video_path}"}
        
        if not Path(webhook.subtitles_path).exists():
            return {"status": "error", "message": f"VTT non trouvé: {webhook.subtitles_path}"}
        
        # Préparer le nom de sortie
        output_filename = f"final_{webhook.video_id}.mp4"
        output_path = OUTPUTS_DIR / output_filename
        
        # Lancer la fusion en arrière-plan
        background_tasks.add_task(
            _merge_background,
            webhook.video_path,
            webhook.subtitles_path,
            str(output_path),
            webhook.session_id,
            webhook.metadata
        )
        
        return {
            "status": "processing",
            "session_id": webhook.session_id,
            "video_id": webhook.video_id,
            "message": "Fusion en cours..."
        }
    
    except Exception as e:
        logger.error(f"❌ Erreur webhook: {e}")
        return {"status": "error", "message": str(e)}

async def _merge_background(video_path: str, subtitles_path: str, output_path: str, session_id: str, metadata: dict = None):
    """Exécute la fusion en arrière-plan"""
    try:
        logger.info(f"🔄 Fusion en arrière-plan: {session_id}")
        
        result = merger.merge_video_with_subtitles(
            video_path=video_path,
            subtitles_path=subtitles_path,
            output_path=output_path,
            encoding="libx264",
            preset="fast"
        )
        
        if result["status"] == "success":
            logger.info(f"✅ Fusion complète: {output_path}")
            # TODO: Appeler l'API de callback pour notifier le pipeline
        else:
            logger.error(f"❌ Fusion échouée: {result}")
    
    except Exception as e:
        logger.error(f"❌ Erreur fusion arrière-plan: {e}")

# ============================================
# DOWNLOAD ENDPOINT
# ============================================
@app.get("/download/{filename}")
async def download_video(filename: str):
    """Télécharger une vidéo fusionnée"""
    try:
        file_path = OUTPUTS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        
        return FileResponse(
            path=file_path,
            media_type="video/mp4",
            filename=filename
        )
    
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# STATUS ENDPOINT
# ============================================
@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Vérifier le statut d'une fusion"""
    # TODO: Implémenter avec Redis pour tracker les status
    return {
        "session_id": session_id,
        "status": "unknown",
        "message": "Redis tracking à implémenter"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8005))
    )

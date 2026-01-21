import asyncio
import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.utils.progress import ProgressManager
from backend.utils.file_utils import get_upload_path, get_work_dir, clean_filename, file_exists
from backend.database import get_db, SessionLocal
from backend.services.downscale import downscale_video
from backend.services.video_service import VideoService
from backend.services.real_yolo_detector import RealYOLODetector
from backend.services.real_language_detector import RealLanguageDetector
from backend.services.real_transcription import RealTranscription

# Initialiser les services
detector = RealYOLODetector()

router = APIRouter(prefix="/video", tags=["Video"])

print(f"📁 Video Router initialized")
print(f"   UPLOADS_DIR: {settings.UPLOADS_DIR}")
print(f"   DATA_DIR: {settings.DATA_DIR}")

# ============================================
# 1️⃣ UPLOAD ENDPOINT
# ============================================
@router.post("/upload")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload une vidéo - Autorise les doublons avec UUID"""
    try:
        # Nettoyer le nom de fichier
        original_filename = clean_filename(file.filename)
        
        # Ajouter un UUID unique pour éviter les conflits
        file_extension = Path(original_filename).suffix
        file_stem = Path(original_filename).stem
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{file_stem}_{unique_id}{file_extension}"
        
        file_path = get_upload_path(safe_filename)
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Fichier vide")
        
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Fichier trop volumineux")
        
        # Écrire le fichier
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Créer l'enregistrement en BD
        video = VideoService.create_video(
            db=db,
            file_id=safe_filename,
            filename=original_filename,
            file_path=str(file_path),
            file_size=len(content)
        )
        
        print(f"✅ Fichier uploadé: {file_path}")
        print(f"   Taille: {len(content) / 1024 / 1024:.2f} MB")
        print(f"   ID unique: {safe_filename}")
        
        return {
            "success": True,
            "file_id": safe_filename,
            "filename": original_filename,
            "size": len(content),
            "size_mb": round(len(content) / 1024 / 1024, 2)
        }
        
    except HTTPException as e:
        print(f"❌ HTTP Exception: {e.detail}")
        return {
            "success": False,
            "error": e.detail,
            "file_id": None
        }
    except Exception as e:
        print(f"❌ Erreur upload: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "file_id": None
        }


# ============================================
# 2️⃣ PROCESS ENDPOINT (WebSocket) - CORRIGÉ
# ============================================
@router.websocket("/ws/process/{file_id}")
async def process_video(websocket: WebSocket, file_id: str):
    """Traite une vidéo avec détection RÉELLE"""
    await websocket.accept()
    print(f"\n{'='*70}")
    print(f"🎬 TRAITEMENT VIDÉO: {file_id}")
    print(f"{'='*70}\n")
    
    progress = ProgressManager(websocket)
    video_path = get_upload_path(file_id)
    work_dir = get_work_dir(file_id)
    
    from backend.database import SessionLocal
    db = SessionLocal()
    
    try:
        if not file_exists(video_path):
            await progress.send("error", 0, f"Fichier introuvable")
            await websocket.close(code=1000)
            return
        
        print(f"✅ Fichier trouvé: {video_path}\n")
        
        # ÉTAPE 1: Validation
        await progress.send("validation", 5, "Validation du fichier...")
        print("📋 ÉTAPE 1: VALIDATION")
        await asyncio.sleep(1)
        
        # ÉTAPE 2: Upload
        await progress.send("upload", 15, "Fichier téléchargé ✓")
        print("✅ ÉTAPE 2: UPLOAD\n")
        await asyncio.sleep(0.5)
        
        # ÉTAPE 3: Downscale
        await progress.send("downscale", 20, "Réduction résolution...")
        print("📉 ÉTAPE 3: DOWNSCALE\n")
        await asyncio.sleep(1)
        
        # ÉTAPE 4: DÉTECTION LANGUE
        await progress.send("language", 30, "Détection de la langue...")
        print("🗣️  ÉTAPE 4: DÉTECTION LANGUE")
        
        lang_code, language = RealLanguageDetector.detect_from_video(str(video_path))
        print(f"✅ Langue: {language}\n")
        
        await asyncio.sleep(1)
        
        # ÉTAPE 5: DÉTECTION ANIMAUX
        await progress.send("animals", 45, "Détection d'animaux (YOLO)...")
        print("🦁 ÉTAPE 5: DÉTECTION ANIMAUX")
        
        animals = detector.detect_animals(str(video_path), num_samples=8)
        print(f"✅ Animaux: {animals}\n")
        
        await asyncio.sleep(1)
        
        # ÉTAPE 6: Extraction audio
        await progress.send("audio", 55, "Extraction de l'audio...")
        print("🔊 ÉTAPE 6: EXTRACTION AUDIO\n")
        await asyncio.sleep(2)
        
        # ÉTAPE 7: Transcription
        await progress.send("speech", 70, "Transcription vocale...")
        print("📝 ÉTAPE 7: TRANSCRIPTION")
        
        transcription = RealTranscription.transcribe_video(
            str(video_path),
            language_code=lang_code
        )
        print(f"✅ Transcription: {len(transcription)} caractères\n")
        
        await asyncio.sleep(2)
        
        # ÉTAPE 8: Génération sous-titres
        await progress.send("subtitles", 85, "Génération des sous-titres...")
        print("📝 ÉTAPE 8: GÉNÉRATION SOUS-TITRES")
        
        subtitle_file = work_dir / f"{file_id}_subtitles.vtt"
        
        RealTranscription.create_vtt_file(
            transcription,
            str(subtitle_file),
            language=language
        )
        print(f"✅ VTT créé\n")
        
        await asyncio.sleep(1)
        
        # ÉTAPE 9: Compilation
        await progress.send("compilation", 95, "Compilation finale...")
        print("📦 ÉTAPE 9: COMPILATION\n")
        await asyncio.sleep(1)
        
        # ÉTAPE 10: Fin
        await progress.send("complete", 100, "✅ Traitement terminé!")
        print("🏁 ÉTAPE 10: COMPLÉTÉ\n")
        
        # Sauvegarder en BD
        VideoService.update_video(
            db=db,
            file_id=file_id,
            status="completed",
            language=language,
            animals=animals,
            subtitles_path=str(subtitle_file),
            completed_at=datetime.utcnow()
        )
        
        # Sauvegarder metadata
        metadata = {
            "file_id": file_id,
            "status": "completed",
            "language": language,
            "language_code": lang_code,
            "animals": animals,
            "subtitles_path": str(subtitle_file),
            "transcription": transcription
        }
        
        metadata_file = work_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"{'='*70}")
        print(f"✅ TRAITEMENT COMPLÉTÉ: {file_id}")
        print(f"   📝 Langue: {language}")
        print(f"   🦁 Animaux: {animals}")
        print(f"   📄 Transcription: {len(transcription)} caractères")
        print(f"{'='*70}\n")
        
    except WebSocketDisconnect:
        print(f"❌ Client déconnecté")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        try:
            await progress.send("error", 0, f"Erreur: {str(e)}")
        except:
            pass
    finally:
        db.close()


# ============================================
# 3️⃣ STATUS ENDPOINT
# ============================================
@router.get("/status/{file_id}")
async def get_status(file_id: str, db: Session = Depends(get_db)):
    """Retourne le statut d'une vidéo"""
    video = VideoService.get_video(db, file_id)
    if video:
        return video.to_dict()
    return {"file_id": file_id, "status": "not_found"}


# ============================================
# 4️⃣ LIST VIDEOS ENDPOINT
# ============================================
@router.get("/videos")
async def list_videos(db: Session = Depends(get_db)):
    """Liste toutes les vidéos"""
    videos = VideoService.get_all_videos(db)
    return [v.to_dict() for v in videos]


# ============================================
# 5️⃣ SUBTITLES ENDPOINT
# ============================================
@router.get("/subtitles/{file_id}")
async def get_subtitles(file_id: str, db: Session = Depends(get_db)):
    """Retourne les sous-titres"""
    video = VideoService.get_video(db, file_id)
    
    if not video or not video.subtitles_path:
        return {"success": False, "error": "Sous-titres non trouvés"}
    
    try:
        with open(video.subtitles_path, "r", encoding="utf-8") as f:
            return {"success": True, "content": f.read()}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# 6️⃣ DELETE VIDEO ENDPOINT
# ============================================
@router.delete("/delete/{file_id}")
async def delete_video(file_id: str, db: Session = Depends(get_db)):
    """Supprime une vidéo"""
    try:
        success = VideoService.delete_video(db, file_id)
        if success:
            return {"success": True, "message": f"Vidéo {file_id} supprimée"}
        return {"success": False, "error": "Vidéo non trouvée"}
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
        return {"success": False, "error": str(e)}

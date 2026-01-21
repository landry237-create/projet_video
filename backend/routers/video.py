import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.utils.progress import ProgressManager
from backend.utils.file_utils import get_upload_path, get_work_dir, clean_filename, file_exists
from backend.services.json_storage import JSONStorage
from backend.services.video_processor import VideoProcessor
#from backend.services.yolo11_detector import YOLO11Detector
from backend.services.animal.yolo11_detector import YOLO11Detector
from backend.services.subtitles.subtitles import generate_subtitles
#from backend.services.speech_recognition_detector import SpeechRecognitionDetector
#from backend.services.downscale import DownscaleProcessor
from backend.services.downscales.downscale import DownscaleProcessor
from backend.services.language.speech_recognition_detector import SpeechRecognitionDetector

router = APIRouter(prefix="/video", tags=["Video"])

print(f"📁 Video Router initialized")
print(f"   UPLOADS_DIR: {settings.UPLOADS_DIR}")
print(f"   DATA_DIR: {settings.DATA_DIR}")

# Initialiser le stockage JSON
storage = JSONStorage(str(settings.VIDEOS_STORAGE_DIR))

# Initialiser les services
processor = VideoProcessor(temp_dir=str(settings.DATA_DIR / "temp"))
downscale = DownscaleProcessor(temp_dir=str(settings.DATA_DIR / "temp"))
yolo_detector = YOLO11Detector()

# ============================================
# 1️⃣ UPLOAD ENDPOINT
# ============================================
@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload une vidéo - Autorise les doublons avec UUID"""
    try:
        original_filename = clean_filename(file.filename)
        
        # Ajouter un UUID unique
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
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Créer l'enregistrement en JSON
        storage.create_video(
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
# 2️⃣ PROCESS ENDPOINT (WebSocket)
# ============================================
@router.websocket("/ws/process/{file_id}")
async def process_video(websocket: WebSocket, file_id: str):
    """Traite une vidéo avec YOLO11 et SpeechRecognition"""
    await websocket.accept()
    print(f"\n{'='*70}")
    print(f"🎬 TRAITEMENT VIDÉO: {file_id}")
    print(f"{'='*70}\n")
    
    progress = ProgressManager(websocket)
    video_path = get_upload_path(file_id)
    work_dir = get_work_dir(file_id)
    
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
        
        # ÉTAPE 3: DOWNSCALE (OPTIONNEL - si ça marche)
        await progress.send("downscale", 25, "Réduction résolution (640x360)...")
        print("📉 ÉTAPE 3: DOWNSCALE")
        
        downscaled_path = str(work_dir / f"downscaled_{file_id}")
        #downscale_success = processor.pod_downscale(str(video_path), downscaled_path)
        downscale_success = downscale.pod_downscale(str(video_path), downscaled_path)
        
        if downscale_success:
            print("✅ Downscale réussi")
        else:
            print("⚠️  Downscale échoué, utilisation du fichier original")
            downscaled_path = str(video_path)
        
        print()
        await asyncio.sleep(1)
        
        # ÉTAPE 4: DÉTECTION LANGUE + TRANSCRIPTION
        await progress.send("language", 40, "Détection de langue et transcription...")
        print("🎤 ÉTAPE 4: DÉTECTION LANGUE + TRANSCRIPTION")
        
        lang_code, lang_name, transcription = SpeechRecognitionDetector.detect_and_transcribe(
            str(video_path),
            str(work_dir)
        )
        
        await asyncio.sleep(1)
        
        # ÉTAPE 5: DÉTECTION ANIMAUX (YOLO11)
        await progress.send("animals", 55, "Détection d'animaux (YOLO11)...")
        print("🦁 ÉTAPE 5: DÉTECTION ANIMAUX (YOLO11)")
        
        animals = yolo_detector.detect_animals(str(video_path), num_samples=12)
        animals_str = ", ".join(animals)
        print(f"✅ Animaux détectés: {animals_str}\n")
        
        await asyncio.sleep(1)
        
        # ÉTAPE 6: GÉNÉRATION SOUS-TITRES VTT
        await progress.send("subtitles", 75, "Génération des sous-titres VTT...")
        print("📝 ÉTAPE 6: GÉNÉRATION SOUS-TITRES VTT")
        
        subtitle_path = str(work_dir / f"{file_id}.vtt")

        # genérer les sous-titres
        generate_subtitles(str(video_path), subtitle_path, model_size="small")
        
        
        # Créer le fichier VTT avec la transcription
        create_vtt_file(transcription, subtitle_path, lang_name)
        print(f"✅ Fichier VTT créé\n")
        
        await asyncio.sleep(1)
        
        # ÉTAPE 7: Compilation
        await progress.send("compilation", 90, "Compilation finale...")
        print("📦 ÉTAPE 7: COMPILATION\n")
        await asyncio.sleep(1)
        
        # ÉTAPE 8: Fin
        await progress.send("complete", 100, "✅ Traitement terminé!")
        print("🏁 ÉTAPE 8: COMPLÉTÉ\n")
        
        # Sauvegarder en JSON
        storage.update_video(
            file_id=file_id,
            status="completed",
            language=lang_name,
            animals=animals_str,
            subtitles_path=subtitle_path,
            completed_at=datetime.utcnow().isoformat()
        )
        
        # Sauvegarder metadata additionnels
        metadata_file = work_dir / "metadata.json"
        metadata = {
            "file_id": file_id,
            "status": "completed",
            "language": lang_name,
            "language_code": lang_code,
            "animals": animals,
            "subtitles_path": subtitle_path,
            "transcription": transcription
        }
        
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"{'='*70}")
        print(f"✅ TRAITEMENT COMPLÉTÉ: {file_id}")
        print(f"   📝 Langue: {lang_name}")
        print(f"   🦁 Animaux: {animals_str}")
        print(f"   📄 Transcription: {len(transcription)} caractères")
        print(f"   📽️  Sous-titres: {subtitle_path}")
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


# ============================================
# HELPER FUNCTION - Créer VTT
# ============================================
def create_vtt_file(transcription: str, output_path: str, language: str = "Français"):
    """Crée un fichier VTT avec la transcription"""
    try:
        sentences = transcription.split('. ')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            # En-tête
            f.write("00:00:00.000 --> 00:00:03.000\n")
            f.write(f"Langue: {language}\n\n")
            
            # Ajouter le texte complet divisé en segments
            current_time = 3000  # En ms
            chars_per_second = 80  # Vitesse de lecture
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                sentence = sentence.strip()
                if not sentence.endswith('.'):
                    sentence += '.'
                
                # Calculer la durée basée sur le nombre de caractères
                duration = max(2000, len(sentence) * 1000 // chars_per_second)
                
                start = current_time / 1000
                end = (current_time + duration) / 1000
                
                start_str = f"{int(start // 60):02d}:{int(start % 60):02d}.{int((start % 1) * 1000):03d}"
                end_str = f"{int(end // 60):02d}:{int(end % 60):02d}.{int((end % 1) * 1000):03d}"
                
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{sentence}\n\n")
                
                current_time += duration
        
        print(f"✅ Fichier VTT créé: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur VTT: {e}")
        return False


# ============================================
# 3️⃣ STATUS ENDPOINT
# ============================================
@router.get("/status/{file_id}")
async def get_status(file_id: str):
    """Retourne le statut d'une vidéo"""
    video = storage.get_video(file_id)
    if video:
        return video
    return {"file_id": file_id, "status": "not_found"}


# ============================================
# 4️⃣ LIST VIDEOS ENDPOINT
# ============================================
@router.get("/videos")
async def list_videos():
    """Liste toutes les vidéos"""
    videos = storage.get_all_videos()
    return videos


# ============================================
# 5️⃣ SUBTITLES ENDPOINT
# ============================================
@router.get("/subtitles/{file_id}")
async def get_subtitles(file_id: str):
    """Retourne les sous-titres VTT"""
    video = storage.get_video(file_id)
    
    if not video or not video.get('subtitles_path'):
        return {"success": False, "error": "Sous-titres non trouvés"}
    
    try:
        with open(video['subtitles_path'], "r", encoding="utf-8") as f:
            content = f.read()
            return {
                "success": True,
                "content": content,
                "file_id": file_id
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# 6️⃣ DOWNSCALED VIDEO ENDPOINT
# ============================================
@router.get("/downscaled/{file_id}")
async def get_downscaled_video(file_id: str):
    """Retourne la vidéo downscalée"""
    try:
        work_dir = get_work_dir(file_id)
        downscaled_path = work_dir / f"downscaled_{file_id}"
        
        if downscaled_path.exists():
            return FileResponse(
                path=downscaled_path,
                media_type="video/mp4",
                filename=f"downscaled_{file_id}"
            )
        
        # Si la vidéo downscalée n'existe pas, retourner la vidéo originale
        original_path = get_upload_path(file_id)
        if original_path.exists():
            return FileResponse(
                path=original_path,
                media_type="video/mp4",
                filename=file_id
            )
        
        return {"success": False, "error": "Vidéo non trouvée"}
        
    except Exception as e:
        print(f"❌ Erreur lecture vidéo: {e}")
        return {"success": False, "error": str(e)}


# ============================================
# 7️⃣ DELETE VIDEO ENDPOINT
# ============================================
@router.delete("/delete/{file_id}")
async def delete_video(file_id: str):
    """Supprime une vidéo"""
    try:
        video = storage.get_video(file_id)
        
        if not video:
            return {"success": False, "error": "Vidéo non trouvée"}
        
        # Supprimer les fichiers
        try:
            if Path(video.get('file_path')).exists():
                Path(video.get('file_path')).unlink()
            if video.get('subtitles_path') and Path(video.get('subtitles_path')).exists():
                Path(video.get('subtitles_path')).unlink()
        except Exception as e:
            print(f"⚠️  Erreur suppression fichiers: {e}")
        
        # Supprimer de l'index JSON
        success = storage.delete_video(file_id)
        
        if success:
            return {"success": True, "message": f"Vidéo {file_id} supprimée"}
        return {"success": False, "error": "Erreur suppression"}
        
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
        return {"success": False, "error": str(e)}

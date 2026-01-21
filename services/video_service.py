from sqlalchemy.orm import Session
from backend.database import VideoModel
from datetime import datetime
from pathlib import Path

class VideoService:
    @staticmethod
    def create_video(db: Session, file_id: str, filename: str, file_path: str, file_size: int):
        """Créer une nouvelle vidéo"""
        video = VideoModel(
            file_id=file_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            status="processing"
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        print(f"✅ Vidéo créée en BD: {file_id}")
        return video
    
    @staticmethod
    def update_video(db: Session, file_id: str, **kwargs):
        """Mettre à jour une vidéo"""
        video = db.query(VideoModel).filter(VideoModel.file_id == file_id).first()
        if video:
            for key, value in kwargs.items():
                if hasattr(video, key):
                    setattr(video, key, value)
            db.commit()
            db.refresh(video)
            print(f"✅ Vidéo mise à jour: {file_id}")
        return video
    
    @staticmethod
    def get_video(db: Session, file_id: str):
        """Récupérer une vidéo"""
        return db.query(VideoModel).filter(VideoModel.file_id == file_id).first()
    
    @staticmethod
    def get_all_videos(db: Session):
        """Récupérer toutes les vidéos"""
        return db.query(VideoModel).all()
    
    @staticmethod
    def delete_video(db: Session, file_id: str):
        """Supprimer une vidéo"""
        video = db.query(VideoModel).filter(VideoModel.file_id == file_id).first()
        if video:
            try:
                if Path(video.file_path).exists():
                    Path(video.file_path).unlink()
                if video.subtitles_path and Path(video.subtitles_path).exists():
                    Path(video.subtitles_path).unlink()
            except Exception as e:
                print(f"⚠️  Erreur suppression fichiers: {e}")
            
            db.delete(video)
            db.commit()
            print(f"✅ Vidéo supprimée: {file_id}")
            return True
        return False
    
    @staticmethod
    def get_stats(db: Session):
        """Récupérer les statistiques"""
        videos = db.query(VideoModel).all()
        total = len(videos)
        processed = len([v for v in videos if v.status == "completed"])
        storage = sum([v.file_size for v in videos]) / 1024 / 1024
        
        return {
            "total_videos": total,
            "processed": processed,
            "storage_used": f"{storage:.2f} MB"
        }
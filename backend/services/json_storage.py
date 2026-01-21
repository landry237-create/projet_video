import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class JSONStorage:
    """Stockage des vidéos en fichiers JSON"""
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = Path(storage_dir) or Path("data/videos")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        
        print(f"📁 JSON Storage initialized: {self.storage_dir}")
        
        # Créer l'index s'il n'existe pas
        if not self.index_file.exists():
            self._save_index([])
            print(f"✅ Index créé: {self.index_file}")
    
    def _load_index(self) -> List[Dict]:
        """Charge l'index des vidéos"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Erreur lecture index: {e}")
        return []
    
    def _save_index(self, videos: List[Dict]):
        """Sauvegarde l'index des vidéos"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde index: {e}")
    
    def _get_video_file(self, file_id: str) -> Path:
        """Retourne le chemin du fichier JSON d'une vidéo"""
        return self.storage_dir / f"{file_id}.json"
    
    def create_video(self, file_id: str, filename: str, file_path: str, file_size: int) -> Dict:
        """Crée une nouvelle vidéo"""
        try:
            video_data = {
                "id": file_id,
                "file_id": file_id,
                "filename": filename,
                "file_path": file_path,
                "status": "processing",
                "language": None,
                "animals": None,
                "subtitles_path": None,
                "file_size": file_size,
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": None
            }
            
            # Sauvegarder le fichier JSON
            video_file = self._get_video_file(file_id)
            with open(video_file, 'w', encoding='utf-8') as f:
                json.dump(video_data, f, indent=2, ensure_ascii=False)
            
            # Ajouter à l'index
            index = self._load_index()
            index.append(video_data)
            self._save_index(index)
            
            print(f"✅ Vidéo créée: {file_id}")
            return video_data
            
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            return None
    
    def get_video(self, file_id: str) -> Optional[Dict]:
        """Récupère une vidéo"""
        try:
            video_file = self._get_video_file(file_id)
            if video_file.exists():
                with open(video_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Erreur lecture vidéo: {e}")
        return None
    
    def update_video(self, file_id: str, **kwargs) -> Optional[Dict]:
        """Met à jour une vidéo"""
        try:
            video = self.get_video(file_id)
            
            if not video:
                print(f"⚠️  Vidéo non trouvée: {file_id}")
                return None
            
            # Mettre à jour les champs
            for key, value in kwargs.items():
                if key in video:
                    video[key] = value
            
            # Sauvegarder le fichier JSON
            video_file = self._get_video_file(file_id)
            with open(video_file, 'w', encoding='utf-8') as f:
                json.dump(video, f, indent=2, ensure_ascii=False)
            
            # Mettre à jour l'index
            index = self._load_index()
            for i, v in enumerate(index):
                if v['file_id'] == file_id:
                    index[i] = video
                    break
            self._save_index(index)
            
            print(f"✅ Vidéo mise à jour: {file_id}")
            return video
            
        except Exception as e:
            print(f"❌ Erreur mise à jour: {e}")
            return None
    
    def get_all_videos(self) -> List[Dict]:
        """Récupère toutes les vidéos"""
        try:
            return self._load_index()
        except Exception as e:
            print(f"❌ Erreur lecture vidéos: {e}")
            return []
    
    def delete_video(self, file_id: str) -> bool:
        """Supprime une vidéo"""
        try:
            # Supprimer le fichier JSON
            video_file = self._get_video_file(file_id)
            if video_file.exists():
                video_file.unlink()
            
            # Supprimer de l'index
            index = self._load_index()
            index = [v for v in index if v['file_id'] != file_id]
            self._save_index(index)
            
            print(f"✅ Vidéo supprimée: {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur suppression: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques"""
        try:
            videos = self.get_all_videos()
            total = len(videos)
            processed = len([v for v in videos if v.get('status') == 'completed'])
            storage = sum([v.get('file_size', 0) for v in videos]) / 1024 / 1024
            
            return {
                "total_videos": total,
                "processed": processed,
                "storage_used": f"{storage:.2f} MB"
            }
        except Exception as e:
            print(f"❌ Erreur stats: {e}")
            return {
                "total_videos": 0,
                "processed": 0,
                "storage_used": "0 MB"
            }
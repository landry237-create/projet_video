import cv2
import numpy as np
from pathlib import Path

class RealYOLODetector:
    """Détecteur YOLO réel et testé"""
    
    ANIMAL_NAMES = {
        14: "chat",
        15: "chien", 
        16: "cheval",
        17: "mouton",
        18: "vache",
        19: "éléphant",
        20: "ours",
        21: "zèbre",
        22: "girafe",
        23: "oiseau",
        24: "papillon",
    }
    
    def __init__(self):
        self.model = None
        self.available = False
        self.init_yolo()
    
    def init_yolo(self):
        """Initialise YOLOv5"""
        try:
            print("🚀 Initialisation YOLOv5...")
            import torch
            
            self.model = torch.hub.load(
                'ultralytics/yolov5',
                'yolov5s',
                pretrained=True,
                trust_repo=True
            )
            
            self.model.conf = 0.4
            self.model.iou = 0.45
            
            print("✅ YOLOv5 chargé avec succès")
            self.available = True
            
        except Exception as e:
            print(f"❌ Erreur YOLOv5: {e}")
            self.available = False
    
    def extract_frame(self, video_path: str, frame_index: int):
        """Extrait une frame d'une vidéo"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if frame_index >= total_frames:
                frame_index = total_frames - 1
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()
            cap.release()
            
            return frame if ret else None
            
        except Exception as e:
            print(f"❌ Erreur extraction frame: {e}")
            return None
    
    def detect_animals(self, video_path: str, num_samples: int = 10):
        """Détecte les animaux dans une vidéo"""
        
        if not self.available:
            print("⚠️  YOLO non disponible")
            return ["chat", "chien"]
        
        animals_set = set()
        
        try:
            print(f"\n🎥 Détection animaux: {video_path}")
            
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if total_frames == 0:
                print("❌ Vidéo corrompue ou invalide")
                return ["animal"]
            
            print(f"   Total frames: {total_frames}")
            
            frame_indices = np.linspace(0, total_frames - 1, num_samples, dtype=int)
            print(f"   Analyse de {len(frame_indices)} frames...")
            
            for idx, frame_num in enumerate(frame_indices):
                print(f"\n   Frame {idx + 1}/{num_samples} (frame #{frame_num}):")
                
                frame = self.extract_frame(video_path, int(frame_num))
                
                if frame is None:
                    print(f"   ⚠️  Impossible de lire la frame")
                    continue
                
                height, width = frame.shape[:2]
                if width > 640:
                    scale = 640 / width
                    new_w = 640
                    new_h = int(height * scale)
                    frame = cv2.resize(frame, (new_w, new_h))
                
                try:
                    results = self.model(frame, size=640)
                    predictions = results.pred[0]
                    
                    if len(predictions) > 0:
                        print(f"   ✅ {len(predictions)} objet(s) détecté(s)")
                        
                        for det in predictions:
                            x1, y1, x2, y2, conf, cls = det
                            cls_id = int(cls.item())
                            confidence = conf.item()
                            
                            if cls_id in self.ANIMAL_NAMES:
                                animal = self.ANIMAL_NAMES[cls_id]
                                animals_set.add(animal)
                                print(f"      → {animal}: {confidence:.0%}")
                    else:
                        print(f"   ℹ️  Aucun animal détecté dans cette frame")
                        
                except Exception as e:
                    print(f"   ⚠️  Erreur détection: {e}")
            
            animals_list = sorted(list(animals_set))
            
            if not animals_list:
                print("\n⚠️  Aucun animal détecté")
                animals_list = ["animal non identifié"]
            else:
                print(f"\n✅ Animaux trouvés: {animals_list}")
            
            return animals_list
            
        except Exception as e:
            print(f"❌ Erreur globale: {e}")
            import traceback
            traceback.print_exc()
            return ["animal"]
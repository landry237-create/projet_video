import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

class YOLO11Detector:
    """Détecteur d'animaux avec YOLO11"""
    
    # Classes COCO pour les animaux
    ANIMAL_CLASSES = {
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
        self.init_model()
    
    def init_model(self):
        """Initialise YOLO11"""
        try:
            print("🚀 Initialisation YOLO11...")
            self.model = YOLO('yolov8n.pt')  # YOLO11 nano
            print("✅ YOLO11 chargé avec succès")
            self.available = True
        except Exception as e:
            print(f"❌ Erreur YOLO11: {e}")
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
    
    def detect_animals(self, video_path: str, num_samples: int = 15):
        """Détecte les animaux dans une vidéo avec YOLO11"""
        
        if not self.available:
            print("⚠️  YOLO11 non disponible")
            return ["animal non identifié"]
        
        animals_set = set()
        
        try:
            print(f"\n🎥 Détection animaux YOLO11: {video_path}")
            
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            if total_frames == 0:
                print("❌ Vidéo corrompue ou invalide")
                return ["animal non identifié"]
            
            print(f"   Total frames: {total_frames}")
            
            # Échantillonner les frames
            frame_indices = np.linspace(0, total_frames - 1, num_samples, dtype=int)
            print(f"   Analyse de {len(frame_indices)} frames...\n")
            
            for idx, frame_num in enumerate(frame_indices):
                print(f"   Frame {idx + 1}/{num_samples} (frame #{frame_num}):")
                
                frame = self.extract_frame(video_path, int(frame_num))
                
                if frame is None:
                    print(f"   ⚠️  Impossible de lire la frame\n")
                    continue
                
                # Redimensionner pour vitesse
                height, width = frame.shape[:2]
                if width > 640:
                    scale = 640 / width
                    new_w = 640
                    new_h = int(height * scale)
                    frame = cv2.resize(frame, (new_w, new_h))
                
                try:
                    # Détecter avec YOLO11
                    results = self.model(frame, conf=0.45, verbose=False)
                    
                    detections = results[0].boxes
                    
                    if len(detections) > 0:
                        print(f"   ✅ {len(detections)} objet(s) détecté(s):")
                        
                        for i, box in enumerate(detections):
                            cls_id = int(box.cls[0].item())
                            conf = box.conf[0].item()
                            
                            # Classes COCO: 14-24 sont les animaux
                            if 14 <= cls_id <= 24:
                                # Noms des animaux
                                animal_names = {
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
                                
                                animal = animal_names.get(cls_id, "animal")
                                animals_set.add(animal)
                                print(f"      → {animal}: {conf:.0%}")
                    else:
                        print(f"   ℹ️  Aucun animal détecté dans cette frame")
                    
                    print()
                    
                except Exception as e:
                    print(f"   ⚠️  Erreur détection: {e}\n")
            
            animals_list = sorted(list(animals_set))
            
            if not animals_list:
                print("⚠️  Aucun animal détecté")
                animals_list = ["animal non identifié"]
            else:
                print(f"✅ Animaux trouvés: {', '.join(animals_list)}\n")
            
            return animals_list
            
        except Exception as e:
            print(f"❌ Erreur globale: {e}")
            import traceback
            traceback.print_exc()
            return ["animal"]

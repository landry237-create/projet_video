import subprocess
import os
from pathlib import Path

class VideoProcessor:
    """Traitement des vidéos"""
    
    def __init__(self, temp_dir: str = None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path("data/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ VideoProcessor initialized: {self.temp_dir}")
    
   
    def extract_audio(self, video_path: str) -> str:
        """Extrait l'audio d'une vidéo"""
        try:
            print(f"🔊 Extraction audio...")
            
            audio_path = str(self.temp_dir / "temp_audio.wav")
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                audio_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and Path(audio_path).exists():
                size_mb = Path(audio_path).stat().st_size / 1024 / 1024
                print(f"✅ Audio extrait: {size_mb:.2f}MB\n")
                return audio_path
            else:
                print(f"❌ Erreur extraction audio")
                return None
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    def pod_lang_ident(self, audio_path: str) -> str:
        """Identifie la langue"""
        # Maintenant géré par SpeechRecognitionDetector
        return "fr"
    
    def pod_transcribe_full(self, audio_path: str, language: str = "fr") -> str:
        """Transcrit l'audio"""
        # Maintenant géré par SpeechRecognitionDetector
        return "Transcription non disponible"
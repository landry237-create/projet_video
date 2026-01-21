"""import subprocess
import os
from ..app.config import settings

def downscale_video(input_path: str) -> str:
    output_path = input_path.replace(".mp4", "_downscaled.mp4")

    command = [
        settings.FFMPEG_PATH,
        "-i", input_path,
        "-vf", "scale=1280:-1",
        "-crf", "28",
        output_path
    ]

    subprocess.run(command, check=True)
    return output_path
"""
import subprocess
import os
from pathlib import Path


import subprocess
import os
from pathlib import Path

class DownscaleProcessor:
    """Traitement des vidéos"""
    
    def __init__(self, temp_dir: str = None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path("data/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ VideoProcessor initialized: {self.temp_dir}")
    
    def pod_downscale(self, input_video: str, output_video: str, width: int = 240, height: int = 160) -> bool:
        """
        Réduit la résolution d'une vidéo en gardant le ratio d'aspect
        """
        try:
            print(f"\n📉 DOWNSCALE VIDEO")
            print(f"   Input: {input_video}")
            print(f"   Output: {output_video}")
            print(f"   Résolution cible: {width}x{height}")
            
            # Vérifier que le fichier d'entrée existe
            if not Path(input_video).exists():
                print(f"❌ Fichier d'entrée inexistant: {input_video}")
                return False
            
            # Créer le répertoire de sortie
            output_dir = Path(output_video).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Commande FFmpeg pour downscale avec codec vidéo léger
            cmd = [
                'ffmpeg',
                '-i', input_video,
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                '-c:v', 'libx264',           # Codec vidéo H.264 (compatible)
                '-crf', '23',                # Qualité (0-51, défaut 28)
                '-preset', 'fast',           # Vitesse d'encodage
                '-c:a', 'aac',               # Codec audio
                '-b:a', '128k',              # Bitrate audio
                '-y',                        # Overwrite output
                output_video
            ]
            
            print(f"   🚀 Exécution FFmpeg...\n")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0 and Path(output_video).exists():
                size_mb = Path(output_video).stat().st_size / 1024 / 1024
                print(f"✅ Downscale réussi!")
                print(f"   Taille fichier: {size_mb:.2f} MB\n")
                return True
            else:
                print(f"❌ Erreur FFmpeg:")
                print(f"   {result.stderr}\n")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout downscale (> 5 minutes)")
            return False
        except FileNotFoundError:
            print(f"❌ FFmpeg non trouvé")
            print(f"   Installe FFmpeg: https://ffmpeg.org/download.html")
            return False
        except Exception as e:
            print(f"❌ Erreur downscale: {e}\n")
            import traceback
            traceback.print_exc()
            return False
    
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

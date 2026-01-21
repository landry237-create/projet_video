import subprocess
from pathlib import Path

class RealLanguageDetector:
    """Détecteur de langue via Whisper"""
    
    LANGUAGE_MAP = {
        'en': ('Anglais', 'en'),
        'fr': ('Français', 'fr'),
        'es': ('Espagnol', 'es'),
        'de': ('Allemand', 'de'),
        'it': ('Italien', 'it'),
        'pt': ('Portugais', 'pt'),
        'ru': ('Russe', 'ru'),
        'ja': ('Japonais', 'ja'),
        'zh': ('Chinois', 'zh'),
        'ar': ('Arabe', 'ar'),
        'ko': ('Coréen', 'ko'),
    }
    
    @staticmethod
    def extract_audio_ffmpeg(video_path: str, audio_output: str) -> bool:
        """Extrait l'audio avec FFmpeg"""
        try:
            print(f"🔊 Extraction audio: {video_path}")
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                audio_output
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and Path(audio_output).exists():
                size_mb = Path(audio_output).stat().st_size / 1024 / 1024
                print(f"✅ Audio extrait: {size_mb:.2f}MB")
                return True
            else:
                print(f"❌ FFmpeg error: {result.stderr[:200]}")
                return False
                
        except FileNotFoundError:
            print("❌ FFmpeg non trouvé")
            print("   Windows: choco install ffmpeg")
            print("   Linux: sudo apt-get install ffmpeg")
            return False
        except Exception as e:
            print(f"❌ Erreur extraction: {e}")
            return False
    
    @staticmethod
    def detect_language_whisper(audio_path: str) -> tuple:
        """Détecte la langue avec Whisper"""
        try:
            print(f"🎧 Analyse audio avec Whisper: {audio_path}")
            
            import whisper
            
            print("   Chargement du modèle Whisper...")
            model = whisper.load_model("base")
            
            print("   Détection de la langue...")
            result = model.detect_language(audio_path)
            
            lang_code = result
            lang_name = RealLanguageDetector.LANGUAGE_MAP.get(
                lang_code,
                (lang_code, lang_code)
            )[0]
            
            print(f"✅ Langue détectée: {lang_name} ({lang_code})")
            return lang_code, lang_name
            
        except Exception as e:
            print(f"⚠️  Erreur Whisper: {e}")
            print("   Installation: pip install openai-whisper")
            return 'fr', 'Français'
    
    @staticmethod
    def detect_from_video(video_path: str) -> tuple:
        """Détecte la langue d'une vidéo"""
        try:
            audio_path = str(Path(video_path).parent / f"{Path(video_path).stem}_temp.wav")
            
            if not RealLanguageDetector.extract_audio_ffmpeg(video_path, audio_path):
                print("⚠️  Impossible d'extraire l'audio, langue par défaut")
                return 'fr', 'Français'
            
            lang_code, lang_name = RealLanguageDetector.detect_language_whisper(audio_path)
            
            try:
                Path(audio_path).unlink()
            except:
                pass
            
            return lang_code, lang_name
            
        except Exception as e:
            print(f"❌ Erreur détection: {e}")
            return 'fr', 'Français'
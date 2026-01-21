import subprocess
from pathlib import Path

class RealTranscription:
    """Transcription vidéo en texte avec Whisper"""
    
    @staticmethod
    def extract_audio_ffmpeg(video_path: str, audio_output: str) -> bool:
        """Extrait l'audio"""
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
                print(f"✅ Audio extrait")
                return True
            return False
            
        except FileNotFoundError:
            print("❌ FFmpeg non trouvé")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    @staticmethod
    def transcribe_with_whisper(audio_path: str, language_code: str = None) -> str:
        """Transcrit l'audio avec Whisper"""
        try:
            print(f"🎤 Transcription avec Whisper...")
            
            import whisper
            
            model = whisper.load_model("base")
            
            options = {"fp16": False}
            if language_code:
                options["language"] = language_code
            
            result = model.transcribe(audio_path, **options)
            
            transcription = result["text"]
            print(f"✅ Transcription complétée: {len(transcription)} caractères")
            
            return transcription
            
        except Exception as e:
            print(f"❌ Erreur Whisper: {e}")
            return "Transcription non disponible"
    
    @staticmethod
    def transcribe_video(video_path: str, language_code: str = 'fr') -> str:
        """Transcrit une vidéo en texte"""
        try:
            audio_path = str(Path(video_path).parent / f"{Path(video_path).stem}_temp.wav")
            
            if not RealTranscription.extract_audio_ffmpeg(video_path, audio_path):
                return "Erreur extraction audio"
            
            transcription = RealTranscription.transcribe_with_whisper(audio_path, language_code)
            
            try:
                Path(audio_path).unlink()
            except:
                pass
            
            return transcription
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return "Erreur transcription"
    
    @staticmethod
    def create_vtt_file(transcription: str, output_path: str, language: str = "Français"):
        """Crée un fichier VTT avec la transcription"""
        try:
            sentences = transcription.split('. ')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                
                f.write("00:00:00.000 --> 00:00:05.000\n")
                f.write(f"Langue: {language}\n\n")
                
                current_time = 5000
                chars_per_second = 100
                
                for i, sentence in enumerate(sentences):
                    if not sentence.strip():
                        continue
                    
                    sentence = sentence.strip() + "."
                    duration = max(1000, len(sentence) * 1000 // chars_per_second)
                    
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
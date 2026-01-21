import os
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path
import subprocess

class SpeechRecognitionDetector:
    """Détection de langue et transcription avec SpeechRecognition"""
    
    LANGUAGE_MAP = {
        'fr': 'Français 🇫🇷',
        'en': 'Anglais 🇬🇧',
        'es': 'Espagnol 🇪🇸',
        'de': 'Allemand 🇩🇪',
        'it': 'Italien 🇮🇹',
        'pt': 'Portugais 🇵🇹',
        'ru': 'Russe 🇷🇺',
        'ja': 'Japonais 🇯🇵',
        'zh': 'Chinois 🇨🇳',
        'ar': 'Arabe 🇸🇦',
        'ko': 'Coréen 🇰🇷',
        'unk': 'Inconnue ❓'
    }
    
    @staticmethod
    def extract_audio(video_path: str, audio_output: str) -> bool:
        """Extrait l'audio avec FFmpeg"""
        try:
            print(f"🔊 Extraction audio...")
            
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
                print(f"✅ Audio extrait: {size_mb:.2f}MB\n")
                return True
            else:
                print(f"❌ FFmpeg error")
                return False
                
        except FileNotFoundError:
            print("❌ FFmpeg non trouvé")
            return False
        except Exception as e:
            print(f"❌ Erreur extraction: {e}")
            return False
    
    @staticmethod
    def detect_language(audio_path: str) -> str:
        """
        Détecte la langue sur un extrait audio (première 25 secondes).
        Retourne le code langue (fr, en, unk)
        """
        r = sr.Recognizer()
        langue_code = "unk"
        
        print(f"🗣️  Détection de langue...")
        
        try:
            with sr.AudioFile(audio_path) as source:
                # N'écoute que les 25 premières secondes pour la détection rapide
                audio = r.record(source, duration=25) 
            
            # Tentative de détection
            try:
                print("   Test français...")
                r.recognize_google(audio, language="fr-FR", show_all=False)
                langue_code = "fr"
                print(f"✅ Langue détectée: Français 🇫🇷\n")
            except sr.UnknownValueError:
                try:
                    print("   Test anglais...")
                    r.recognize_google(audio, language="en-US", show_all=False)
                    langue_code = "en"
                    print(f"✅ Langue détectée: Anglais 🇬🇧\n")
                except:
                    langue_code = "unk"
                    print(f"⚠️  Langue: Inconnue ❓\n")
            
            return langue_code
            
        except Exception as e:
            print(f"❌ Erreur lors de la détection de langue: {e}")
            print(f"⚠️  Utilisation du français par défaut\n")
            return "fr"
    
    @staticmethod
    def transcribe_full(audio_path: str, langue_code: str) -> str:
        """
        Transcrit l'intégralité du fichier audio en divisant l'audio en morceaux (chunks).
        Retourne le texte transcrit
        """
        if langue_code == 'unk':
            print("⚠️  Impossible de transcrire, langue Inconnue\n")
            return "Impossible de transcrire, langue Inconnue"
            
        print(f"📝 Transcription complète en cours (langue: {langue_code})...\n")
        r = sr.Recognizer()
        full_transcription = []
        
        # Définir la langue pour l'API Google
        api_lang = "fr-FR" if langue_code == "fr" else "en-US"
        
        # Division de l'audio en morceaux de 30 secondes
        chunk_size_ms = 30000 
        audio = AudioSegment.from_wav(audio_path)
        
        # Itération sur chaque morceau
        for i, start_ms in enumerate(range(0, len(audio), chunk_size_ms)):
            end_ms = start_ms + chunk_size_ms
            chunk = audio[start_ms:end_ms]
            
            # Sauvegarde temporaire du morceau
            temp_dir = str(Path(audio_path).parent)
            chunk_path = os.path.join(temp_dir, f"temp_chunk_{i}.wav")
            chunk.export(chunk_path, format="wav")
            
            # Reconnaissance vocale sur le morceau
            with sr.AudioFile(chunk_path) as source:
                audio_data = r.record(source)
                
                try:
                    text = r.recognize_google(audio_data, language=api_lang, show_all=False)
                    full_transcription.append(text)
                    print(f"   [Chunk {i+1}] ✅ Transcrit: '{text[:50]}...'")
                except sr.UnknownValueValue:
                    print(f"   [Chunk {i+1}] ⚠️  Parole non reconnue")
                    pass
                except sr.RequestError as e:
                    print(f"   [Chunk {i+1}] ❌ Erreur API: {e}")
                    pass
            
            # Nettoyage du fichier temporaire du chunk
            try:
                os.remove(chunk_path)
            except:
                pass
        
        final_text = " ".join(full_transcription)
        
        if not final_text:
            print(f"⚠️  Aucune transcription trouvée\n")
            return "Aucune parole détectée"
        
        print(f"\n✅ Transcription complète: {len(final_text)} caractères\n")
        
        return final_text
    
    @staticmethod
    def detect_and_transcribe(video_path: str, temp_dir: str):
        """Détecte la langue ET transcrit la vidéo"""
        try:
            # Extraire l'audio
            audio_path = str(Path(temp_dir) / "temp_audio.wav")
            
            print("=" * 70)
            print("🎤 ÉTAPE: LANGUE + TRANSCRIPTION (SpeechRecognition)")
            print("=" * 70)
            print()
            
            if not SpeechRecognitionDetector.extract_audio(video_path, audio_path):
                print("⚠️  Impossible d'extraire l'audio")
                return 'fr', 'Français 🇫🇷', "Erreur extraction audio"
            
            # Détecter la langue
            lang_code = SpeechRecognitionDetector.detect_language(audio_path)
            lang_name = SpeechRecognitionDetector.LANGUAGE_MAP.get(lang_code, 'Inconnue ❓')
            
            # Transcrire
            transcription = SpeechRecognitionDetector.transcribe_full(audio_path, lang_code)
            
            # Nettoyer
            try:
                Path(audio_path).unlink()
            except:
                pass
            
            print("=" * 70)
            print()
            
            return lang_code, lang_name, transcription
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return 'fr', 'Français 🇫🇷', "Erreur"

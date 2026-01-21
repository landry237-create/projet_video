import os
import json
import time
import ffmpeg 
from PIL import Image
import speech_recognition as sr 
from pydub import AudioSegment # Nouveau module utilisé pour diviser l'audio

# --- CONFIGURATION DES DOSSIERS ---
INPUT_FOLDER = "videos_input"
OUTPUT_FOLDER = "videos_output"
TEMP_AUDIO_FILE = "temp_audio.wav"

# Création automatique des dossiers si absents
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- FONCTIONS SIMULANT LES "PODS" DU PROJET ---

def pod_downscale(input_path, output_path):
    """
    Réduit la résolution et compresse la vidéo.
    """
    print(f"🎬 Traitement de {input_path}...")
    try:
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path, 
                vf='scale=640:-1', 
                vcodec='libx264',   
                crf=28,             
                loglevel="quiet"
            )
            .run(overwrite_output=True)
        )
        print(f"✅ Succès ! Vidéo réduite et compressée créée : {output_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la conversion : {e}")
        return False


def pod_lang_ident(audio_path):
    """
    Détecte la langue sur un extrait audio.
    """
    r = sr.Recognizer()
    langue_code = "unk"
    
    try:
        with sr.AudioFile(audio_path) as source:
            # N'écoute que les 25 premières secondes pour la détection rapide de la langue
            audio = r.record(source, duration=25) 
        
        # Tentative de détection
        try:
            r.recognize_google(audio, language="fr-FR", show_all=False)
            langue_code = "fr"
        except sr.UnknownValueError:
             try:
                r.recognize_google(audio, language="en-US", show_all=False)
                langue_code = "en"
             except:
                langue_code = "unk"

        langues = {"fr": "Français 🇫🇷", "en": "Anglais 🇬🇧", "unk": "Inconnue ❓"}
        print(f"+++ Analyse de la langue sur extrait... Résultat: {langues[langue_code]}")
        
        return langue_code
        
    except Exception as e:
        print(f"❌ Erreur lors de la détection de langue: {e}")
        return "unk"


def pod_transcribe_full(audio_path, langue_code):
    """
    Transcrit l'intégralité du fichier audio en divisant l'audio en morceaux (chunks).
    """
    if langue_code == 'unk':
        return "Impossible da transrcire, langue Inconnue" # Ne transcrit pas si la langue est inconnue
        
    print(f"+++ Transcription complète en cours (langue: {langue_code})...")
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
        chunk.export("temp_chunk.wav", format="wav")
        
        # Reconnaissance vocale sur le morceau
        with sr.AudioFile("temp_chunk.wav") as source:
            audio_data = r.record(source)
            
            try:
                text = r.recognize_google(audio_data, language=api_lang, show_all=False)
                full_transcription.append(text)
                print(f"   [Chunk {i+1}] Transcrit: '{text[:30]}...'")
            except sr.UnknownValueError:
                # print(f"   [Chunk {i+1}] Parole non reconnue.")
                pass
            except sr.RequestError as e:
                print(f"❌ Erreur de l'API Google sur le chunk {i+1}: {e}")
                return "Erreur API lors de la transcription complète."
    
    # Nettoyage du fichier temporaire du chunk
    if os.path.exists("temp_chunk.wav"): os.remove("temp_chunk.wav")
    
    final_text = " ".join(full_transcription)
    print("✅ Transcription complète terminée.")
    
    return final_text


def pod_animal_detect(video_path):
    """
    Analyse une image pour une détection simple (basée sur le contenu visuel).
    """
    temp_frame = "temp_frame.jpg"
    try:
        # 1. Extraction d'une image clé à 1 seconde
        (
            ffmpeg
            .input(video_path)
            .filter('select', 'gte(n, 30)') 
            .output(temp_frame, vframes=1, loglevel="quiet")
            .run(overwrite_output=True)
        )
    except Exception:
        return "Non ❌"

    # 2. Analyse de l'image 
    try:
        img = Image.open(temp_frame)
        pixels = img.getdata()
        
        green_pixels = sum(1 for r, g, b in pixels if g > 100 and g > r + 30 and g > b + 30)
        
        if green_pixels / (img.width * img.height) > 0.001:
             animal_detected = "Oui " 
        else:
             animal_detected = "Non "
        
        os.remove(temp_frame)
    except Exception:
        animal_detected = "Non "

    print(f"+++ Analyse d'image... Résultat: {animal_detected}")
    return animal_detected


def pod_subtitle(base_filename, output_folder, langue_code, transcription):
    """
    Génère un fichier de sous-titres .srt basé sur la transcription complète.
    """
    subtitle_filename = f"{base_filename}.{langue_code}.srt"
    output_path = os.path.join(output_folder, subtitle_filename)
    
    # On utilise la transcription pour le contenu du sous-titre
    if transcription:
        texte = transcription
    else:
        texte = "Pas de transcription vocale détectée."
        
    # Génération du format SubRip (.srt) - Affichage des 100 premiers caractères
    srt_content = f"1\n00:00:01,000 --> 00:00:05,000\n{texte[:100]}..." 
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        print(f"+++ Fichier de sous-titres généré : {subtitle_filename}")
        return subtitle_filename
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier SRT : {e}")
        return None




def generate_metadata(filename, langue, animal_result, subtitle_file, full_transcription, path_json):
    """
    Génère les métadonnées et inclut la transcription complète.
    """
    animal_status = animal_result.split()[0]
    
    metadata = {
        "video_name_original": filename,
        "video_name_processed": f"processed_{filename}",
        "subtitle_file": subtitle_file if subtitle_file else "None",
        "language_code": langue,
        # On stocke ici la transcription complète
        "full_transcription": full_transcription, 
        "animal_detected": animal_status,
        "processing_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "processed_locally"
    }
    
    with open(path_json, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    return metadata



# --- LE CHEF D'ORCHESTRE (MAIN) ---

def main_pipeline():
    print("🚀 Démarrage du Pipeline Vidéo Local")
    
    fichiers = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(('.mp4', '.avi', '.mov'))]
    
    if not fichiers:
        print(f" Aucune vidéo trouvée dans le dossier '{INPUT_FOLDER}'.")
        print(" Veuillez y déposer une vidéo (ex: test.mp4) et relancer.")
        return

    for video_file in fichiers:
        path_entree = os.path.join(INPUT_FOLDER, video_file)
        path_sortie = os.path.join(OUTPUT_FOLDER, f"processed_{video_file}")
        path_json = os.path.join(OUTPUT_FOLDER, f"{video_file}.json")
        base_filename = os.path.splitext(video_file)[0] 

        # ETAPE 1 : DOWNSCALE
        success = pod_downscale(path_entree, path_sortie)
        
        if success:
            
            # Prépare l'audio
            audio_path = extract_audio(path_entree)
            
            # ETAPE 2 : LANCEMENT DES ANALYSES
            full_transcription = ""
            if audio_path:
                # 2a. Détection de langue rapide
                langue_result = pod_lang_ident(audio_path)
                
                # 2b. Transcription complète si la langue est connue
                if langue_result != "unk":
                    full_transcription = pod_transcribe_full(audio_path, langue_result)
                
                # Nettoyage du fichier audio temporaire
                if os.path.exists(TEMP_AUDIO_FILE): os.remove(TEMP_AUDIO_FILE)
            else:
                langue_result = "unk"
                
            # Détection d'animal
            animal_result = pod_animal_detect(path_entree)
            
            # ETAPE 3 : SOUS-TITRES (basés sur la transcription)
            subtitle_file = pod_subtitle(base_filename, OUTPUT_FOLDER, langue_result, full_transcription)

            # ETAPE 4 : METADONNEES & STOCKAGE (inclut la transcription complète)
            metadata_dict = generate_metadata(video_file, langue_result, animal_result, subtitle_file, full_transcription, path_json)

            # AFFICHAGE DES METADONNÉES FINALES
            print("\n Affichage des métadonnées :")
            print("------------------------------------------------------------------")
            for key, value in metadata_dict.items():
                # Affiche seulement un extrait de la transcription pour la console
                display_value = str(value)
                if key == "full_transcription" and len(display_value) > 100:
                    display_value = display_value[:100] + "..."
                    
                print(f"| {key.ljust(25)} : {display_value.ljust(25)} |\n")
            print("------------------------------------------------------------------")
            
            print(f" Fichier JSON enregistré : {path_json}")
            print(" Cycle terminé pour cette vidéo.")

# --- LANCEMENT ---
main_pipeline()
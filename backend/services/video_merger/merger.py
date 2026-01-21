"""
Service de Fusion Vidéo + Sous-titres
Reçoit une vidéo downscalée et un fichier VTT, puis les fusionne avec FFmpeg
"""

import os
import ffmpeg
import webvtt
from pathlib import Path
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoMerger:
    def __init__(self, output_dir: str = "/app/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(output_dir) / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def merge_video_with_subtitles(
        self,
        video_path: str,
        subtitles_path: str,
        output_path: str,
        encoding: str = "libx264",
        preset: str = "fast"
    ) -> Dict[str, str]:
        """
        Fusionne une vidéo avec des sous-titres VTT
        
        Args:
            video_path: Chemin vers la vidéo downscalée (MP4)
            subtitles_path: Chemin vers le fichier VTT
            output_path: Chemin de sortie
            encoding: Codec vidéo (libx264, libx265, copy)
            preset: Preset FFmpeg (ultrafast, fast, medium, slow)
        
        Returns:
            Dict avec status et chemins des fichiers
        """
        try:
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Vidéo non trouvée: {video_path}")
            
            if not Path(subtitles_path).exists():
                raise FileNotFoundError(f"Sous-titres non trouvés: {subtitles_path}")
            
            # Valider le fichier VTT
            try:
                vtt = webvtt.read(subtitles_path)
                logger.info(f"✅ VTT valide: {len(vtt.captions)} sous-titres")
            except Exception as e:
                logger.warning(f"⚠️  Fichier VTT invalide: {e}")
            
            logger.info(f"🎬 Fusion en cours:")
            logger.info(f"   Vidéo: {video_path}")
            logger.info(f"   Sous-titres: {subtitles_path}")
            logger.info(f"   Sortie: {output_path}")
            
            # Stratégie 1: Utiliser FFmpeg pour intégrer les sous-titres en dur (hardsub)
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.filter(stream, 'subtitles', subtitles_path)
            stream = ffmpeg.output(
                stream, 
                output_path,
                vcodec=encoding,
                preset=preset,
                audio_codec='aac',
                q=0
            )
            
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            if not Path(output_path).exists():
                raise Exception("Erreur: fichier de sortie non créé")
            
            file_size = Path(output_path).stat().st_size / (1024 * 1024)  # MB
            
            logger.info(f"✅ Fusion terminée:")
            logger.info(f"   Fichier: {output_path}")
            logger.info(f"   Taille: {file_size:.2f} MB")
            
            return {
                "status": "success",
                "output_path": str(output_path),
                "file_size_mb": round(file_size, 2),
                "message": "Vidéo avec sous-titres générée avec succès"
            }
        
        except Exception as e:
            logger.error(f"❌ Erreur fusion: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": f"Erreur lors de la fusion: {str(e)}"
            }
    
    def merge_video_with_subtitles_soft(
        self,
        video_path: str,
        subtitles_path: str,
        output_path: str
    ) -> Dict[str, str]:
        """
        Fusionne vidéo + sous-titres en tant que piste (soft subs)
        Moins de traitement, sous-titres optionnels pour l'utilisateur
        """
        try:
            logger.info(f"🎬 Ajout sous-titres (soft):")
            
            # Copier la vidéo et ajouter la piste de sous-titres
            stream = ffmpeg.input(video_path)
            subtitle_stream = ffmpeg.input(subtitles_path)
            
            stream = ffmpeg.output(
                stream,
                subtitle_stream,
                output_path,
                c="copy",
                c_s="mov_text"
            )
            
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            file_size = Path(output_path).stat().st_size / (1024 * 1024)
            
            logger.info(f"✅ Sous-titres (soft) ajoutés: {file_size:.2f} MB")
            
            return {
                "status": "success",
                "output_path": str(output_path),
                "file_size_mb": round(file_size, 2),
                "subtitle_type": "soft",
                "message": "Sous-titres ajoutés à la vidéo"
            }
        
        except Exception as e:
            logger.error(f"❌ Erreur soft subs: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_ass_from_vtt(self, vtt_path: str, ass_path: str) -> str:
        """
        Convertit VTT en ASS pour meilleure compatibilité FFmpeg
        """
        try:
            vtt = webvtt.read(vtt_path)
            
            # Header ASS
            ass_content = """[Script Info]
Title: Generated Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,68,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            
            for caption in vtt.captions:
                start = caption.start
                end = caption.end
                text = caption.text.replace('\n', '\\N')
                ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"
            
            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write(ass_content)
            
            logger.info(f"✅ ASS créé: {ass_path}")
            return ass_path
        
        except Exception as e:
            logger.error(f"❌ Erreur conversion VTT->ASS: {e}")
            raise

if __name__ == "__main__":
    merger = VideoMerger()
    
    # Test
    result = merger.merge_video_with_subtitles(
        video_path="/app/inputs/video.mp4",
        subtitles_path="/app/inputs/subtitles.vtt",
        output_path="/app/outputs/video_with_subs.mp4"
    )
    print(result)

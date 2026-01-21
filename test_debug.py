#!/usr/bin/env python3
"""Script de débogage pour tester les dépendances"""

import subprocess
import sys
from pathlib import Path

print("🔍 VÉRIFICATION DES DÉPENDANCES\n")

# 1. FFmpeg
print("1️⃣  Vérification FFmpeg...")
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version = result.stdout.split('\n')[0]
        print(f"   ✅ FFmpeg trouvé: {version}\n")
    else:
        print(f"   ❌ FFmpeg erreur: {result.stderr}\n")
except FileNotFoundError:
    print("   ❌ FFmpeg NOT FOUND - À installer avec: choco install ffmpeg\n")
except Exception as e:
    print(f"   ❌ Erreur FFmpeg: {e}\n")

# 2. Packages Python
print("2️⃣  Vérification des packages Python...\n")

packages = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "speech_recognition",
    "pydub",
    "ultralytics",
    "opencv-python",
    "numpy"
]

for package in packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - À installer avec: pip install {package}")

print("\n3️⃣  Vérification des répertoires...\n")

dirs = [
    Path("frontend"),
    Path("backend"),
    Path("backend/data"),
    Path("backend/data/temp"),
]

for dir_path in dirs:
    if dir_path.exists():
        print(f"   ✅ {dir_path}/")
    else:
        print(f"   ❌ {dir_path}/ - À créer")
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"      ✅ Créé: {dir_path}/")

print("\n4️⃣  Test de traitement vidéo...\n")

# Test simple avec une vidéo de test
test_video = Path("uploads") / "test.mp4"
if test_video.exists():
    print(f"   ℹ️  Vidéo de test trouvée: {test_video}")
    print("   (Vous pouvez tester l'upload manuellement)")
else:
    print(f"   ℹ️  Aucune vidéo de test")

print("\n✅ Diagnostic terminé!")
print("\nCorriges les problèmes ❌ avant de lancer le serveur.\n")

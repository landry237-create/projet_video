import os
import sys
from pathlib import Path

print("=" * 60)
print("🔍 DIAGNOSTIC COMPLET")
print("=" * 60)

# 1. Vérifier les dossiers
print("\n📁 STRUCTURE DES DOSSIERS:")
print(f"CWD: {os.getcwd()}")

folders = [
    "backend",
    "backend/routers",
    "backend/utils",
    "backend/services",
    "backend/data",
    "frontend",
    "frontend/templates",
    "frontend/static",
    "uploads"
]

for folder in folders:
    exists = os.path.exists(folder)
    status = "✅" if exists else "❌"
    print(f"{status} {folder}")

# 2. Vérifier les fichiers critiques
print("\n📄 FICHIERS CRITIQUES:")
files = [
    "run_local.py",
    "backend/__init__.py",
    "backend/routers/__init__.py",
    "backend/routers/video.py",
    "backend/routers/dashboard.py",
    "backend/utils/__init__.py",
    "backend/utils/progress.py",
    "frontend/templates/upload.html",
    "frontend/templates/dashboard.html",
    "frontend/static/upload.js",
    "frontend/static/upload.css"
]

for file in files:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    size = f"({os.path.getsize(file)} bytes)" if exists else ""
    print(f"{status} {file} {size}")

# 3. Vérifier les imports
print("\n🔧 VÉRIFICATION DES IMPORTS:")
try:
    from backend.routers import video, dashboard
    print("✅ Imports routers OK")
except Exception as e:
    print(f"❌ Erreur imports: {e}")

try:
    from backend.utils.progress import ProgressManager
    print("✅ ProgressManager OK")
except Exception as e:
    print(f"❌ Erreur ProgressManager: {e}")

print("\n" + "=" * 60)
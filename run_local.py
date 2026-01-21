import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
import json

print("🔧 Initialisation du serveur...\n")

try:
    from backend.app.config import settings
    print("✅ Config chargée\n")
except Exception as e:
    print(f"❌ Erreur config: {e}")
    sys.exit(1)

try:
    from backend.routers import video, dashboard
    print("✅ Routers chargés\n")
except Exception as e:
    print(f"❌ Erreur routers: {e}")
    sys.exit(1)

app = FastAPI(
    title="VideoAI Cloud",
    version="1.0.0",
    description="Plateforme de traitement vidéo avec IA"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path("frontend/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print(f"✅ Static files montés\n")

@app.get("/")
async def index():
    html_file = Path("frontend/templates/upload.html")
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Home"}

@app.get("/upload")
async def upload_page():
    html_file = Path("frontend/templates/upload.html")
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Upload"}

@app.get("/dashboard")
async def dashboard_page():
    html_file = Path("frontend/templates/dashboard.html")
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Dashboard"}

app.include_router(video.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok", "storage": "JSON"}

@app.get("/api/videos")
async def get_videos():
    # Remplacez ceci par le chemin réel de votre fichier JSON
    json_file_path = Path("backend/data/videos.json")
    
    if json_file_path.exists():
        with open(json_file_path, "r", encoding="utf-8") as f:
            videos = json.load(f)
        return {"videos": videos}
    
    return {"videos": []}

print("=" * 70)
print("📋 ROUTES DISPONIBLES:")
print("=" * 70)
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ", ".join(route.methods)
        print(f"  {methods:15} {route.path}")
    elif hasattr(route, 'path'):
        print(f"  {'WS':15} {route.path}")

print("=" * 70)
print(f"🌐 Serveur: http://127.0.0.1:8000")
print(f"📖 Docs: http://127.0.0.1:8000/docs")
print(f"💾 Uploads: {settings.UPLOADS_DIR}")
print(f"📁 Storage JSON: {settings.VIDEOS_STORAGE_DIR}")
print("=" * 70 + "\n")

if __name__ == "__main__":
    uvicorn.run(
        "run_local:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

{
  "id": "video_abc123",
  "file_id": "video_abc123",
  "filename": "ma_video.mp4",
  "file_path": "C:/Users/power/.../uploads/ma_video_abc123.mp4",
  "status": "completed",
  "language": "Français 🇫🇷",
  "animals": "chat, oiseau",
  "subtitles_path": "C:/Users/power/.../backend/data/work/video_abc123/video_abc123.vtt",
  "file_size": 52428800,
  "created_at": "2024-01-18T15:30:45.123456",
  "completed_at": "2024-01-18T15:35:12.654321"
}
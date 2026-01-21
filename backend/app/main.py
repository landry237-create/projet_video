from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

from ..routers import video, dashboard
#from config import settings
print("Backen API only Loader")
app = FastAPI(
    title="Video Processing Platform",
    description="Pipeline de traitement vidéo (Downscale, Langue, Sous-titres, Animaux)",
    version="1.0.0"
)



"""

# CORS si frontend séparé
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes API
app.include_router(video.router, prefix="/video", tags=["Video Processing"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])


"""
# --- FRONTEND ROUTES ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dash_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})



# TEMPLATES
templates = Jinja2Templates(directory="frontend/templates")



# --- API ROUTES ---
#app.include_router(video.router, prefix="/video", tags=["Video Processing"])
app.include_router(video.router, prefix="/video", tags=["Video"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
#app.include_router(video_router, prefix="/api/video", tags=["Video"])
#app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])

# STATIC
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

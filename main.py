from backend.utils.video_utils import downscale_video, extract_audio, extract_frames
from backend.utils.inference import full_inference
import os
import uuid

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VideoAI Local Runner")


@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    work_dir = f"workspace/{session_id}"
    os.makedirs(work_dir, exist_ok=True)

    input_video = f"{work_dir}/uploaded.mp4"
    with open(input_video, "wb") as f:
        f.write(await file.read())

    downscaled = f"{work_dir}/downscaled.mp4"
    downscale_video(input_video, downscaled)

    audio_path = f"{work_dir}/audio.wav"
    extract_audio(downscaled, audio_path)

    extract_frames(downscaled, f"{work_dir}/frames")

    result = full_inference(video_path=downscaled, work_dir=work_dir)

    return {
        "status": "ok",
        "langue": result["langue"],
        "animal": result["animal_detecte"],
        "sous_titres": result["subtitles_file"]
    }

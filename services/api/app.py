import os
from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil, uuid, requests, json, time
from datetime import datetime
from utils.s3_dynamo import upload_file_to_s3, write_metadata_dynamo

app = FastAPI()
SHARED_DIR = os.getenv("SHARED_DIR", "/data")
DOWN_SCALE_URL = os.getenv("DOWN_SCALE_URL")
TRANSCRIBE_URL = os.getenv("TRANSCRIBE_URL")
SUBTITLES_URL = os.getenv("SUBTITLES_URL")
ANIMALS_URL = os.getenv("ANIMALS_URL")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE")

os.makedirs(SHARED_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # save locally
    job_id = str(uuid.uuid4())
    filename = f"{job_id}_{file.filename}"
    local_path = os.path.join(SHARED_DIR, filename)
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # call downscale
    steps = {}
    try:
        # Downscale
        r = requests.post(DOWN_SCALE_URL, json={"path": local_path})
        r.raise_for_status()
        steps['downscale'] = r.json()

        # Transcribe
        r = requests.post(TRANSCRIBE_URL, json={"path": steps['downscale']['output']})
        r.raise_for_status()
        steps['transcribe'] = r.json()

        # Subtitles (generate srt)
        r = requests.post(SUBTITLES_URL, json={"path": steps['downscale']['output'], "transcription": steps['transcribe']})
        r.raise_for_status()
        steps['subtitles'] = r.json()

        # Animals detection
        r = requests.post(ANIMALS_URL, json={"path": steps['downscale']['output']})
        r.raise_for_status()
        steps['animals'] = r.json()

        # Upload final video and subtitles to S3
        s3_video_key = f"videos/{job_id}/{os.path.basename(steps['downscale']['output'])}"
        s3_video_url = upload_file_to_s3(steps['downscale']['output'], s3_video_key)

        s3_sub_key = f"videos/{job_id}/{os.path.basename(steps['subtitles']['srt'])}"
        s3_sub_url = upload_file_to_s3(steps['subtitles']['srt'], s3_sub_key)

        # write metadata
        metadata = {
            "job_id": job_id,
            "original_filename": file.filename,
            "created_at": datetime.utcnow().isoformat(),
            "s3_video": s3_video_url,
            "s3_subtitles": s3_sub_url,
            "transcription": steps['transcribe']['transcript'],
            "animals": steps['animals']['animals']
        }
        write_metadata_dynamo(DYNAMO_TABLE, metadata)

        return {"job_id": job_id, "metadata": metadata}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()

status_streams = {}

async def event_generator(job_id: str):
    while True:
        if job_id in status_streams:
            while status_streams[job_id]:
                msg = status_streams[job_id].pop(0)
                yield f"data: {msg}\n\n"
        await asyncio.sleep(0.5)

@router.get("/video/stream_status/{job_id}")
async def stream_status(job_id: str):
    return StreamingResponse(event_generator(job_id), media_type="text/event-stream")

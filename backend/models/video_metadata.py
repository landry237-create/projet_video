from pydantic import BaseModel

class VideoMetadata(BaseModel):
    id: str
    filename: str
    language: str
    subtitles: str
    animals: list

from fastapi import HTTPException
from sqlmodel import SQLModel
from pydantic import validator, field_validator, BaseModel
import uuid


from app.videos.extractors import extract_video_id


class VideoCreateSchema(BaseModel):
    url: str
    # user_id: uuid.UUID
    channel_id:uuid.UUID
    description:str

    @validator("url")
    def validate_youtube_url(cls, url):
        video_id = extract_video_id(url)
        if video_id is None:
            # raise ValueError(f"{url} is not a valid YouTube URL")
            raise HTTPException(status_code=400, detail=f"{url} is not a valid YouTube URL")
        return url

    @field_validator("url")
    @classmethod
    def validate_url(cls, url):
        if not url.startswith("http"):
            # raise ValueError("A valid URL is required.")
            raise HTTPException(status_code=400, detail="A valid URL is required.")
        return url


    class Config:
        orm_mode = True

class VideoUpdateSchema(BaseModel):
    channel_id: uuid.UUID
    description: str

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from models.video_project import VideoStatus


class ImageSchema(BaseModel):
    id: int
    image_url: str
    order_index: int

    model_config = {"from_attributes": True}


class VideoProjectRead(BaseModel):
    id: int
    status: VideoStatus
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    images: list[ImageSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class VideoProjectCreate(BaseModel):
    pass


class VideoProjectUploadResponse(BaseModel):
    id: int
    status: VideoStatus
    message: str

    model_config = {"from_attributes": True}

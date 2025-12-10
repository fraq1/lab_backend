from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from .base import Base


class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class VideoProject(Base):
    __tablename__ = "video_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[VideoStatus] = mapped_column(
        String(20),
        default=VideoStatus.PENDING
    )
    video_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    images: Mapped[list["Image"]] = relationship(
        "Image",
        back_populates="video_project",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"VideoProject(id={self.id}, status={self.status})"

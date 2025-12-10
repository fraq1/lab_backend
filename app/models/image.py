from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    video_project_id: Mapped[int] = mapped_column(
        ForeignKey("video_projects.id", ondelete="CASCADE")
    )
    image_path: Mapped[str] = mapped_column(String(500))
    order_index: Mapped[int] = mapped_column(Integer)

    video_project: Mapped["VideoProject"] = relationship(
        "VideoProject",
        back_populates="images"
    )

    def __repr__(self):
        return f"Image(id={self.id}, order={self.order_index})"

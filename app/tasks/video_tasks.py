from pathlib import Path
from typing import Annotated
import os

os.environ["FFMPEG_BINARY"] = r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"
from moviepy import ImageClip, concatenate_videoclips
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from taskiq_broker import broker
from models.video_project import VideoProject, VideoStatus
from models.image import Image
from models import db_helper


@broker.task
async def generate_video_task(
    video_project_id: int,
    session: Annotated[
        AsyncSession,
        TaskiqDepends(db_helper.session_getter),
    ],
) -> None:
    print("TASK STARTED")
    """
    Generate video from images for a video project.

    Args:
        video_project_id: ID of the video project
        session: Database session injected by TaskiqDepends
    """
    try:
        # Update status to processing
        result = await session.execute(
            select(VideoProject).where(VideoProject.id == video_project_id)
        )
        video_project = result.scalar_one_or_none()

        if not video_project:
            return

        video_project.status = VideoStatus.PROCESSING
        await session.commit()

        # Get all images sorted by order_index
        result = await session.execute(
            select(Image)
            .where(Image.video_project_id == video_project_id)
            .order_by(Image.order_index)
        )
        images = result.scalars().all()

        if not images:
            video_project.status = VideoStatus.FAILED
            video_project.error_message = "No images found"
            await session.commit()
            return

        # Create video clips from images (each image displayed for 2 seconds)
        clips = []
        for image in images:
            image_path = Path(image.image_path)
            if not image_path.exists():
                video_project.status = VideoStatus.FAILED
                video_project.error_message = f"Image not found: {image.image_path}"
                await session.commit()
                return

            clip = ImageClip(str(image_path), duration=2)
            clips.append(clip)

        # Concatenate clips
        final_video = concatenate_videoclips(clips, method="compose")

        # Save video
        videos_dir = Path("media/videos")
        videos_dir.mkdir(parents=True, exist_ok=True)

        video_filename = f"video_{video_project_id}.mp4"
        video_path = videos_dir / video_filename

        # Write video file
        final_video.write_videofile(
            str(video_path),
            fps=24,
            codec="libx264",
            audio=False,
            preset="medium",       # скорость кодирования
            ffmpeg_params=[
                "-pix_fmt", "yuv420p",
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"  # приводим размеры к чётным
            ]
        )

        # Clean up
        final_video.close()
        for clip in clips:
            clip.close()

        # Update database
        video_project.video_path = str(video_path)
        video_project.status = VideoStatus.SUCCESS
        await session.commit()

    except Exception as e:
        # Update status to failed with error message
        video_project.status = VideoStatus.FAILED
        video_project.error_message = str(e)
        await session.commit()

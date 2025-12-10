from typing import Annotated
from pathlib import Path
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config.config import settings
from models import db_helper, VideoProject, Image
from models.video_project import VideoStatus
from schemas import VideoProjectRead, VideoProjectUploadResponse, ImageSchema
from tasks.video_tasks import generate_video_task


router = APIRouter(
    tags=["Videos"],
    prefix="/videos",
)


@router.post("", response_model=VideoProjectUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_images(
    images: list[UploadFile] = File(...),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Upload images and create video project.
    Images will be processed in background to generate video.
    """
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images provided"
        )

    # Validate image files
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    for img in images:
        file_ext = Path(img.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {img.filename}. Allowed: {allowed_extensions}"
            )

    # Create video project
    video_project = VideoProject(status=VideoStatus.PENDING)
    session.add(video_project)
    await session.commit()
    await session.refresh(video_project)

    # Save images
    images_dir = Path("media/images")
    images_dir.mkdir(parents=True, exist_ok=True)

    for idx, img_file in enumerate(images):
        # Save file
        file_ext = Path(img_file.filename).suffix
        filename = f"project_{video_project.id}_img_{idx}{file_ext}"
        file_path = images_dir / filename

        content = await img_file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Create database record
        image = Image(
            video_project_id=video_project.id,
            image_path=str(file_path),
            order_index=idx
        )
        session.add(image)

    await session.commit()

    # Kick off video generation task
    await generate_video_task.kiq(video_project.id)

    return VideoProjectUploadResponse(
        id=video_project.id,
        status=video_project.status,
        message="Images uploaded successfully. Video generation started."
    )


@router.get("", response_model=list[VideoProjectRead])
async def get_all_projects(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Get all video projects with their images and videos.
    """
    result = await session.execute(
        select(VideoProject).options(selectinload(VideoProject.images))
    )
    projects = result.scalars().all()

    # Convert to response schema with URLs
    response = []
    base_url = str(request.base_url).rstrip("/")

    for project in projects:
        images_data = [
            ImageSchema(
                id=img.id,
                image_url=f"{base_url}/media/images/{Path(img.image_path).name}",
                order_index=img.order_index
            )
            for img in sorted(project.images, key=lambda x: x.order_index)
        ]

        video_url = None
        if project.video_path:
            video_url = f"{base_url}/media/videos/{Path(project.video_path).name}"

        response.append(
            VideoProjectRead(
                id=project.id,
                status=project.status,
                video_url=video_url,
                error_message=project.error_message,
                created_at=project.created_at,
                updated_at=project.updated_at,
                images=images_data
            )
        )

    return response


@router.get("/{project_id}", response_model=VideoProjectRead)
async def get_project(
    project_id: int,
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """
    Get a single video project by ID.
    """
    result = await session.execute(
        select(VideoProject)
        .where(VideoProject.id == project_id)
        .options(selectinload(VideoProject.images))
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video project {project_id} not found"
        )

    # Convert to response schema with URLs
    base_url = str(request.base_url).rstrip("/")

    images_data = [
        ImageSchema(
            id=img.id,
            image_url=f"{base_url}/media/images/{Path(img.image_path).name}",
            order_index=img.order_index
        )
        for img in sorted(project.images, key=lambda x: x.order_index)
    ]

    video_url = None
    if project.video_path:
        video_url = f"{base_url}/media/videos/{Path(project.video_path).name}"

    return VideoProjectRead(
        id=project.id,
        status=project.status,
        video_url=video_url,
        error_message=project.error_message,
        created_at=project.created_at,
        updated_at=project.updated_at,
        images=images_data
    )

from typing import Annotated
from fastapi import APIRouter, Depends, status
from config.config import settings
from services import PostService
from queries import PostQueries
from schemas import PostRead, PostCreate

router = APIRouter(
    tags=["Posts"],
    prefix=settings.url.posts,
)


@router.get("", response_model=list[PostRead])
async def index(
    queries: Annotated[PostQueries, Depends(PostQueries)],
):
    return await queries.get_all()


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def store(
    service: Annotated[PostService, Depends(PostService)],
    post_create: PostCreate,
):
    return await service.create(post_create.title, post_create.descr)


@router.get("/{id}", response_model=PostRead)
async def show(
    queries: Annotated[PostQueries, Depends(PostQueries)],
    id: int,
):
    return await queries.get_by_id(id)


@router.put("/{id}", response_model=PostRead)
async def update(
    service: Annotated[PostService, Depends(PostService)],
    id: int,
    post_update: PostCreate,
):
    return await service.update(id, post_update.title, post_update.descr)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    service: Annotated[PostService, Depends(PostService)],
    id: int,
):
    await service.destroy(id)

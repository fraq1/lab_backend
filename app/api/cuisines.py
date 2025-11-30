from typing import Annotated
from fastapi import APIRouter, Depends, status
from config.config import settings
from services import CuisineService
from queries import CuisineQueries
from schemas import CuisineRead, CuisineCreate

router = APIRouter(
    tags=["Cuisine"],
    prefix=settings.url.cuisines,
)


@router.get("", response_model=list[CuisineRead])
async def index(
    queries: Annotated[CuisineQueries, Depends(CuisineQueries)],
):
    return await queries.get_all()


@router.post("", response_model=CuisineRead, status_code=status.HTTP_201_CREATED)
async def store(
    service: Annotated[CuisineService, Depends(CuisineService)],
    cuisine_create: CuisineCreate,
):
    return await service.create(cuisine_create.name)


@router.get("/{id}", response_model=CuisineRead)
async def show(
    queries: Annotated[CuisineQueries, Depends(CuisineQueries)],
    id: int,
):
    return await queries.get_by_id(id)


@router.put("/{id}", response_model=CuisineRead)
async def update(
    service: Annotated[CuisineService, Depends(CuisineService)],
    id: int,
    cuisine_update: CuisineCreate,
):
    return await service.update(id, cuisine_update.name)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    service: Annotated[CuisineService, Depends(CuisineService)],
    id: int,
):
    await service.destroy(id)

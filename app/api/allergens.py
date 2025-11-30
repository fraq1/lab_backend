from typing import Annotated
from fastapi import APIRouter, Depends, status
from config.config import settings
from services import AllergenService
from queries import AllergenQueries
from schemas import AllergenRead, AllergenCreate

router = APIRouter(
    tags=["Allergen"],
    prefix=settings.url.allergens,
)


@router.get("", response_model=list[AllergenRead])
async def index(
    queries: Annotated[AllergenQueries, Depends(AllergenQueries)],
):
    return await queries.get_all()


@router.post("", response_model=AllergenRead, status_code=status.HTTP_201_CREATED)
async def store(
    service: Annotated[AllergenService, Depends(AllergenService)],
    allergen_create: AllergenCreate,
):
    return await service.create(allergen_create.name)


@router.get("/{id}", response_model=AllergenRead)
async def show(
    queries: Annotated[AllergenQueries, Depends(AllergenQueries)],
    id: int,
):
    return await queries.get_by_id(id)


@router.put("/{id}", response_model=AllergenRead)
async def update(
    service: Annotated[AllergenService, Depends(AllergenService)],
    id: int,
    allergen_update: AllergenCreate,
):
    return await service.update(id, allergen_update.name)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    service: Annotated[AllergenService, Depends(AllergenService)],
    id: int,
):
    await service.destroy(id)

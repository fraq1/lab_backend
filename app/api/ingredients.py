from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from include import parse_select_fields, parse_include
from config.config import settings
from services import IngredientService
from queries import IngredientQueries
from schemas import IngredientRead, IngredientCreate

router = APIRouter(
    tags=["Ingredient"],
    prefix=settings.url.ingredients,
)


@router.get("", response_model=list[IngredientRead])
async def index(
    queries: Annotated[IngredientQueries, Depends(IngredientQueries)],
):
    return await queries.get_all()


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
async def store(
    service: Annotated[IngredientService, Depends(IngredientService)],
    ingredient_create: IngredientCreate,
):
    return await service.create(ingredient_create.name)


@router.get("/{id}", response_model=IngredientRead)
async def show(
    queries: Annotated[IngredientQueries, Depends(IngredientQueries)],
    id: int,
):
    return await queries.get_by_id(id)


@router.put("/{id}", response_model=IngredientRead)
async def update(
    service: Annotated[IngredientService, Depends(IngredientService)],
    id: int,
    ingredient_update: IngredientCreate,
):
    return await service.update(id, ingredient_update.name)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    service: Annotated[IngredientService, Depends(IngredientService)],
    id: int,
):
    await service.destroy(id)


@router.get("/{ingredient_id}/recipes")
async def recipes_by_ingredient(
    ingredient_id: int,
    include: Optional[str] = Query(
        None,
        description="cuisine,ingredients,allergens"
    ),
    select_fields: Optional[str] = Query(
        None,
        alias="select",
        description="list of base fields to select: id, title, description, cooking_time, difficulty"
    ),
    queries: Annotated[IngredientQueries, Depends(IngredientQueries)] = None,
):
    
    select_set = parse_select_fields(select_fields)

    include_set = parse_include(include)

    return await queries.get_recipes_by_ingredient(ingredient_id, include_set, select_set)
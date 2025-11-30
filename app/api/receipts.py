from typing import Annotated, Optional, List
from pydantic import model_validator
from fastapi import APIRouter, Depends, status
from models import Recipe, RecipeIngredient, User
from config.config import settings
from sqlalchemy import select, exists
from fastapi_pagination import Page
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from authentication.fastapi_users import fastapi_users
from services import RecipeService, RecipeIngredientData
from queries import RecipeQueries
from schemas import RecipeRead, RecipeCreate

router = APIRouter(
    tags=["Receipts"],
    prefix=settings.url.receipts,
)

current_active_user = fastapi_users.current_user(active=True)


class RecipeFilter(Filter):
    name__like: Optional[str] = None
    ingredient_id: Optional[str] = None
    order_by: list[str] = ["-id"]

    _parsed_ingredient_ids: Optional[List[int]] = None

    class Constants(Filter.Constants):
        model = Recipe
        ordering_fields = ["id", "difficulty"]

    @model_validator(mode="after")
    def parse_ingredient_id(self) -> "RecipeFilter":
        if self.ingredient_id is not None:
            try:
                ids = [int(x.strip()) for x in self.ingredient_id.split(",") if x.strip()]
                self._parsed_ingredient_ids = ids
            except ValueError:
                raise ValueError("ingredient_id must be a comma-separated list of integers")
        else:
            self._parsed_ingredient_ids = None
        return self

    def apply_filter(self, query):
        if self.name__like is not None:
            query = query.where(Recipe.title.ilike(f"%{self.name__like}%"))

        if self._parsed_ingredient_ids:
            ids = self._parsed_ingredient_ids
            subq = (
                select(RecipeIngredient.recipe_id)
                .where(RecipeIngredient.ingredient_id.in_(ids))
                .where(RecipeIngredient.recipe_id == Recipe.id)
            )
            query = query.where(exists(subq))

        return query


@router.get("", response_model=Page[RecipeRead])
async def index(
    recipe_filter: RecipeFilter = FilterDepends(RecipeFilter),
    queries: Annotated[RecipeQueries, Depends(RecipeQueries)] = None,
):
    return await queries.get_all_paginated(recipe_filter)


@router.get("/{id}", response_model=RecipeRead)
async def show(
    id: int,
    queries: Annotated[RecipeQueries, Depends(RecipeQueries)],
):
    return await queries.get_by_id(id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def store(
    recipe_create: RecipeCreate,
    service: Annotated[RecipeService, Depends(RecipeService)],
    queries: Annotated[RecipeQueries, Depends(RecipeQueries)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> RecipeRead:
    ingredients = [
        RecipeIngredientData(
            ingredient_id=ri.ingredient_id,
            quantity=ri.quantity,
            measurement=ri.measurement
        )
        for ri in recipe_create.ingredients
    ]

    recipe_id = await service.create(
        title=recipe_create.title,
        description=recipe_create.description,
        cooking_time=recipe_create.cooking_time,
        difficulty=recipe_create.difficulty,
        cuisine_id=recipe_create.cuisine_id,
        allergen_ids=recipe_create.allergen_ids,
        ingredients=ingredients,
        current_user=current_user
    )
    return await queries.get_by_id(recipe_id)


@router.put("/{id}")
async def update(
    id: int,
    recipe_update: RecipeCreate,
    service: Annotated[RecipeService, Depends(RecipeService)],
    queries: Annotated[RecipeQueries, Depends(RecipeQueries)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> RecipeRead:
    recipe_id = await service.update(
        recipe_id=id,
        title=recipe_update.title,
        description=recipe_update.description,
        cooking_time=recipe_update.cooking_time,
        difficulty=recipe_update.difficulty,
        cuisine_id=recipe_update.cuisine_id,
        allergen_ids=recipe_update.allergen_ids,
        current_user=current_user
    )
    return await queries.get_by_id(recipe_id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    id: int,
    service: Annotated[RecipeService, Depends(RecipeService)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    await service.destroy(id, current_user)
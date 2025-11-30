from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_helper, Ingredient, RecipeIngredient, Recipe, Allergen, Cuisine
from config.config import settings
from pydantic import BaseModel

router = APIRouter(
    tags=["Ingredient"],
    prefix=settings.url.ingredients,
)

class IngredientRead(BaseModel):
    id: int
    name: str
    quantity: float | None = None
    measurement: int | None = None

class IngredientCreate(BaseModel):
    name: str

class CuisineRead(BaseModel):
    id: int
    name: str

class AllergenRead(BaseModel):
    id: int
    name: str

class RecipeRead(BaseModel):
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    cuisine: CuisineRead | None = None
    allergens: List[AllergenRead] = []
    ingredients: List[IngredientRead] = []


@router.get("", response_model=list[IngredientRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = select(Ingredient).order_by(Ingredient.id)
    ingredients = await session.scalars(stmt)
    return ingredients.all()


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
async def store(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ingredient_create: IngredientCreate,
):
    ingredient = Ingredient(name=ingredient_create.name)
    session.add(ingredient)
    await session.commit()
    await session.refresh(ingredient)
    return ingredient


@router.get("/{id}", response_model=IngredientRead)
async def show(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingredient with id {id} not found")
    return ingredient


@router.put("/{id}", response_model=IngredientRead)
async def update(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
    ingredient_update: IngredientCreate,
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingredient with id {id} not found")
    ingredient.name = ingredient_update.name
    await session.commit()
    await session.refresh(ingredient)
    return ingredient


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingredient with id {id} not found")
    await session.delete(ingredient)
    await session.commit()


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
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)] = None,
):
    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found"
        )

    include_set = set()
    if include:
        include_set = {part.strip() for part in include.split(",") if part.strip()}
    ALLOWED_INCLUDES = {"cuisine", "ingredients", "allergens"}
    if not include_set.issubset(ALLOWED_INCLUDES):
        invalid = include_set - ALLOWED_INCLUDES
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid include values: {', '.join(invalid)}. Allowed: {', '.join(ALLOWED_INCLUDES)}"
        )

    SELECTABLE_FIELDS = {"id", "title", "description", "cooking_time", "difficulty"}
    if select_fields is not None:
        select_set = {part.strip() for part in select_fields.split(",") if part.strip()}
        invalid = select_set - SELECTABLE_FIELDS
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid fields: {', '.join(invalid)}. Allowed: {', '.join(SELECTABLE_FIELDS)}"
            )
    else:
        select_set = SELECTABLE_FIELDS

    stmt = (
        select(Recipe)
        .join(Recipe.ingredients)
        .where(RecipeIngredient.ingredient_id == ingredient_id)
        .order_by(Recipe.id)
    )

    options = []
    if "cuisine" in include_set:
        options.append(selectinload(Recipe.cuisine))
    if "allergens" in include_set:
        options.append(selectinload(Recipe.allergens))
    if "ingredients" in include_set:
        options.append(selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient))

    if options:
        stmt = stmt.options(*options)

    recipes = (await session.scalars(stmt)).all()

    result = []
    for recipe in recipes:
        base_data = {}
        if "id" in select_set:
            base_data["id"] = recipe.id
        if "title" in select_set:
            base_data["title"] = recipe.title
        if "description" in select_set:
            base_data["description"] = recipe.description
        if "cooking_time" in select_set:
            base_data["cooking_time"] = recipe.cooking_time
        if "difficulty" in select_set:
            base_data["difficulty"] = recipe.difficulty

        if "cuisine" in include_set and recipe.cuisine:
            base_data["cuisine"] = {"id": recipe.cuisine.id, "name": recipe.cuisine.name}
        if "allergens" in include_set:
            base_data["allergens"] = [{"id": a.id, "name": a.name} for a in recipe.allergens]
        if "ingredients" in include_set:
            base_data["ingredients"] = [
                {
                    "id": ri.ingredient.id,
                    "name": ri.ingredient.name,
                    "quantity": ri.quantity,
                    "measurement": ri.measurement,
                }
                for ri in recipe.ingredients
            ]

        result.append(base_data)

    return result
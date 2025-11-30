from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from models import db_helper, Recipe, Allergen, RecipeIngredient, Ingredient, Cuisine, User
from pydantic import BaseModel, ConfigDict, model_validator
from config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from authentication.fastapi_users import fastapi_users
from models.recipe import MeasurementEnum

router = APIRouter(
    tags=["Receipts"],
    prefix=settings.url.receipts,
)

current_active_user = fastapi_users.current_user(active=True)


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str | None = None
    last_name: str | None = None


class IngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ingredient_id: int
    name: str
    quantity: float
    measurement: int
    measurement_label: str

    @model_validator(mode="before")
    @classmethod
    def extract_ingredient_and_label(cls, data):
        if hasattr(data, "ingredient") and data.ingredient is not None:
            return {
                "ingredient_id": data.ingredient.id,
                "name": data.ingredient.name,
                "quantity": data.quantity,
                "measurement": data.measurement,
                "measurement_label": MeasurementEnum.get_label(data.measurement),
            }
        if isinstance(data, dict) and "ingredient" in data:
            ing = data["ingredient"]
            return {
                "ingredient_id": ing["id"],
                "name": ing["name"],
                "quantity": data["quantity"],
                "measurement": data["measurement"],
                "measurement_label": MeasurementEnum.get_label(data["measurement"]),
            }
        return data


class CuisineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class AllergenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    author: AuthorRead
    cuisine: CuisineRead | None
    allergens: List[AllergenRead]
    ingredients: List[IngredientRead]


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: float
    measurement: int


class RecipeCreate(BaseModel):
    title: str
    description: str
    cooking_time: int
    difficulty: int = 1
    cuisine_id: int
    allergen_ids: List[int] = []
    ingredients: List[RecipeIngredientCreate] = []


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
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)] = None,
):
    stmt = select(Recipe)
    stmt = recipe_filter.apply_filter(stmt)
    stmt = stmt.options(
        selectinload(Recipe.cuisine),
        selectinload(Recipe.allergens),
        selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient),
        selectinload(Recipe.author),
    )
    stmt = recipe_filter.sort(stmt)
    return await apaginate(session, stmt)


@router.get("/{id}", response_model=RecipeRead)
async def show(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author),
        )
        .where(Recipe.id == id)
    )
    recipe = await session.scalar(stmt)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {id} not found")
    return recipe


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def store(
    recipe_create: RecipeCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    cuisine = await session.get(Cuisine, recipe_create.cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail=f"Cuisine with id {recipe_create.cuisine_id} not found")

    recipe = Recipe(
        title=recipe_create.title,
        description=recipe_create.description,
        cooking_time=recipe_create.cooking_time,
        difficulty=recipe_create.difficulty,
        cuisine=cuisine,
        author_id=current_user.id,
    )

    if recipe_create.allergen_ids:
        allergens_stmt = select(Allergen).where(Allergen.id.in_(recipe_create.allergen_ids))
        allergens = (await session.scalars(allergens_stmt)).all()
        recipe.allergens = allergens

    session.add(recipe)
    await session.flush()

    for ri_data in recipe_create.ingredients:
        ingredient = await session.get(Ingredient, ri_data.ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient with id {ri_data.ingredient_id} not found")
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ri_data.ingredient_id,
            quantity=ri_data.quantity,
            measurement=ri_data.measurement,
        )
        session.add(recipe_ingredient)

    await session.commit()
    return await show(recipe.id, session)


@router.put("/{id}", response_model=RecipeRead)
async def update(
    id: int,
    recipe_update: RecipeCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients),
            selectinload(Recipe.author),
        )
        .where(Recipe.id == id)
    )
    recipe = await session.scalar(stmt)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {id} not found")

    if recipe.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recipe")

    recipe.title = recipe_update.title
    recipe.description = recipe_update.description
    recipe.cooking_time = recipe_update.cooking_time
    recipe.difficulty = recipe_update.difficulty

    if recipe_update.cuisine_id != (recipe.cuisine.id if recipe.cuisine else None):
        cuisine = await session.get(Cuisine, recipe_update.cuisine_id)
        if not cuisine:
            raise HTTPException(status_code=404, detail="Cuisine not found")
        recipe.cuisine = cuisine

    if recipe_update.allergen_ids is not None:
        allergens_stmt = select(Allergen).where(Allergen.id.in_(recipe_update.allergen_ids))
        allergens = (await session.scalars(allergens_stmt)).all()
        recipe.allergens = allergens

    await session.commit()
    await session.refresh(recipe)
    return recipe


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    recipe = await session.get(Recipe, id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {id} not found")

    if recipe.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")

    await session.delete(recipe)
    await session.commit()
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload
from models import Recipe, Allergen, RecipeIngredient, Ingredient, Cuisine
from .base import BaseRepository
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate


class RecipeRepository(BaseRepository[Recipe]):
    """Repository for Recipe database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Recipe, session)

    async def get_recipe_by_id_with_relations(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID with all its relations loaded."""
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.cuisine),
                selectinload(Recipe.allergens),
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient),
                selectinload(Recipe.author),
            )
            .where(Recipe.id == recipe_id)
        )
        result = await self.session.scalar(stmt)
        return result

    async def get_recipes_paginated(
        self,
        stmt_with_filters
    ) -> Page[Recipe]:
        """Get paginated recipes with filters applied."""
        return await apaginate(self.session, stmt_with_filters)

    async def get_allergens_by_ids(self, allergen_ids: List[int]) -> List[Allergen]:
        """Get allergens by their IDs."""
        stmt = select(Allergen).where(Allergen.id.in_(allergen_ids))
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_recipes_by_ingredient_id(
        self,
        ingredient_id: int,
        options: List = None
    ) -> List[Recipe]:
        """Get all recipes containing a specific ingredient."""
        stmt = (
            select(Recipe)
            .join(Recipe.ingredients)
            .where(RecipeIngredient.ingredient_id == ingredient_id)
            .order_by(Recipe.id)
        )

        if options:
            stmt = stmt.options(*options)

        result = await self.session.scalars(stmt)
        return result.all()

    async def delete_recipe_ingredients(self, recipe_id: int) -> None:
        """Delete all ingredients for a recipe."""
        await self.session.execute(
            select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
        )
        await self.session.flush()

    async def add_recipe_ingredient(self, recipe_ingredient: RecipeIngredient) -> None:
        """Add a recipe ingredient."""
        self.session.add(recipe_ingredient)

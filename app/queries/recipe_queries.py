from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from models import db_helper, Recipe, RecipeIngredient


class RecipeQueries:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.session = session

    def get_recipes_query(self):
        """Get base query for recipes with all relationships."""
        return select(Recipe).options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author),
        )

    async def get_all_paginated(self, recipe_filter) -> Page[Recipe]:
        """Get all recipes with filtering and pagination."""
        stmt = select(Recipe)
        stmt = recipe_filter.apply_filter(stmt)
        stmt = stmt.options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author),
        )
        stmt = recipe_filter.sort(stmt)
        return await apaginate(self.session, stmt)

    async def get_by_id(self, recipe_id: int) -> Recipe:
        """Get a single recipe by ID with all relationships."""
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
        recipe = await self.session.scalar(stmt)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe with id {recipe_id} not found"
            )
        return recipe

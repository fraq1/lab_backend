from typing import Annotated, Set, Dict, Any, List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models import db_helper, Ingredient, Recipe, RecipeIngredient


class IngredientQueries:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.session = session

    async def get_all(self) -> list[Ingredient]:
        """Get all ingredients ordered by ID."""
        stmt = select(Ingredient).order_by(Ingredient.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_id(self, ingredient_id: int) -> Ingredient:
        """Get a single ingredient by ID."""
        ingredient = await self.session.get(Ingredient, ingredient_id)
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient with id {ingredient_id} not found"
            )
        return ingredient

    async def get_recipes_by_ingredient(
        self,
        ingredient_id: int,
        include_set: Set[str],
        select_set: Set[str]
    ) -> List[Dict[str, Any]]:
        """Get recipes containing a specific ingredient with optional includes."""
        options = []
        if "cuisine" in include_set:
            options.append(selectinload(Recipe.cuisine))
        if "allergens" in include_set:
            options.append(selectinload(Recipe.allergens))
        if "ingredients" in include_set:
            options.append(selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient))

        stmt = (
            select(Recipe)
            .join(Recipe.ingredients)
            .where(RecipeIngredient.ingredient_id == ingredient_id)
            .order_by(Recipe.id)
        )

        if options:
            stmt = stmt.options(*options)

        recipes = (await self.session.scalars(stmt)).all()

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

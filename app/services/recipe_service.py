from typing import List, Optional, Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import RecipeRepository, CuisineRepository, IngredientRepository
from models import Recipe, RecipeIngredient, User, db_helper
from models.unit_of_work import UnitOfWork


class RecipeIngredientData:
    """Data class for recipe ingredient creation."""
    def __init__(self, ingredient_id: int, quantity: float, measurement: int):
        self.ingredient_id = ingredient_id
        self.quantity = quantity
        self.measurement = measurement


class RecipeService:
    """Service for Recipe business logic."""

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.uow = UnitOfWork(session)
        self.repository = RecipeRepository(session)
        self.cuisine_repository = CuisineRepository(session)
        self.ingredient_repository = IngredientRepository(session)

    async def create(
        self,
        title: str,
        description: str,
        cooking_time: int,
        difficulty: int,
        cuisine_id: int,
        allergen_ids: List[int],
        ingredients: List[RecipeIngredientData],
        current_user: User
    ) -> int:
        """Create a new recipe."""
        cuisine = await self.cuisine_repository.get_one(cuisine_id)
        if not cuisine:
            # 
            raise Exception(
                f"Cuisine with id {cuisine_id} not found"
            )

        recipe = Recipe(
            title=title,
            description=description,
            cooking_time=cooking_time,
            difficulty=difficulty,
            cuisine=cuisine,
            author_id=current_user.id,
        )

        if allergen_ids:
            allergens = await self.repository.get_allergens_by_ids(allergen_ids)
            recipe.allergens = allergens

        self.repository.session.add(recipe)
        await self.uow.flush()

        for ri_data in ingredients:
            ingredient = await self.ingredient_repository.get_one(ri_data.ingredient_id)
            if not ingredient:
                raise Exception(
                    f"Ingredient with id {ri_data.ingredient_id} not found"
                )

            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ri_data.ingredient_id,
                quantity=ri_data.quantity,
                measurement=ri_data.measurement,
            )
            await self.repository.add_recipe_ingredient(recipe_ingredient)

        await self.uow.commit()
        return recipe.id

    async def update(
        self,
        recipe_id: int,
        title: str,
        description: str,
        cooking_time: int,
        difficulty: int,
        cuisine_id: int,
        allergen_ids: Optional[List[int]],
        current_user: User
    ) -> int:
        """Update an existing recipe."""
        recipe = await self.repository.get_recipe_by_id_with_relations(recipe_id)
        if not recipe:
            raise Exception(
                f"Recipe with id {recipe_id} not found"
            )

        if recipe.author_id != current_user.id:
            raise Exception(
                "Not authorized to update this recipe"
            )

        recipe.title = title
        recipe.description = description
        recipe.cooking_time = cooking_time
        recipe.difficulty = difficulty

        if cuisine_id != (recipe.cuisine.id if recipe.cuisine else None):
            cuisine = await self.cuisine_repository.get_one(cuisine_id)
            if not cuisine:
                raise Exception(
                    "Cuisine not found"
                )
            recipe.cuisine = cuisine

        if allergen_ids is not None:
            allergens = await self.repository.get_allergens_by_ids(allergen_ids)
            recipe.allergens = allergens

        await self.uow.commit()
        await self.uow.refresh(recipe)
        return recipe.id

    async def destroy(self, recipe_id: int, current_user: User) -> None:
        """Delete a recipe."""
        recipe = await self.repository.get_one(recipe_id)
        if not recipe:
            raise Exception(
                f"Recipe with id {recipe_id} not found"
            )

        if recipe.author_id != current_user.id:
            raise Exception(
                "Not authorized to delete this recipe"
            )

        await self.repository.delete(recipe)
        await self.uow.commit()

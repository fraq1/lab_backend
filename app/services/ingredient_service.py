from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import IngredientRepository
from models import Ingredient, db_helper
from models.unit_of_work import UnitOfWork


class IngredientService:
    """Service for Ingredient business logic."""

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.uow = UnitOfWork(session)
        self.repository = IngredientRepository(session)

    async def create(self, name: str) -> Ingredient:
        """Create a new ingredient."""
        ingredient = Ingredient(name=name)
        self.repository.save(ingredient)
        await self.uow.commit()
        await self.uow.refresh(ingredient)
        return ingredient

    async def update(self, ingredient_id: int, name: str) -> Ingredient:
        """Update an existing ingredient."""
        ingredient = await self.repository.get_one(ingredient_id)
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient with id {ingredient_id} not found"
            )

        ingredient.name = name
        await self.uow.commit()
        await self.uow.refresh(ingredient)
        return ingredient

    async def destroy(self, ingredient_id: int) -> None:
        """Delete an ingredient."""
        ingredient = await self.repository.get_one(ingredient_id)
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredient with id {ingredient_id} not found"
            )
        await self.repository.delete(ingredient)
        await self.uow.commit()

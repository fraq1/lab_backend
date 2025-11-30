from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models import Ingredient
from .base import BaseRepository


class IngredientRepository(BaseRepository[Ingredient]):
    """Repository for Ingredient database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Ingredient, session)

    async def get_all_ingredients(self) -> List[Ingredient]:
        """Get all ingredients ordered by ID."""
        return await self.get_all(order_by=Ingredient.id)

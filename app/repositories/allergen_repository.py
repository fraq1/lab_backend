from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models import Allergen
from .base import BaseRepository


class AllergenRepository(BaseRepository[Allergen]):
    """Repository for Allergen database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Allergen, session)

    async def get_all_allergens(self) -> List[Allergen]:
        """Get all allergens ordered by ID."""
        return await self.get_all(order_by=Allergen.id)

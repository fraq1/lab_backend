from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models import Cuisine
from .base import BaseRepository


class CuisineRepository(BaseRepository[Cuisine]):
    """Repository for Cuisine database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Cuisine, session)

    async def get_all_cuisines(self) -> List[Cuisine]:
        """Get all cuisines ordered by ID."""
        return await self.get_all(order_by=Cuisine.id)

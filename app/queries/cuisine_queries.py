from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import db_helper, Cuisine


class CuisineQueries:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.session = session

    async def get_all(self) -> list[Cuisine]:
        """Get all cuisines ordered by ID."""
        stmt = select(Cuisine).order_by(Cuisine.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_id(self, cuisine_id: int) -> Cuisine:
        """Get a single cuisine by ID."""
        cuisine = await self.session.get(Cuisine, cuisine_id)
        if not cuisine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuisine with id {cuisine_id} not found"
            )
        return cuisine

from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import db_helper, Allergen


class AllergenQueries:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.session = session

    async def get_all(self) -> list[Allergen]:
        """Get all allergens ordered by ID."""
        stmt = select(Allergen).order_by(Allergen.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_id(self, allergen_id: int) -> Allergen:
        """Get a single allergen by ID."""
        allergen = await self.session.get(Allergen, allergen_id)
        if not allergen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergen with id {allergen_id} not found"
            )
        return allergen

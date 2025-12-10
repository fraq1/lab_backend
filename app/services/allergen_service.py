from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import AllergenRepository
from models import Allergen, db_helper
from models.unit_of_work import UnitOfWork


class AllergenService:
    """Service for Allergen business logic."""

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.uow = UnitOfWork(session)
        self.repository = AllergenRepository(session)

    async def create(self, name: str) -> Allergen:
        """Create a new allergen."""
        allergen = Allergen(name=name)
        self.repository.save(allergen)
        await self.uow.commit()
        await self.uow.refresh(allergen)
        return allergen

    async def update(self, allergen_id: int, name: str) -> Allergen:
        """Update an existing allergen."""
        allergen = await self.repository.get_one(allergen_id)
        if not allergen:
            raise Exception(
                f"Allergen with id {allergen_id} not found"
            )

        allergen.name = name
        await self.uow.commit()
        await self.uow.refresh(allergen)
        return allergen

    async def destroy(self, allergen_id: int) -> None:
        """Delete an allergen."""
        allergen = await self.repository.get_one(allergen_id)
        if not allergen:
            raise Exception(
                f"Allergen with id {allergen_id} not found"
            )
        await self.repository.delete(allergen)
        await self.uow.commit()

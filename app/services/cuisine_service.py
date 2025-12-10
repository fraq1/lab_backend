from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import CuisineRepository
from models import Cuisine, db_helper
from models.unit_of_work import UnitOfWork


class CuisineService:
    """Service for Cuisine business logic."""

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.uow = UnitOfWork(session)
        self.repository = CuisineRepository(session)

    async def create(self, name: str) -> Cuisine:
        """Create a new cuisine."""
        cuisine = Cuisine(name=name)
        self.repository.save(cuisine)
        await self.uow.commit()
        await self.uow.refresh(cuisine)
        return cuisine

    async def update(self, cuisine_id: int, name: str) -> Cuisine:
        """Update an existing cuisine."""
        cuisine = await self.repository.get_one(cuisine_id)
        if not cuisine:
            raise Exception(
                f"Cuisine with id {cuisine_id} not found"
            )

        cuisine.name = name
        await self.uow.commit()
        await self.uow.refresh(cuisine)
        return cuisine

    async def destroy(self, cuisine_id: int) -> None:
        """Delete a cuisine."""
        cuisine = await self.repository.get_one(cuisine_id)
        if not cuisine:
            raise Exception(
                f"Cuisine with id {cuisine_id} not found"
            )
        await self.repository.delete(cuisine)
        await self.uow.commit()

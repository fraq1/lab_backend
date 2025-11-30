from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations for database access."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_all(self, order_by: Any = None) -> List[ModelType]:
        """Get all records."""
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_one(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        return await self.session.get(self.model, id)

    def save(self, entity: ModelType) -> None:
        """Add entity to session (does not commit)."""
        self.session.add(entity)

    async def delete(self, entity: ModelType) -> None:
        """Delete a record (does not commit)."""
        await self.session.delete(entity)

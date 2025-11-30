from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """Unit of Work pattern for transaction management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self.session.rollback()

    async def flush(self) -> None:
        """Flush pending changes to the database."""
        await self.session.flush()

    async def refresh(self, entity) -> None:
        """Refresh an entity from the database."""
        await self.session.refresh(entity)

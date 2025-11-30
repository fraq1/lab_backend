from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models import Post
from .base import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Repository for Post database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get_all_posts(self) -> List[Post]:
        """Get all posts ordered by ID."""
        return await self.get_all(order_by=Post.id)

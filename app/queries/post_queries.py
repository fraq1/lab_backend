from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import db_helper, Post


class PostQueries:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.session = session

    async def get_all(self) -> list[Post]:
        """Get all posts ordered by ID."""
        stmt = select(Post).order_by(Post.id)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_id(self, post_id: int) -> Post:
        """Get a single post by ID."""
        post = await self.session.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id {post_id} not found"
            )
        return post

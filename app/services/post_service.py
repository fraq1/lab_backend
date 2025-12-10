from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import PostRepository
from models import Post, db_helper
from models.unit_of_work import UnitOfWork


class PostService:
    """Service for Post business logic."""

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ):
        self.uow = UnitOfWork(session)
        self.repository = PostRepository(session)

    async def create(self, title: str, descr: str) -> Post:
        """Create a new post."""
        post = Post(title=title, descr=descr)
        self.repository.save(post)
        await self.uow.commit()
        await self.uow.refresh(post)
        return post

    async def update(self, post_id: int, title: str, descr: str) -> Post:
        """Update an existing post."""
        post = await self.repository.get_one(post_id)
        if not post:
            raise Exception(
                f"Post with id {post_id} not found"
            )

        post.title = title
        post.descr = descr
        await self.uow.commit()
        await self.uow.refresh(post)
        return post

    async def destroy(self, post_id: int) -> None:
        """Delete a post."""
        post = await self.repository.get_one(post_id)
        if not post:
            raise Exception(
                f"Post with id {post_id} not found"
            )
        await self.repository.delete(post)
        await self.uow.commit()

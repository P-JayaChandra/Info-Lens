import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Look up user by normalized lowercase email address."""
        stmt = (
            select(User)
            .where(User.email == email.lower().strip())
            .where(User.is_deleted.is_(False))
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_with_memberships(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> Optional[User]:
        """Fetch user with eager loaded organization memberships."""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .where(User.is_deleted.is_(False))
            .options(selectinload(User.memberships))
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def update_last_login(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        """Update last login timestamp."""
        user = await self.get(session, user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            session.add(user)
            await session.flush()

    async def list_active(
        self, session: AsyncSession, skip: int = 0, limit: int = 50
    ) -> Sequence[User]:
        """List active users."""
        stmt = (
            select(User)
            .where(User.is_active.is_(True))
            .where(User.is_deleted.is_(False))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()


user_repository = UserRepository()

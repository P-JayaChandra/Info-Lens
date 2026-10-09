import uuid
from datetime import datetime, timezone
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import APIKey
from app.repositories.base import BaseRepository
from app.schemas.api_key import APIKeyCreate


class APIKeyRepository(BaseRepository[APIKey, APIKeyCreate, APIKeyCreate]):
    def __init__(self):
        super().__init__(APIKey)

    async def get_by_prefix(self, session: AsyncSession, prefix: str) -> Sequence[APIKey]:
        """Look up active API keys by key prefix."""
        stmt = (
            select(APIKey)
            .where(APIKey.key_prefix == prefix)
            .where(APIKey.is_active.is_(True))
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_user(
        self, session: AsyncSession, user_id: uuid.UUID
    ) -> Sequence[APIKey]:
        """List keys owned by a specific user."""
        stmt = (
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .where(APIKey.is_active.is_(True))
            .order_by(APIKey.created_at.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_last_used(self, session: AsyncSession, key_id: uuid.UUID) -> None:
        """Mark API key last used time."""
        key = await self.get(session, key_id)
        if key:
            key.last_used_at = datetime.now(timezone.utc)
            session.add(key)
            await session.flush()


api_key_repository = APIKeyRepository()

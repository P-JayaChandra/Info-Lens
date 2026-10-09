import uuid
from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base repository providing CRUD and query operations for SQLAlchemy 2.0 models.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Union[uuid.UUID, str]) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        if isinstance(id, str):
            try:
                id = uuid.UUID(id)
            except ValueError:
                return None

        stmt = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))

        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None,
    ) -> Sequence[ModelType]:
        """Fetch multiple records with pagination and ordering."""
        stmt = select(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))

        if order_by is not None:
            stmt = stmt.order_by(order_by)
        elif hasattr(self.model, "created_at"):
            stmt = stmt.order_by(self.model.created_at.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def count(self, session: AsyncSession) -> int:
        """Count total non-deleted records."""
        stmt = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def create(
        self, session: AsyncSession, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Create and persist a new record."""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)

        db_obj = self.model(**create_data)
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update an existing record with partial fields."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def remove(self, session: AsyncSession, id: Union[uuid.UUID, str]) -> Optional[ModelType]:
        """Hard delete a record from persistence."""
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            await session.flush()
        return obj

    async def soft_delete(self, session: AsyncSession, id: Union[uuid.UUID, str]) -> Optional[ModelType]:
        """Soft delete a record by setting is_deleted=True."""
        obj = await self.get(session, id)
        if obj and hasattr(obj, "soft_delete"):
            obj.soft_delete()
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
        return obj

    async def exists(self, session: AsyncSession, id: Union[uuid.UUID, str]) -> bool:
        """Check if record exists without loading full object."""
        if isinstance(id, str):
            try:
                id = uuid.UUID(id)
            except ValueError:
                return False

        stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))
        result = await session.execute(stmt)
        return (result.scalar() or 0) > 0

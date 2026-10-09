import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy database models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Default table name is lowercase class name if not specified
        return cls.__name__.lower()

    def __init__(self, **kwargs: Any) -> None:
        # Ensure default values are populated on direct Python instantiation
        if hasattr(self.__class__, "id") and "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()
        if hasattr(self.__class__, "is_deleted") and "is_deleted" not in kwargs:
            kwargs["is_deleted"] = False
        if hasattr(self.__class__, "created_at") and "created_at" not in kwargs:
            kwargs["created_at"] = utc_now()
        if hasattr(self.__class__, "updated_at") and "updated_at" not in kwargs:
            kwargs["updated_at"] = utc_now()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def as_dict(self) -> Dict[str, Any]:
        """Convert model attributes to a standard dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        attrs = []
        for key in ["id", "name", "email", "status", "title"]:
            if hasattr(self, key):
                attrs.append(f"{key}={getattr(self, key)!r}")
        return f"<{self.__class__.__name__}({', '.join(attrs)})>"


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID primary key for models."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        sort_order=-100,
    )


class TimestampMixin:
    """Mixin providing UTC created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin providing soft deletion capabilities."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = utc_now()

    def restore(self) -> None:
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """Mixin tracking creator and updater identifiers."""

    created_by_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        default=None,
    )
    updated_by_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        default=None,
    )

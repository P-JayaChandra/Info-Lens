import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import (
    AuditMixin,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class SampleModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "sample_test_models"

    name: Mapped[str] = mapped_column(String(100), nullable=False)


def test_base_model_instantiation():
    sample = SampleModel(name="Test Item")
    # UUID should be set
    assert isinstance(sample.id, uuid.UUID)
    assert sample.name == "Test Item"
    assert sample.is_deleted is False
    assert sample.deleted_at is None


def test_soft_delete_and_restore():
    sample = SampleModel(name="Delete Item")
    assert sample.is_deleted is False

    sample.soft_delete()
    assert sample.is_deleted is True
    assert isinstance(sample.deleted_at, datetime)

    sample.restore()
    assert sample.is_deleted is False
    assert sample.deleted_at is None


def test_model_as_dict():
    sample = SampleModel(name="Dict Item", created_by_id="admin_1")
    data = sample.as_dict()
    assert data["name"] == "Dict Item"
    assert data["created_by_id"] == "admin_1"
    assert "id" in data
    assert "is_deleted" in data

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import UserRole
from app.schemas.user import UserSummary


class OrganizationBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str = Field(min_length=1, max_length=150, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    plan_type: str = "free"


class OrganizationCreate(OrganizationBase):
    settings: Optional[Dict[str, Any]] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None
    plan_type: Optional[str] = None
    max_members: Optional[int] = None
    max_storage_bytes: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationMembershipBase(BaseModel):
    user_id: uuid.UUID
    role: UserRole = UserRole.MEMBER


class OrganizationMembershipCreate(OrganizationMembershipBase):
    pass


class OrganizationMembershipUpdate(BaseModel):
    role: UserRole
    is_active: Optional[bool] = None


class OrganizationMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    user: Optional[UserSummary] = None


class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    max_members: int
    max_storage_bytes: int
    storage_used_bytes: int
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

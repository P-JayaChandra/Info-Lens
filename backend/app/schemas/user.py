import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=150)
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    profile_picture_url: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128, description="Plain text password")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    profile_picture_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_verified: bool
    is_superuser: bool
    last_login_at: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

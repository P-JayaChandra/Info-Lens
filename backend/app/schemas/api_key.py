import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class APIKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    organization_id: Optional[uuid.UUID] = None
    expires_in_days: Optional[int] = Field(default=None, ge=1, le=365)
    scopes: List[str] = Field(default_factory=lambda: ["read", "write"])


class APIKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    key_prefix: str
    name: str
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    scopes: List[str]
    created_at: datetime


class APIKeyCreatedResponse(APIKeyResponse):
    raw_key: str = Field(description="Raw API key token shown only once at creation")

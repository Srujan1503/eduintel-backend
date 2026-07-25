from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SchoolCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(...)
    subscription_tier: Optional[str] = Field("starter")
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None


class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    subscription_tier: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None


class SchoolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    type: str
    subscription_tier: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool

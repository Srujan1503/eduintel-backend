from typing import Optional

from pydantic import BaseModel, Field
from uuid import UUID


class SchoolCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(...)
    subscription_tier: Optional[str] = Field("starter")
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    logo_url: Optional[str]


class SchoolUpdate(BaseModel):
    name: Optional[str]
    type: Optional[str]
    subscription_tier: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    logo_url: Optional[str]


class SchoolResponse(BaseModel):
    id: UUID
    name: str
    type: str
    subscription_tier: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    logo_url: Optional[str]
    is_active: bool

    class Config:
        orm_mode = True

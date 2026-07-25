from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CampaignCreate(BaseModel):
    name: str = Field(...)
    channel: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    meta: Optional[dict] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    channel: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    spend: Optional[float] = None
    conversions: Optional[int] = None
    meta: Optional[dict] = None


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID
    name: str
    channel: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    spend: Optional[float] = None
    conversions: Optional[int] = None
    meta: Optional[dict] = None

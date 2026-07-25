from typing import Optional
from uuid import UUID

from datetime import date
from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(...)
    channel: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[float]
    meta: Optional[dict]


class CampaignUpdate(BaseModel):
    name: Optional[str]
    channel: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[float]
    spend: Optional[float]
    conversions: Optional[int]
    meta: Optional[dict]


class CampaignResponse(BaseModel):
    id: UUID
    school_id: UUID
    name: str
    channel: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[float]
    spend: Optional[float]
    conversions: Optional[int]
    meta: Optional[dict]

    class Config:
        orm_mode = True

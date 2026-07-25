from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompetitorCreate(BaseModel):
    name: str = Field(..., min_length=1)
    domain: Optional[str] = None
    meta: Optional[dict] = None


class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    meta: Optional[dict] = None
    threat_score: Optional[float] = None


class CompetitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: Optional[UUID] = None
    name: str
    domain: Optional[str] = None
    meta: Optional[dict] = None
    threat_score: Optional[float] = None

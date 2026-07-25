from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CompetitorCreate(BaseModel):
    name: str = Field(..., min_length=1)
    domain: Optional[str]
    meta: Optional[dict]


class CompetitorUpdate(BaseModel):
    name: Optional[str]
    domain: Optional[str]
    meta: Optional[dict]
    threat_score: Optional[float]


class CompetitorResponse(BaseModel):
    id: UUID
    school_id: Optional[UUID]
    name: str
    domain: Optional[str]
    meta: Optional[dict]
    threat_score: Optional[float]

    class Config:
        orm_mode = True

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.competitor_service import CompetitorService
from app.auth.dependencies import require_school, require_role

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.post("/", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
def create_competitor(
    payload: CompetitorCreate,
    db: Session = Depends(get_db),
    user=Depends(require_school),
):
    service = CompetitorService(db)
    obj = service.create(payload, school_id=user.school_id)
    return obj


@router.get("/", response_model=PaginatedResponse[CompetitorResponse])
def list_competitors(pagination: PaginationParams = Depends(), q: Optional[str] = None, db: Session = Depends(get_db)):
    service = CompetitorService(db)
    items, total = service.search(q=q, page=pagination.page, page_size=pagination.page_size)
    return PaginatedResponse.build(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{competitor_id}", response_model=CompetitorResponse)
def get_competitor(competitor_id: UUID, db: Session = Depends(get_db)):
    service = CompetitorService(db)
    obj = service.get(competitor_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    return obj


@router.put("/{competitor_id}", response_model=CompetitorResponse)
def update_competitor(
    competitor_id: UUID,
    payload: CompetitorUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_role("super_admin")),
):
    service = CompetitorService(db)
    obj = service.get(competitor_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    return service.update(obj, payload)


@router.post("/{competitor_id}/threat", response_model=CompetitorResponse)
def set_threat_score(competitor_id: UUID, score: float, db: Session = Depends(get_db), _ = Depends(require_role("super_admin"))):
    service = CompetitorService(db)
    updated = service.set_threat_score(competitor_id, score)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    return updated


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competitor(competitor_id: UUID, db: Session = Depends(get_db), _ = Depends(require_role("super_admin"))):
    service = CompetitorService(db)
    obj = service.get(competitor_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    service.delete(obj)
    return None

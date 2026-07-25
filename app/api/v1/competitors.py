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
from app.auth.dependencies import CurrentUser, ensure_tenant_access, require_role, require_school

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.post("/", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
def create_competitor(
    payload: CompetitorCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("school_admin", "marketing_manager")),
):
    if user.school_id is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account is not linked to a school yet")
    service = CompetitorService(db)
    obj = service.create(payload, school_id=user.school_id)
    return obj


@router.get("/", response_model=PaginatedResponse[CompetitorResponse])
def list_competitors(
    pagination: PaginationParams = Depends(),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_school),
):
    service = CompetitorService(db)
    items, total = service.search(q=q, page=pagination.page, page_size=pagination.page_size)
    return PaginatedResponse.build(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{competitor_id}", response_model=CompetitorResponse)
def get_competitor(competitor_id: UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(require_school)):
    service = CompetitorService(db)
    obj = service.get(competitor_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    ensure_tenant_access(obj, user)
    return obj


@router.put("/{competitor_id}", response_model=CompetitorResponse)
def update_competitor(
    competitor_id: UUID,
    payload: CompetitorUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("school_admin", "marketing_manager")),
):
    service = CompetitorService(db)
    obj = service.get(competitor_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    ensure_tenant_access(obj, user)
    return service.update(obj, payload)


@router.post("/{competitor_id}/threat", response_model=CompetitorResponse)
def set_threat_score(
    competitor_id: UUID,
    score: float,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("school_admin", "marketing_manager")),
):
    service = CompetitorService(db)
    updated = service.set_threat_score(competitor_id, score)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    ensure_tenant_access(updated, user)
    return updated


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competitor(
    competitor_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("school_admin", "marketing_manager")),
):
    service = CompetitorService(db)
    obj = service.get(competitor_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Competitor not found")
    ensure_tenant_access(obj, user)
    service.delete(obj)
    return None

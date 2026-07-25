from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.campaign_service import CampaignService
from app.auth.dependencies import CurrentUser, ensure_tenant_access, require_role, require_school

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("school_admin", "marketing_manager")),
):
    if user.school_id is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account is not linked to a school yet")
    service = CampaignService(db)
    obj = service.create(payload, school_id=user.school_id)
    return obj


@router.get("/", response_model=PaginatedResponse[CampaignResponse])
def list_campaigns(pagination: PaginationParams = Depends(), db: Session = Depends(get_db), user: CurrentUser = Depends(require_school)):
    service = CampaignService(db)
    items, total = service.list(page=pagination.page, page_size=pagination.page_size, filters={"school_id": user.school_id})
    return PaginatedResponse.build(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(require_school)):
    service = CampaignService(db)
    obj = service.get(campaign_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    ensure_tenant_access(obj, user)
    return obj


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: UUID,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("school_admin", "marketing_manager")),
):
    service = CampaignService(db)
    obj = service.get(campaign_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    ensure_tenant_access(obj, user)
    return service.update(obj, payload)


@router.get("/{campaign_id}/roi")
def campaign_roi(campaign_id: UUID, db: Session = Depends(get_db), user: CurrentUser = Depends(require_school)):
    service = CampaignService(db)
    obj = service.get(campaign_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    ensure_tenant_access(obj, user)
    roi = service.compute_roi(obj)
    return {"campaign_id": str(campaign_id), "roi": roi}


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role("school_admin", "marketing_manager")),
):
    service = CampaignService(db)
    obj = service.get(campaign_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    ensure_tenant_access(obj, user)
    service.delete(obj)
    return None

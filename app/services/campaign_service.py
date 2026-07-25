from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.campaign import CampaignRepository
from app.schemas.campaign import CampaignCreate, CampaignUpdate


class CampaignService:
    def __init__(self, db: Session):
        self.repo = CampaignRepository(db)

    def get(self, id: UUID):
        return self.repo.get(id)

    def list(self, page: int = 1, page_size: int = 20, filters: dict | None = None):
        return self.repo.list(page=page, page_size=page_size, filters=filters)

    def create(self, data: CampaignCreate, school_id: Optional[UUID] = None):
        payload = data.model_dump()
        if school_id:
            payload["school_id"] = school_id
        return self.repo.create(payload)

    def update(self, db_obj, data: CampaignUpdate):
        return self.repo.update(db_obj, data.model_dump(exclude_unset=True))

    def delete(self, db_obj):
        return self.repo.soft_delete(db_obj)

    def list_active(self, school_id: Optional[UUID] = None):
        return self.repo.list_active(school_id=school_id)

    def compute_roi(self, campaign):
        try:
            budget = float(campaign.budget or 0)
            conversions = int(campaign.conversions or 0)
            # placeholder: treat revenue per conversion as meta or default 1
            revenue_per_conversion = (campaign.meta or {}).get("revenue_per_conversion", 1)
            revenue = conversions * float(revenue_per_conversion)
            return (revenue - budget) / budget if budget else None
        except Exception:
            return None

from uuid import UUID
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.repositories.base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db: Session):
        super().__init__(Campaign, db)

    def list_active(self, *, school_id=None):
        query = self.db.query(self.model)
        if school_id:
            query = query.filter(Campaign.school_id == school_id)
        query = query.filter(Campaign.deleted_at.is_(None))
        return query.all()

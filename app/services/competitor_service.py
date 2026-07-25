from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.competitor import CompetitorRepository
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate


class CompetitorService:
    def __init__(self, db: Session):
        self.repo = CompetitorRepository(db)

    def get(self, id: UUID):
        return self.repo.get(id)

    def list(self, page: int = 1, page_size: int = 20, filters: dict | None = None):
        return self.repo.list(page=page, page_size=page_size, filters=filters)

    def search(self, q: str | None = None, page: int = 1, page_size: int = 20):
        return self.repo.search(q=q, page=page, page_size=page_size)

    def create(self, data: CompetitorCreate, school_id: Optional[UUID] = None):
        payload = data.model_dump()
        if school_id:
            payload["school_id"] = school_id
        return self.repo.create(payload)

    def update(self, db_obj, data: CompetitorUpdate):
        return self.repo.update(db_obj, data.model_dump(exclude_unset=True))

    def delete(self, db_obj):
        return self.repo.soft_delete(db_obj)

    def set_threat_score(self, id: UUID, score: float):
        return self.repo.update_threat_score(id, score)

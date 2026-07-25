from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.competitor import Competitor
from app.repositories.base import BaseRepository


class CompetitorRepository(BaseRepository[Competitor]):
    def __init__(self, db: Session):
        super().__init__(Competitor, db)

    def search(self, q: str | None = None, page: int = 1, page_size: int = 20):
        query = self.db.query(self.model)
        if q:
            like = f"%{q}%"
            query = query.filter(or_(Competitor.name.ilike(like), Competitor.domain.ilike(like)))
        query = query.filter(Competitor.deleted_at.is_(None))
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def update_threat_score(self, competitor_id: UUID, score: float) -> Competitor | None:
        obj = self.get(competitor_id)
        if obj is None:
            return None
        obj.threat_score = score
        self.db.commit()
        self.db.refresh(obj)
        return obj

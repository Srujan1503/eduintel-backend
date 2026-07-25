from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.school import School
from app.repositories.base import BaseRepository


class SchoolRepository(BaseRepository[School]):
    def __init__(self, db: Session):
        super().__init__(School, db)

    def search(self, q: str | None = None, *, page: int = 1, page_size: int = 20) -> tuple[list[School], int]:
        query = self.db.query(self.model)
        if q:
            like = f"%{q}%"
            query = query.filter(School.name.ilike(like) | School.city.ilike(like) | School.state.ilike(like))

        query = query.filter(School.deleted_at.is_(None))
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

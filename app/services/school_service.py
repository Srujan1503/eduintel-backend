from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.school import SchoolRepository
from app.schemas.school import SchoolCreate, SchoolUpdate


class SchoolService:
    def __init__(self, db: Session):
        self.repo = SchoolRepository(db)

    def get(self, id: UUID):
        return self.repo.get(id)

    def list(self, page: int = 1, page_size: int = 20, filters: dict | None = None):
        return self.repo.list(page=page, page_size=page_size, filters=filters)

    def search(self, q: str | None = None, page: int = 1, page_size: int = 20):
        return self.repo.search(q=q, page=page, page_size=page_size)

    def create(self, data: SchoolCreate):
        payload = data.dict()
        return self.repo.create(payload)

    def update(self, db_obj, data: SchoolUpdate):
        return self.repo.update(db_obj, data.dict())

    def delete(self, db_obj):
        return self.repo.soft_delete(db_obj)

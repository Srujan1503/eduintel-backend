from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Database-access-only layer. No business rules live here -- that belongs
    in the service layer. Every feature repository (SchoolRepository,
    CompetitorRepository, ...) subclasses this."""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: UUID) -> ModelType | None:
        return self.db.get(self.model, id)

    def list(
        self,
        *,
        school_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[ModelType], int]:
        query = self.db.query(self.model)

        if school_id is not None and hasattr(self.model, "school_id"):
            query = query.filter(self.model.school_id == school_id)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))

        for field, value in (filters or {}).items():
            if value is not None and hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)

        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def create(self, data: dict[str, Any]) -> ModelType:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, db_obj: ModelType, data: dict[str, Any]) -> ModelType:
        for field, value in data.items():
            if value is not None:
                setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> None:
        self.db.delete(db_obj)
        self.db.commit()

    def soft_delete(self, db_obj: ModelType) -> ModelType:
        if not hasattr(db_obj, "deleted_at"):
            raise ValueError(f"{self.model.__name__} does not support soft delete")
        db_obj.deleted_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

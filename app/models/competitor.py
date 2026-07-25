import uuid

from sqlalchemy import Column, DateTime, String, func, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=True)
    meta = Column(JSONB, nullable=True)
    threat_score = Column(Float, nullable=True, default=0.0)
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Competitor {self.name}>"

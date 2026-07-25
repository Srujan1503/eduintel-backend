import uuid

from sqlalchemy import Column, Date, DateTime, String, Numeric, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False)
    name = Column(String, nullable=False)
    channel = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Numeric, nullable=True, default=0)
    spend = Column(Numeric, nullable=True, default=0)
    conversions = Column(Integer, nullable=True, default=0)
    meta = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Campaign {self.name}>"

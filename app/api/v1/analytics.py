from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.database.session import get_db
from app.models.campaign import Campaign
from app.models.competitor import Competitor

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/admissions")
def admissions(db: Session = Depends(get_db)):
    # Admissions model not implemented yet; return placeholder
    return {"data": [], "note": "Admissions model not implemented"}


@router.get("/campaigns")
def campaigns(db: Session = Depends(get_db)):
    # simple campaign analytics: counts and recent
    total = db.query(Campaign).filter(Campaign.deleted_at.is_(None)).count()
    recent_days = 30
    cutoff = date.today() - timedelta(days=recent_days)
    recent = (
        db.query(Campaign)
        .filter(Campaign.deleted_at.is_(None))
        .filter((Campaign.start_date.is_(None)) | (Campaign.start_date >= cutoff))
        .count()
    )
    return {"total": total, "recent_30_days": recent}


@router.get("/competitors")
def competitors(db: Session = Depends(get_db)):
    total = db.query(Competitor).filter(Competitor.deleted_at.is_(None)).count()
    top_threats = (
        db.query(Competitor)
        .filter(Competitor.deleted_at.is_(None))
        .order_by(Competitor.threat_score.desc())
        .limit(5)
        .all()
    )
    return {"total": total, "top_threats": [dict(id=str(c.id), name=c.name, threat_score=c.threat_score) for c in top_threats]}

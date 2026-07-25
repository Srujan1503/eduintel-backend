from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.school import School
from app.models.competitor import Competitor
from app.models.campaign import Campaign
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total_schools = db.query(School).filter(School.deleted_at.is_(None)).count()
    total_competitors = db.query(Competitor).filter(Competitor.deleted_at.is_(None)).count()
    today = date.today()
    active_campaigns = (
        db.query(Campaign)
        .filter(Campaign.deleted_at.is_(None))
        .filter((Campaign.start_date.is_(None)) | (Campaign.start_date <= today))
        .filter((Campaign.end_date.is_(None)) | (Campaign.end_date >= today))
        .count()
    )

    campaigns = db.query(Campaign).filter(Campaign.deleted_at.is_(None)).all()
    service = CampaignService(db)
    rois = [service.compute_roi(c) for c in campaigns]
    rois = [r for r in rois if r is not None]
    avg_roi = sum(rois) / len(rois) if rois else None

    return {
        "total_schools": total_schools,
        "total_competitors": total_competitors,
        "active_campaigns": active_campaigns,
        "average_marketing_roi": avg_roi,
    }


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    overview_data = overview(db=db)
    growth_score = None
    if overview_data.get("average_marketing_roi") is not None:
        try:
            growth_score = min(100, max(0, int(50 + overview_data["average_marketing_roi"] * 10)))
        except Exception:
            growth_score = None

    return {**overview_data, "growth_score": growth_score}

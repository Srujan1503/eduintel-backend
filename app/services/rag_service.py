"""
Retrieval-Augmented Generation (RAG) service for tenant-specific data retrieval.

Ensures:
- Only authenticated tenant's data is retrieved
- No cross-tenant data exposure
- Efficient querying with minimal database load
- Safe context building for AI prompts
"""

from uuid import UUID
from datetime import datetime, timedelta
from typing import Any, Dict
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.school import School
from app.models.campaign import Campaign
from app.models.competitor import Competitor


class RAGService:
    """
    Retrieves tenant-specific data for grounded AI responses.
    Every query is scoped to the authenticated tenant.
    """

    def __init__(self, db: Session, school_id: UUID):
        """
        Initialize with database session and authenticated tenant school_id.

        Args:
            db: SQLAlchemy session
            school_id: UUID of authenticated tenant school
        """
        self.db = db
        self.school_id = school_id

    def get_school_context(self) -> Dict[str, Any]:
        """
        Retrieve school profile, metadata, and basic info.
        
        Returns school name, type, subscription tier, location, and activity status.
        Safe to include in prompts.
        """
        school = self.db.query(School).filter(
            School.id == self.school_id,
            School.deleted_at.is_(None)
        ).first()

        if not school:
            return {}

        return {
            "id": str(school.id),
            "name": school.name,
            "type": school.type,
            "subscription_tier": school.subscription_tier,
            "city": school.city,
            "state": school.state,
            "country": school.country,
            "is_active": school.is_active,
            "created_at": school.created_at.isoformat() if school.created_at else None,
        }

    def get_campaigns_context(
        self,
        limit: int = 50,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Retrieve campaigns for the tenant within optional date range.
        
        Args:
            limit: Maximum number of campaigns to retrieve
            days_back: Only retrieve campaigns from last N days (0 = all)
        
        Returns:
            Dict with campaign count, summary stats, and detailed campaign list
        """
        query = self.db.query(Campaign).filter(
            Campaign.school_id == self.school_id,
            Campaign.deleted_at.is_(None)
        )

        if days_back > 0:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            query = query.filter(Campaign.created_at >= cutoff_date)

        campaigns = query.order_by(Campaign.created_at.desc()).limit(limit).all()

        total_budget = Decimal("0")
        total_spend = Decimal("0")
        total_conversions = 0
        campaign_list = []

        for campaign in campaigns:
            budget = campaign.budget or Decimal("0")
            spend = campaign.spend or Decimal("0")
            conversions = campaign.conversions or 0

            total_budget += budget
            total_spend += spend
            total_conversions += conversions

            roi_pct = 0.0
            if spend > 0:
                roi_pct = float((budget - spend) / spend * 100)

            campaign_list.append({
                "id": str(campaign.id),
                "name": campaign.name,
                "channel": campaign.channel,
                "status": "active" if campaign.end_date >= datetime.now().date() else "completed",
                "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                "budget": float(budget),
                "spend": float(spend),
                "conversions": conversions,
                "roi_pct": roi_pct,
            })

        avg_spend = float(total_spend / len(campaigns)) if campaigns else 0.0
        avg_conversions = int(total_conversions / len(campaigns)) if campaigns else 0

        return {
            "count": len(campaigns),
            "total_budget": float(total_budget),
            "total_spend": float(total_spend),
            "total_conversions": total_conversions,
            "avg_spend": avg_spend,
            "avg_conversions": avg_conversions,
            "campaigns": campaign_list,
        }

    def get_competitors_context(self, limit: int = 50) -> Dict[str, Any]:
        """
        Retrieve competitors tracked for the tenant.
        
        Args:
            limit: Maximum number of competitors to retrieve
        
        Returns:
            Dict with competitor count and detailed competitor list
        """
        competitors = self.db.query(Competitor).filter(
            Competitor.school_id == self.school_id,
            Competitor.deleted_at.is_(None)
        ).order_by(
            Competitor.threat_score.desc()
        ).limit(limit).all()

        competitor_list = []
        for competitor in competitors:
            competitor_list.append({
                "id": str(competitor.id),
                "name": competitor.name,
                "domain": competitor.domain,
                "threat_score": float(competitor.threat_score) if competitor.threat_score else 0.0,
                "first_seen": competitor.first_seen.isoformat() if competitor.first_seen else None,
                "last_seen": competitor.last_seen.isoformat() if competitor.last_seen else None,
            })

        avg_threat_score = 0.0
        if competitor_list:
            avg_threat_score = sum(c["threat_score"] for c in competitor_list) / len(competitor_list)

        high_threat_count = len([c for c in competitor_list if c["threat_score"] > 0.7])

        return {
            "count": len(competitor_list),
            "avg_threat_score": avg_threat_score,
            "high_threat_competitors": high_threat_count,
            "competitors": competitor_list,
        }

    def get_full_context(self) -> Dict[str, Any]:
        """
        Build complete, grounded context for AI prompts.
        
        Safe to pass directly to LLM. All data is scoped to authenticated tenant.
        Minimal and efficient - retrieves only necessary information.
        
        Returns:
            Dict with school, campaigns, and competitors context
        """
        return {
            "school": self.get_school_context(),
            "campaigns": self.get_campaigns_context(),
            "competitors": self.get_competitors_context(),
            "retrieved_at": datetime.now().isoformat(),
        }

    def verify_tenant_access(self) -> bool:
        """
        Verify that the tenant exists and is active.
        
        Returns:
            True if school exists and is accessible, False otherwise
        """
        school = self.db.query(School).filter(
            School.id == self.school_id,
            School.deleted_at.is_(None),
            School.is_active.is_(True)
        ).first()
        return school is not None

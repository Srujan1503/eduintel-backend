"""
Pydantic schemas for AI request/response validation.

Provides type-safe contracts for chat, analysis, and prediction endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from enum import Enum


class AIAnalysisType(str, Enum):
    """Types of AI analysis available."""
    SWOT = "swot"
    RECOMMENDATIONS = "recommendations"
    COMPETITOR_INSIGHTS = "competitor_insights"
    CAMPAIGN_OPTIMIZATION = "campaign_optimization"
    TREND_PREDICTIONS = "trend_predictions"


# Request Schemas

class ChatRequest(BaseModel):
    """Chat message request to AI assistant."""
    message: str = Field(..., description="User message or query")
    include_full_context: bool = Field(
        default=False,
        description="Include full tenant context in response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are the top-performing campaigns?",
                "include_full_context": False
            }
        }


class AnalysisRequest(BaseModel):
    """Request for structured AI analysis."""
    analysis_type: AIAnalysisType = Field(..., description="Type of analysis to perform")
    focus_area: Optional[str] = Field(
        default=None,
        description="Optional specific area to focus on (e.g., 'email marketing')"
    )
    include_historical_data: bool = Field(
        default=True,
        description="Include historical campaign data in analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "analysis_type": "swot",
                "focus_area": None,
                "include_historical_data": True
            }
        }


class PredictionRequest(BaseModel):
    """Request for AI predictions based on current data."""
    prediction_type: str = Field(..., description="Type of prediction (e.g., 'campaign_success', 'competitor_threat')")
    time_horizon_days: int = Field(
        default=30,
        description="How many days ahead to predict (1-365)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prediction_type": "campaign_success",
                "time_horizon_days": 30
            }
        }


# Response Schemas

class AIResponse(BaseModel):
    """Standard AI response format."""
    response: str = Field(..., description="AI-generated response text")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence level (0.0-1.0)"
    )
    data_sufficient: bool = Field(
        default=True,
        description="Whether sufficient data was available for response"
    )
    limitations: Optional[List[str]] = Field(
        default=None,
        description="Known limitations or gaps in the response"
    )
    context_used: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of data used to generate response"
    )
    retrieved_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when context was retrieved"
    )


class SWOTAnalysis(BaseModel):
    """SWOT analysis result."""
    strengths: List[str] = Field(default_factory=list, description="Internal strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Internal weaknesses")
    opportunities: List[str] = Field(default_factory=list, description="External opportunities")
    threats: List[str] = Field(default_factory=list, description="External threats")
    summary: Optional[str] = Field(default=None, description="High-level SWOT summary")


class SWOTResponse(BaseModel):
    """SWOT analysis endpoint response."""
    swot: SWOTAnalysis
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    data_points_analyzed: int = Field(default=0, description="Number of data points used")
    recommendations: Optional[List[str]] = Field(default=None, description="Strategic recommendations based on SWOT")
    limitations: Optional[List[str]] = Field(default=None)


class MarketingRecommendation(BaseModel):
    """Individual marketing recommendation."""
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(..., description="Priority level: high, medium, low")
    estimated_impact: str = Field(..., description="Expected impact on metrics")
    implementation_effort: str = Field(..., description="Effort required: low, medium, high")


class RecommendationsResponse(BaseModel):
    """Marketing recommendations endpoint response."""
    recommendations: List[MarketingRecommendation] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None, description="Overall summary of recommendations")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    limitations: Optional[List[str]] = Field(default=None)


class CompetitorInsight(BaseModel):
    """AI insight about a competitor."""
    competitor_name: str = Field(..., description="Name of competitor")
    threat_level: str = Field(..., description="Threat level: high, medium, low")
    key_strengths: List[str] = Field(default_factory=list)
    vulnerabilities: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class CompetitorInsightsResponse(BaseModel):
    """Competitor insights endpoint response."""
    insights: List[CompetitorInsight] = Field(default_factory=list)
    market_overview: Optional[str] = Field(default=None)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    limitations: Optional[List[str]] = Field(default=None)


class Prediction(BaseModel):
    """Individual prediction result."""
    metric: str = Field(..., description="Metric being predicted")
    predicted_value: str = Field(..., description="Predicted value or outcome")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    reasoning: str = Field(..., description="Reasoning behind prediction")


class PredictionsResponse(BaseModel):
    """Trend predictions endpoint response."""
    predictions: List[Prediction] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None)
    data_points_used: int = Field(default=0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    limitations: Optional[List[str]] = Field(default=None)


class CampaignOptimization(BaseModel):
    """Campaign optimization suggestion."""
    campaign_name: str = Field(..., description="Campaign being optimized")
    suggestion: str = Field(..., description="Optimization suggestion")
    expected_improvement: str = Field(..., description="Expected improvement in metrics")
    urgency: str = Field(..., description="Urgency level: high, medium, low")


class CampaignOptimizationResponse(BaseModel):
    """Campaign optimization endpoint response."""
    optimizations: List[CampaignOptimization] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    limitations: Optional[List[str]] = Field(default=None)

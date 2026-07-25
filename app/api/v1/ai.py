"""
Production AI endpoints with Gemini integration and RAG.

All endpoints require authentication and enforce tenant isolation.
Responses are grounded in database data.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.schemas.ai import (
    ChatRequest,
    AnalysisRequest,
    PredictionRequest,
    AIResponse,
    SWOTResponse,
    RecommendationsResponse,
    CompetitorInsightsResponse,
    CampaignOptimizationResponse,
    PredictionsResponse,
)
from app.services.ai_service import AIService, AIServiceError

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=AIResponse)
def chat_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Chat with AI assistant (grounded in tenant data).
    
    Requires authentication. Responses are scoped to authenticated tenant.
    """
    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be linked to a school to use AI features"
        )

    try:
        service = AIService(db, user.school_id)
        result = service.chat(req.message, include_full_context=req.include_full_context)
        return AIResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error in chat endpoint"
        )


@router.post("/swot", response_model=SWOTResponse)
def swot_endpoint(
    req: AnalysisRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Generate SWOT analysis based on tenant's campaigns and competitive landscape.
    
    Requires authentication. Analysis is scoped to authenticated tenant only.
    """
    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be linked to a school to use AI features"
        )

    try:
        service = AIService(db, user.school_id)
        result = service.swot_analysis(focus_area=req.focus_area)
        return SWOTResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error in SWOT endpoint"
        )


@router.post("/recommendations", response_model=RecommendationsResponse)
def recommendations_endpoint(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Generate marketing recommendations based on tenant data.
    
    Requires authentication. Recommendations are grounded in actual tenant metrics.
    """
    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be linked to a school to use AI features"
        )

    try:
        service = AIService(db, user.school_id)
        result = service.recommendations()
        return RecommendationsResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error in recommendations endpoint"
        )


@router.post("/competitor-insights", response_model=CompetitorInsightsResponse)
def competitor_insights_endpoint(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Generate insights about tracked competitors.
    
    Requires authentication. Uses threat scores and market analysis scoped to tenant.
    """
    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be linked to a school to use AI features"
        )

    try:
        service = AIService(db, user.school_id)
        result = service.competitor_insights()
        return CompetitorInsightsResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error in competitor insights endpoint"
        )


@router.post("/campaign-optimization", response_model=CampaignOptimizationResponse)
def campaign_optimization_endpoint(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Generate campaign optimization suggestions.
    
    Requires authentication. Suggestions are based on tenant's campaign performance data.
    """
    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be linked to a school to use AI features"
        )

    try:
        service = AIService(db, user.school_id)
        result = service.campaign_optimization()
        return CampaignOptimizationResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error in campaign optimization endpoint"
        )


@router.post("/predictions", response_model=PredictionsResponse)
def predictions_endpoint(
    req: PredictionRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Predict trends based on historical campaign data.
    
    Requires authentication. Predictions are grounded in tenant's historical metrics.
    """
    if not user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be linked to a school to use AI features"
        )

    # Validate time horizon
    if req.time_horizon_days < 1 or req.time_horizon_days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="time_horizon_days must be between 1 and 365"
        )

    try:
        service = AIService(db, user.school_id)
        result = service.trend_predictions(time_horizon_days=req.time_horizon_days)
        return PredictionsResponse(**result)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error in predictions endpoint"
        )

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.ai_service import AIService
from app.database.session import get_db
from app.auth.dependencies import require_school

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str


class RecommendationRequest(BaseModel):
    context: dict | None = None


class SWOTRequest(BaseModel):
    school_id: str | None = None


class PredictionRequest(BaseModel):
    payload: dict | None = None


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db), user=Depends(require_school)):
    service = AIService()
    return service.chat(req.message, context={"school_id": str(user.school_id)})


@router.post("/recommendations")
def recommendations(req: RecommendationRequest, db: Session = Depends(get_db), user=Depends(require_school)):
    service = AIService()
    return service.recommendations(req.context or {})


@router.post("/swot")
def swot(req: SWOTRequest, db: Session = Depends(get_db), user=Depends(require_school)):
    service = AIService()
    return service.swot(req.school_id or str(user.school_id))


@router.post("/predictions")
def predictions(req: PredictionRequest, db: Session = Depends(get_db), user=Depends(require_school)):
    service = AIService()
    return service.predictions(req.payload or {})

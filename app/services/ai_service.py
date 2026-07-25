from typing import Any, Dict


class AIService:
    """Placeholder AI service. Integrate Gemini here when available."""

    def chat(self, message: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # Return a deterministic placeholder
        return {"response": f"Echo: {message}", "context_used": context}

    def recommendations(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"recommendations": [], "note": "placeholder"}

    def swot(self, school_id: str | None = None) -> Dict[str, Any]:
        return {"swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}}

    def predictions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"predictions": [], "note": "placeholder"}

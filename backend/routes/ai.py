"""AI API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])


class AISuggestRequest(BaseModel):
    """Request model for AI task suggestions."""
    prompt: str = Field(..., min_length=1, description="User's prompt for task suggestions")


class AISuggestResponse(BaseModel):
    """Response model for AI task suggestions."""
    suggestions: list[str]


@router.post("/suggest-tasks", response_model=AISuggestResponse)
def suggest_tasks(request: AISuggestRequest):
    """Get AI-powered task suggestions based on a prompt."""
    suggestions, error = ai_service.suggest_tasks(request.prompt)
    if error:
        raise HTTPException(status_code=503, detail=error)
    return AISuggestResponse(suggestions=suggestions)


@router.get("/status")
def ai_status():
    """Check if AI is configured and available."""
    configured = ai_service.is_ai_configured()
    return {
        "configured": configured,
        "message": "AI is ready" if configured else "AI is not configured. Set OPENAI_API_KEY in .env",
    }

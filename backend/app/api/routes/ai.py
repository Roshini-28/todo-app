"""AI chat API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])


class AIChatRequest(BaseModel):
    """Request model for AI chat."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's message"
    )
    provider: str | None = Field(
        default=None,
        description="AI provider (ollama_cloud, nvidia, gemini). Uses default if not specified."
    )


class AIChatResponse(BaseModel):
    """Response model for AI chat."""
    answer: str
    provider: str
    model: str


# Legacy models (kept for backward compatibility)
class AISuggestRequest(BaseModel):
    """Request model for AI task suggestions."""
    prompt: str = Field(..., min_length=1, description="User's prompt for task suggestions")


class AISuggestResponse(BaseModel):
    """Response model for AI task suggestions."""
    suggestions: list[str]
    provider: str | None = None
    model: str | None = None


@router.post("/chat", response_model=AIChatResponse)
async def chat(request: AIChatRequest):
    """Chat with the AI assistant.

    The AI can help with:
    - Summarizing tasks
    - Suggesting priorities
    - Daily planning
    - Answering questions about tasks
    """
    try:
        result = ai_service.generate_response(
            messages=[{"role": "user", "content": request.message}],
            provider=request.provider,
            max_tokens=2048,
        )

        return AIChatResponse(
            answer=result["answer"],
            provider=result["provider"],
            model=result["model"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "rate" in error_msg.lower() or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="AI provider rate limit exceeded. Please try again later.")
        raise HTTPException(status_code=502, detail=f"AI provider error: {error_msg}")


@router.post("/suggest-tasks", response_model=AISuggestResponse)
async def suggest_tasks(request: AISuggestRequest):
    """Get AI-powered task suggestions based on a prompt."""
    try:
        result = ai_service.suggest_tasks(request.prompt)
        return AISuggestResponse(
            suggestions=result["suggestions"],
            provider=result["provider"],
            model=result["model"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        if "rate" in error_msg.lower() or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="AI provider rate limit exceeded. Please try again later.")
        raise HTTPException(status_code=502, detail=f"AI provider error: {error_msg}")


@router.get("/health")
def ai_health():
    """Check if AI is configured and available."""
    providers = ai_service.get_available_providers()
    return {
        "configured": len(providers) > 0,
        "providers": providers,
        "default_provider": ai_service.settings.DEFAULT_AI_PROVIDER,
        "message": "AI is ready" if providers else "AI is not configured. Please set provider API keys in .env",
    }

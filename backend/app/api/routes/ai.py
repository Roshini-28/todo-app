"""AI chat API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agents.todo_agent import create_todo_agent, chat_with_agent
from app.ai.providers import get_available_providers
from app.config.settings import settings

router = APIRouter(prefix="/ai", tags=["AI"])


class AIChatRequest(BaseModel):
    """Request model for AI chat."""
    message: str = Field(..., min_length=1, description="User's message")


class AIChatResponse(BaseModel):
    """Response model for AI chat."""
    response: str
    provider: str
    model: str


# Store agent instance (created once, reused for all requests)
_agent = None


def get_agent():
    """Get or create the AI agent."""
    global _agent
    if _agent is None:
        _agent = create_todo_agent(settings.DEFAULT_LLM)
    return _agent


@router.post("/chat", response_model=AIChatResponse)
async def chat(request: AIChatRequest):
    """Chat with the AI agent.

    The agent can:
    - Create tasks
    - List tasks
    - Update tasks
    - Complete/uncomplete tasks
    - Delete tasks
    - Summarize tasks
    """
    try:
        agent = get_agent()
        response = chat_with_agent(agent, request.message)

        return AIChatResponse(
            response=response,
            provider="ollama",
            model="llama3.2:3b",
        )
    except Exception as e:
        error_msg = str(e)
        if "ollama" in error_msg.lower() or "connection" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="Ollama is not available. Please start Ollama and try again."
            )
        raise HTTPException(status_code=500, detail=f"AI error: {error_msg}")


@router.get("/health")
def ai_health():
    """Check if AI is configured and available."""
    providers = get_available_providers()
    return {
        "configured": len(providers) > 0,
        "providers": providers,
        "default_provider": "ollama",
        "message": "AI is ready" if providers else "AI is not configured",
    }

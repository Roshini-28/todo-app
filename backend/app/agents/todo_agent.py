"""Agno Todo Agent - AI agent that can perform Todo operations."""
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from app.tools.todo_tools import TODO_TOOLS
from app.ai.litellm_client import get_llm_client
from app.config.settings import settings


def create_todo_agent(provider=None):
    """Create an AI agent with Todo tools.

    Args:
        provider: AI provider name ('ollama', 'gemini', 'nvidia', 'openai')

    Returns:
        Agent: Configured Agno agent
    """
    if provider is None:
        provider = settings.DEFAULT_LLM

    # Get LLM client for the specified provider
    llm_client = get_llm_client(provider)

    # Create LiteLLM model for Agno
    # LiteLLM requires provider prefix for Ollama models
    model_id = llm_client.config["model"]
    if provider == "ollama" and not model_id.startswith("ollama/"):
        model_id = f"ollama/{model_id}"

    # Create the model with correct configuration
    model_kwargs = {
        "id": model_id,
    }

    # Add base URL for Ollama
    if provider == "ollama" and llm_client.config.get("base_url"):
        model_kwargs["api_base"] = llm_client.config["base_url"]

    model = LiteLLM(**model_kwargs)

    # System instructions for the agent
    system_instructions = """You are a helpful Todo assistant. You help users manage their tasks.

Your capabilities:
- Create new tasks
- List all tasks
- Update existing tasks
- Mark tasks as completed or pending
- Delete tasks
- Summarize tasks

Guidelines:
- Always confirm actions with the user before deleting tasks
- When listing tasks, show them in a clear, organized format
- When creating tasks, use sensible defaults if information is missing
- If a user asks to complete a task, first find the task by name or ID
- Be concise and helpful in your responses

Example interactions:
User: "Add a task to learn Python"
→ Call create_todo(title="Learn Python")

User: "Show my pending tasks"
→ Call list_todos(status="Pending")

User: "Complete my Python task"
→ First list tasks to find it, then call complete_todo(task_id)

User: "Delete the old task"
→ Ask for confirmation, then call delete_todo(task_id)
"""

    # Create the agent
    agent = Agent(
        model=model,
        tools=TODO_TOOLS,
        instructions=system_instructions,
        markdown=True,
    )

    return agent


def chat_with_agent(agent, message: str) -> str:
    """Send a message to the agent and get a response.

    Args:
        agent: The Agno agent
        message: User's message

    Returns:
        str: Agent's response
    """
    response = agent.run(message)
    return response.content if hasattr(response, 'content') else str(response)

"""AI service - unified interface for all cloud AI providers via LiteLLM."""
import os
import json
import litellm
from typing import Optional
from app.config.settings import settings


# Map logical provider names to LiteLLM prefixes
PROVIDER_PREFIXES = {
    "ollama_cloud": "ollama/",
    "nvidia": "nvidia/",
    "gemini": "gemini/",
}


def is_provider_configured(provider: str) -> bool:
    """Check if a cloud provider is properly configured."""
    if provider == "ollama_cloud":
        return bool(
            settings.OLLAMA_CLOUD_API_KEY
            and "your_" not in settings.OLLAMA_CLOUD_API_KEY
            and settings.OLLAMA_CLOUD_BASE_URL
            and "your-" not in settings.OLLAMA_CLOUD_BASE_URL
        )
    elif provider == "nvidia":
        return bool(
            settings.NVIDIA_API_KEY
            and "your_" not in settings.NVIDIA_API_KEY
        )
    elif provider == "gemini":
        return bool(
            settings.GEMINI_API_KEY
            and "your_" not in settings.GEMINI_API_KEY
        )
    return False


def get_provider_model(provider: str) -> str:
    """Get the model name for a provider."""
    if provider == "ollama_cloud":
        return settings.OLLAMA_CLOUD_MODEL
    elif provider == "nvidia":
        return settings.NVIDIA_MODEL
    elif provider == "gemini":
        return settings.GEMINI_MODEL
    return "unknown"


def get_provider_base_url(provider: str) -> Optional[str]:
    """Get the base URL for a provider."""
    if provider == "ollama_cloud":
        return settings.OLLAMA_CLOUD_BASE_URL
    elif provider == "nvidia":
        return settings.NVIDIA_BASE_URL
    elif provider == "gemini":
        return settings.GEMINI_BASE_URL
    return None


def validate_provider(provider: str) -> tuple[bool, str]:
    """Validate a provider name and check if it's configured.

    Returns:
        tuple: (is_valid, error_message)
    """
    valid_providers = ["ollama_cloud", "nvidia", "gemini"]

    if provider not in valid_providers:
        return False, f"Invalid provider '{provider}'. Valid options: {', '.join(valid_providers)}"

    if not is_provider_configured(provider):
        missing = []
        if provider == "ollama_cloud":
            if not settings.OLLAMA_CLOUD_API_KEY or "your_" in settings.OLLAMA_CLOUD_API_KEY:
                missing.append("OLLAMA_CLOUD_API_KEY")
            if not settings.OLLAMA_CLOUD_BASE_URL or "your-" in settings.OLLAMA_CLOUD_BASE_URL:
                missing.append("OLLAMA_CLOUD_BASE_URL")
        elif provider == "nvidia":
            if not settings.NVIDIA_API_KEY or "your_" in settings.NVIDIA_API_KEY:
                missing.append("NVIDIA_API_KEY")
        elif provider == "gemini":
            if not settings.GEMINI_API_KEY or "your_" in settings.GEMINI_API_KEY:
                missing.append("GEMINI_API_KEY")

        if missing:
            return False, f"Provider '{provider}' is not configured. Missing: {', '.join(missing)}"

    return True, ""


def generate_response(
    messages: list,
    provider: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> dict:
    """Generate a response using LiteLLM with the selected cloud provider.

    Args:
        messages: List of message dicts with 'role' and 'content'
        provider: Provider name ('ollama_cloud', 'nvidia', 'gemini')
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        dict: {'answer': str, 'provider': str, 'model': str}

    Raises:
        ValueError: If provider is invalid or not configured
        Exception: If the LLM call fails
    """
    # Use default provider if not specified
    if provider is None:
        provider = settings.DEFAULT_AI_PROVIDER

    # Validate provider
    is_valid, error_msg = validate_provider(provider)
    if not is_valid:
        raise ValueError(error_msg)

    # Get model and construct LiteLLM model name
    model = get_provider_model(provider)
    litellm_model = f"{PROVIDER_PREFIXES[provider]}{model}"

    # Build kwargs for LiteLLM
    kwargs = {
        "model": litellm_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # Add base URL for providers that need it
    base_url = get_provider_base_url(provider)
    if base_url:
        kwargs["api_base"] = base_url

    # Make the API call with fallback support
    try:
        response = litellm.completion(**kwargs)
        answer = response.choices[0].message.content
        return {
            "answer": answer,
            "provider": provider,
            "model": model,
        }
    except Exception as e:
        error_msg = str(e).lower()
        # Check if it's a rate limit or quota error
        if "rate" in error_msg or "quota" in error_msg or "limit" in error_msg or "429" in error_msg:
            # Try fallback provider if enabled
            if settings.ENABLE_FALLBACK and settings.FALLBACK_PROVIDER != provider:
                fallback_model = get_provider_model(settings.FALLBACK_PROVIDER)
                litellm_model = f"{PROVIDER_PREFIXES[settings.FALLBACK_PROVIDER]}{fallback_model}" if settings.FALLBACK_PROVIDER in PROVIDER_PREFIXES else fallback_model

                fallback_kwargs = {
                    "model": litellm_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }

                # Pass API key explicitly for fallback provider
                if settings.FALLBACK_PROVIDER == "nvidia":
                    fallback_kwargs["api_key"] = settings.NVIDIA_API_KEY
                elif settings.FALLBACK_PROVIDER == "gemini":
                    fallback_kwargs["api_key"] = settings.GEMINI_API_KEY
                elif settings.FALLBACK_PROVIDER == "ollama_cloud":
                    fallback_kwargs["api_key"] = settings.OLLAMA_CLOUD_API_KEY

                fallback_base_url = get_provider_base_url(settings.FALLBACK_PROVIDER)
                if fallback_base_url:
                    fallback_kwargs["api_base"] = fallback_base_url

                response = litellm.completion(**fallback_kwargs)
                answer = response.choices[0].message.content
                return {
                    "answer": answer,
                    "provider": settings.FALLBACK_PROVIDER,
                    "model": fallback_model,
                }
        raise


def suggest_tasks(prompt: str, provider: Optional[str] = None) -> dict:
    """Use AI to suggest tasks based on a user prompt.

    Args:
        prompt: User's prompt for task suggestions
        provider: AI provider to use

    Returns:
        dict: {'suggestions': list, 'provider': str, 'model': str}
    """
    system_prompt = """You are a helpful task management assistant.
Given a user's prompt, suggest 3-6 specific, actionable tasks they should create.
Return ONLY a JSON array of task title strings. No other text.
Example: ["Review chapter 5", "Practice problems", "Schedule study session"]"""

    result = generate_response(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        provider=provider,
        max_tokens=512,
    )

    # Parse the response
    content = result["answer"].strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]
        content = content.strip()

    suggestions = json.loads(content)
    if not isinstance(suggestions, list):
        raise ValueError("AI returned an unexpected format")

    suggestions = [s.strip() for s in suggestions if isinstance(s, str) and s.strip()]

    return {
        "suggestions": suggestions,
        "provider": result["provider"],
        "model": result["model"],
    }


def get_available_providers() -> list:
    """Get list of configured cloud providers."""
    available = []
    for provider in ["ollama_cloud", "nvidia", "gemini"]:
        if is_provider_configured(provider):
            available.append(provider)
    return available

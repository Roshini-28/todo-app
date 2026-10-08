"""AI provider selection and configuration."""
from app.config.settings import settings


def get_provider_config(provider_name=None):
    """Get configuration for a specific AI provider.

    Args:
        provider_name: 'ollama', 'gemini', 'nvidia', or 'openai'.
                       If None, uses DEFAULT_LLM from settings.

    Returns:
        dict with 'model', 'api_key', 'base_url' (if applicable)
    """
    if provider_name is None:
        provider_name = settings.DEFAULT_LLM

    providers = {
        "ollama": {
            "model": settings.OLLAMA_MODEL,
            "api_key": None,
            "base_url": settings.OLLAMA_BASE_URL,
        },
        "gemini": {
            "model": settings.GEMINI_MODEL,
            "api_key": settings.GEMINI_API_KEY,
            "base_url": None,
        },
        "nvidia": {
            "model": settings.NVIDIA_MODEL,
            "api_key": settings.NVIDIA_API_KEY,
            "base_url": None,
        },
        "openai": {
            "model": settings.OPENAI_MODEL,
            "api_key": settings.OPENAI_API_KEY,
            "base_url": None,
        },
    }

    return providers.get(provider_name, providers["ollama"])


def is_provider_available(provider_name):
    """Check if a provider is properly configured and available."""
    config = get_provider_config(provider_name)

    if provider_name == "ollama":
        # Ollama runs locally - check if it's running
        return True  # We'll check at runtime

    # For API-based providers, check if API key exists
    return config["api_key"] is not None and "your_" not in config["api_key"]


def get_available_providers():
    """Get list of all available (configured) providers."""
    available = []
    for provider in ["ollama", "gemini", "nvidia", "openai"]:
        if is_provider_available(provider):
            available.append(provider)
    return available


def get_fallback_provider():
    """Get the fallback provider name."""
    if settings.ENABLE_FALLBACK and is_provider_available(settings.FALLBACK_PROVIDER):
        return settings.FALLBACK_PROVIDER
    return None

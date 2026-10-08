"""LiteLLM client - unified interface for all AI providers."""
import litellm
from app.ai.providers import get_provider_config, is_provider_available, get_fallback_provider


class LLMClient:
    """Simple wrapper around LiteLLM for text generation."""

    def __init__(self, provider=None):
        """Initialize with a specific provider or use default.

        Args:
            provider: 'ollama', 'gemini', 'nvidia', or 'openai'
        """
        self.provider = provider
        self.config = get_provider_config(provider)

    def generate(self, messages, max_tokens=500, temperature=0.7):
        """Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            str: The generated response text

        Raises:
            Exception: If the LLM call fails
        """
        model = self.config["model"]

        # LiteLLM requires provider prefix for Ollama models
        if self.provider == "ollama" and not model.startswith("ollama/"):
            model = f"ollama/{model}"

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Add base URL for Ollama
        if self.provider == "ollama" and self.config["base_url"]:
            kwargs["api_base"] = self.config["base_url"]

        response = litellm.completion(**kwargs)
        return response.choices[0].message.content

    def generate_with_fallback(self, messages, max_tokens=500, temperature=0.7):
        """Generate with fallback to another provider if primary fails.

        Args:
            messages: List of message dicts
            max_tokens: Maximum tokens
            temperature: Sampling temperature

        Returns:
            tuple: (response_text, provider_used)
        """
        # Try primary provider
        try:
            response = self.generate(messages, max_tokens, temperature)
            return response, self.provider
        except Exception:
            pass

        # Try fallback provider
        fallback = get_fallback_provider()
        if fallback and fallback != self.provider:
            fallback_client = LLMClient(fallback)
            try:
                response = fallback_client.generate(messages, max_tokens, temperature)
                return response, fallback
            except Exception:
                pass

        raise Exception("All AI providers failed. Please check your configuration.")


def get_llm_client(provider=None):
    """Factory function to get an LLM client.

    Args:
        provider: Provider name or None for default

    Returns:
        LLMClient instance
    """
    return LLMClient(provider)

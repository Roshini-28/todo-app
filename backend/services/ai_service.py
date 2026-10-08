"""AI service - supports multiple providers via LiteLLM: Ollama, Gemini, NVIDIA, OpenAI."""
import os
import json
import litellm
from dotenv import load_dotenv

load_dotenv()


def is_ai_configured():
    """Check if any AI provider is configured."""
    if os.getenv("OLLAMA_ENABLED", "false").lower() == "true":
        return True
    if os.getenv("GEMINI_ENABLED", "false").lower() == "true" and os.getenv("GEMINI_API_KEY"):
        return True
    if os.getenv("NVIDIA_ENABLED", "false").lower() == "true" and os.getenv("NVIDIA_API_KEY") and "your_nvidia" not in os.getenv("NVIDIA_API_KEY", ""):
        return True
    if os.getenv("OPENAI_ENABLED", "false").lower() == "true" and os.getenv("OPENAI_API_KEY") and "your_openai" not in os.getenv("OPENAI_API_KEY", ""):
        return True
    return False


def get_provider_config():
    """Get configuration for all providers from .env"""
    return {
        "ollama": {
            "enabled": os.getenv("OLLAMA_ENABLED", "false").lower() == "true",
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "llama3.1"),
            "api_key": None,
        },
        "gemini": {
            "enabled": os.getenv("GEMINI_ENABLED", "false").lower() == "true",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        },
        "nvidia": {
            "enabled": os.getenv("NVIDIA_ENABLED", "false").lower() == "true",
            "api_key": os.getenv("NVIDIA_API_KEY"),
            "model": os.getenv("NVIDIA_MODEL", "llama-3.1-nemotron-70b-instruct"),
        },
        "openai": {
            "enabled": os.getenv("OPENAI_ENABLED", "false").lower() == "true",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        },
    }


def suggest_tasks(prompt):
    """Use AI to suggest tasks based on a user prompt.
    Tries multiple providers in order: Ollama -> Gemini -> NVIDIA -> OpenAI
    Returns (suggestions_list, error_message).
    """
    if not is_ai_configured():
        return None, "AI is not configured. Please set at least one provider in your .env file."

    try:
        system_prompt = """You are a helpful task management assistant. 
Given a user's prompt, suggest 3-6 specific, actionable tasks they should create.
Return ONLY a JSON array of task title strings. No other text.
Example: ["Review chapter 5", "Practice problems", "Schedule study session"]"""

        config = get_provider_config()
        models_to_try = []

        # Build model list based on enabled providers
        if config["ollama"]["enabled"]:
            models_to_try.append(f"ollama/{config['ollama']['model']}")

        if config["gemini"]["enabled"] and config["gemini"]["api_key"]:
            models_to_try.append(f"gemini/{config['gemini']['model']}")

        if config["nvidia"]["enabled"] and config["nvidia"]["api_key"] and "your_nvidia" not in config["nvidia"]["api_key"]:
            models_to_try.append(f"nvidia/{config['nvidia']['model']}")

        if config["openai"]["enabled"] and config["openai"]["api_key"] and "your_openai" not in config["openai"]["api_key"]:
            models_to_try.append(f"openai/{config['openai']['model']}")

        if not models_to_try:
            return None, "No AI providers are enabled. Please configure at least one provider in .env"

        response = None
        last_error = None
        tried_models = []

        for model in models_to_try:
            tried_models.append(model)
            try:
                kwargs = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300,
                }
                if model.startswith("ollama/"):
                    kwargs["api_base"] = config["ollama"]["base_url"]

                response = litellm.completion(**kwargs)
                break
            except Exception as e:
                last_error = e
                continue

        if response is None:
            return None, f"AI service error: Could not connect to any AI provider. Tried: {', '.join(tried_models)}. Error: {last_error}"

        content = response.choices[0].message.content.strip()

        # Try to parse JSON from the response
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
            content = content.strip()

        suggestions = json.loads(content)

        if not isinstance(suggestions, list):
            return None, "AI returned an unexpected format. Please try again."

        # Clean up suggestions
        suggestions = [s.strip() for s in suggestions if isinstance(s, str) and s.strip()]

        if not suggestions:
            return None, "No suggestions generated. Please try a different prompt."

        return suggestions, None

    except json.JSONDecodeError:
        return None, "Could not parse AI response. Please try again."
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            return None, "AI authentication failed. Please check your API keys in .env file."
        return None, f"AI service error: {error_msg}"

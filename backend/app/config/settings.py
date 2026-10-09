"""Application settings loaded from environment variables."""
import os
from dotenv import load_dotenv

# Load .env from the backend directory regardless of working directory
load_dotenv()


class Settings:
    """Central configuration for the application."""

    # Database
    MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "todo_db")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 60 * 24  # 24 hours

    # AI Provider Selection
    DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "gemini")
    ENABLE_FALLBACK = os.getenv("ENABLE_FALLBACK", "false").lower() == "true"
    FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "nvidia")

    # Legacy Ollama Local Settings (kept for backward compatibility)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"

    # Cloud Ollama Settings
    OLLAMA_CLOUD_MODEL = os.getenv("OLLAMA_CLOUD_MODEL", "llama3.2:3b")
    OLLAMA_CLOUD_API_KEY = os.getenv("OLLAMA_CLOUD_API_KEY")
    OLLAMA_CLOUD_BASE_URL = os.getenv("OLLAMA_CLOUD_BASE_URL")

    # Cloud NVIDIA Settings
    NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "llama-3.1-nemotron-70b-instruct")
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # Cloud Gemini Settings
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

    # Legacy settings (kept for backward compatibility)
    GEMINI_ENABLED = os.getenv("GEMINI_ENABLED", "false").lower() == "true"
    NVIDIA_ENABLED = os.getenv("NVIDIA_ENABLED", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"


settings = Settings()

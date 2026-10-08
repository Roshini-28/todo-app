"""Application settings loaded from environment variables."""
import os
from dotenv import load_dotenv

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
    DEFAULT_LLM = os.getenv("DEFAULT_LLM", "ollama")
    ENABLE_FALLBACK = os.getenv("ENABLE_FALLBACK", "false").lower() == "true"
    FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "gemini")

    # Ollama Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    # Gemini Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    # NVIDIA Settings
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "llama-3.1-nemotron-70b-instruct")

    # OpenAI Settings (fallback)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()

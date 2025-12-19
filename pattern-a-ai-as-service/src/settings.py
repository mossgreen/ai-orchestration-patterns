"""Configuration settings for Pattern A."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path | None:
    """Find .env file, searching from current directory up to root."""
    # Start from this file's location
    current = Path(__file__).parent.parent.resolve()

    # Search up to 3 levels (pattern dir, root, parent of root)
    for _ in range(3):
        env_path = current / ".env"
        if env_path.exists():
            return env_path
        current = current.parent

    return None


# Find .env file at module load time
_env_file = _find_env_file()


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

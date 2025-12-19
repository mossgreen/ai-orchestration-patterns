"""Settings for Pattern A."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from shared import get_env_file


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=get_env_file(), extra="ignore")

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

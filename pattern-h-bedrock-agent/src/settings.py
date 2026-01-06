"""Settings for Pattern H - Bedrock Agent configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from shared import get_env_file


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=get_env_file(), extra="ignore")

    # Bedrock Agent configuration
    bedrock_agent_id: Optional[str] = None
    bedrock_agent_alias_id: Optional[str] = None

    # AWS configuration
    aws_region: str = "us-east-1"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

"""Settings for Pattern E - supports local dev and Lambda deployment."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from shared import get_env_file


def _get_secret_from_aws(secret_arn: str) -> str:
    """Fetch secret value from AWS Secrets Manager."""
    import boto3

    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    return response["SecretString"]


class Settings(BaseSettings):
    """Application settings loaded from environment or AWS Secrets Manager."""

    model_config = SettingsConfigDict(env_file=get_env_file(), extra="ignore")

    openai_api_key: Optional[str] = None
    openai_secret_arn: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    def get_openai_api_key(self) -> str:
        """Get OpenAI API key from env var or Secrets Manager."""
        if self.openai_api_key:
            return self.openai_api_key
        if self.openai_secret_arn:
            return _get_secret_from_aws(self.openai_secret_arn)
        raise ValueError("No OpenAI API key configured. Set OPENAI_API_KEY or OPENAI_SECRET_ARN.")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

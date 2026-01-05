"""
Service 1: Intent Parser

Extracts structured booking intent from natural language.
Uses OpenAI to parse date, time, and preferences from user messages.
"""

import json
import logging
from datetime import datetime
from typing import Any, Protocol

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from ..models import ParsedIntent, ServiceResponse
from ..settings import Settings, get_settings
from .base import BaseService

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a booking intent parser. Extract booking details from user messages.

Today's date is {today}.

Return a JSON object with:
- date: extracted date in YYYY-MM-DD format (null if not specified)
- time: extracted time in HH:MM format (null if not specified)

Handle relative dates like "tomorrow", "next Monday", etc.
Handle time ranges like "afternoon" (14:00), "morning" (09:00), "evening" (17:00).

Examples:
- "Book tomorrow at 3pm" -> {{"date": "2024-01-16", "time": "15:00"}}
- "I need a court next Monday" -> {{"date": "2024-01-22", "time": null}}
- "Book for the afternoon" -> {{"date": null, "time": "14:00"}}

Return ONLY valid JSON, no other text."""


class OpenAIClient(Protocol):
    """Protocol for OpenAI-compatible client."""

    class Chat:
        class Completions:
            async def create(self, **kwargs) -> ChatCompletion: ...

        completions: Completions

    chat: Chat


class IntentParserService(BaseService):
    """
    Parses natural language booking requests into structured data.
    This service could be deployed as its own Lambda function.
    """

    def __init__(
        self,
        *,
        client: OpenAIClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client or AsyncOpenAI(api_key=self._settings.get_openai_api_key())

    @property
    def name(self) -> str:
        return "IntentParser"

    async def execute(self, request: dict[str, Any]) -> ServiceResponse[ParsedIntent]:
        """
        Parse user message to extract booking intent.

        Args:
            request: {"message": str} - The user's booking request

        Returns:
            ServiceResponse containing ParsedIntent
        """
        message = request.get("message", "")
        if not message or not message.strip():
            logger.warning("Empty message received")
            return ServiceResponse(success=False, error="No message provided")

        logger.debug("Parsing message: %s", message[:50])

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            response = await self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT.format(today=today)},
                    {"role": "user", "content": message},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                logger.error("OpenAI returned empty response")
                return ServiceResponse(success=False, error="AI returned empty response")

            parsed = json.loads(content)

            intent = ParsedIntent(
                date=parsed.get("date"),
                time=parsed.get("time"),
                raw_message=message,
            )

            logger.info("Parsed intent: date=%s, time=%s", intent.date, intent.time)
            return ServiceResponse(success=True, data=intent)

        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response: %s", e)
            return ServiceResponse(success=False, error=f"Failed to parse AI response: {e}")

        except Exception as e:
            logger.error("Intent parsing failed: %s", e)
            return ServiceResponse(success=False, error=f"Intent parsing failed: {e}")

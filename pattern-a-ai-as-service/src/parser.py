"""
Pattern A: LLM Parser - The ONLY AI Component

This module is the ONLY place where AI/LLM is used in Pattern A.
The LLM's job is simple: convert natural language into structured data.

No business logic, no decisions, no actions - just parsing.
"""

import json
import logging
from datetime import datetime
from typing import Protocol

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from .exceptions import ParseError
from .models import ParsedIntent
from .settings import Settings, get_settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a text parser. Extract booking details from user messages.

Today's date is {today}.

Return a JSON object with:
- date: extracted date in YYYY-MM-DD format (null if not specified)
- time: extracted time in HH:MM format (null if not specified)
- slot_preference: which slot the user wants as a number (1=first, 2=second, etc.), null if not specified

Handle relative dates like "tomorrow", "next Monday", etc.
Handle time ranges like "afternoon" (14:00), "morning" (09:00), "evening" (17:00).
Handle slot preferences like "first slot", "second one", "the first available", etc.

Examples:
- "Book tomorrow at 3pm" -> {{"date": "2024-01-16", "time": "15:00", "slot_preference": null}}
- "Tomorrow 3pm, first slot" -> {{"date": "2024-01-16", "time": "15:00", "slot_preference": 1}}
- "Next Monday afternoon, second one" -> {{"date": "2024-01-22", "time": "14:00", "slot_preference": 2}}
- "Give me the first available tomorrow" -> {{"date": "2024-01-16", "time": null, "slot_preference": 1}}

Return ONLY valid JSON
"""


class OpenAIClient(Protocol):
    """Protocol for OpenAI-compatible client."""

    class Chat:
        class Completions:
            async def create(self, **kwargs) -> ChatCompletion: ...

        completions: Completions

    chat: Chat


async def parse_intent(
    message: str,
    *,
    client: OpenAIClient | None = None,
    settings: Settings | None = None,
) -> ParsedIntent:
    """
    Parse user message to extract booking intent.

    THIS IS THE ONLY AI COMPONENT IN PATTERN A.

    Args:
        message: The user's natural language booking request
        client: OpenAI client (injected for testing)
        settings: Application settings (injected for testing)

    Returns:
        ParsedIntent with extracted date/time

    Raises:
        ParseError: If message is empty or parsing fails
    """
    if not message or not message.strip():
        raise ParseError("No message provided")

    settings = settings or get_settings()
    client = client or AsyncOpenAI(api_key=settings.openai_api_key)

    today = datetime.now().strftime("%Y-%m-%d (%A)")

    logger.debug("Parsing message: %s", message[:50])

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(today=today)},
                {"role": "user", "content": message},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.error("OpenAI API call failed: %s", e)
        raise ParseError(f"Failed to parse message: {e}") from e

    content = response.choices[0].message.content
    if not content:
        logger.error("OpenAI returned empty response")
        raise ParseError("AI returned empty response")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response: %s", content)
        raise ParseError(f"Invalid JSON from AI: {e}") from e

    logger.info(
        "Parsed intent: date=%s, time=%s, slot=%s",
        parsed.get("date"),
        parsed.get("time"),
        parsed.get("slot_preference"),
    )

    return ParsedIntent(
        date=parsed.get("date"),
        time=parsed.get("time"),
        slot_preference=parsed.get("slot_preference"),
        raw_message=message,
    )

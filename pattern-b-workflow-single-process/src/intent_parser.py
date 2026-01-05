"""Intent parser using OpenAI to extract booking details from natural language."""

import json
import logging
from datetime import datetime

from openai import AsyncOpenAI

from .models import ParsedIntent
from .settings import Settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a booking intent parser. Extract booking details from user messages.

Today's date is {today}.

Return a JSON object with:
- date: extracted date in YYYY-MM-DD format (null if not specified)
- time: extracted time in HH:MM format (null if not specified)

Handle relative dates like "tomorrow", "next Monday", etc.
Handle time expressions like "afternoon" (14:00), "morning" (09:00), "evening" (17:00).

Return ONLY valid JSON, no other text."""


class IntentParser:
    """Parses user messages to extract booking intent using OpenAI."""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.get_openai_api_key())
        self._model = settings.openai_model

    async def parse(self, message: str) -> ParsedIntent:
        """Parse user message and extract booking intent."""
        logger.debug("Parsing message: %s", message[:50])

        try:
            today = datetime.now().strftime("%Y-%m-%d")

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT.format(today=today)},
                    {"role": "user", "content": message},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)

            intent = ParsedIntent(
                date=parsed.get("date"),
                time=parsed.get("time"),
            )

            logger.info("Parsed intent: date=%s, time=%s", intent.date, intent.time)
            return intent

        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response: %s", e)
            raise

        except Exception as e:
            logger.error("OpenAI API call failed: %s", e)
            raise

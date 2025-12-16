"""
Pattern A: LLM Parser - The ONLY AI Component

This module is the ONLY place where AI/LLM is used in Pattern A.
The LLM's job is simple: convert natural language into structured data.

No business logic, no decisions, no actions - just parsing.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Setup paths for imports
_src_dir = Path(__file__).parent
sys.path.insert(0, str(_src_dir))

from models import ParsedIntent

# Load .env from project root
load_dotenv(_src_dir.parent.parent / ".env")


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

Return ONLY valid JSON, no other text."""


# Initialize the OpenAI client
_client = AsyncOpenAI()


async def parse_intent(message: str) -> ParsedIntent:
    """
    Parse user message to extract booking intent.

    THIS IS THE ONLY AI COMPONENT IN PATTERN A.

    The LLM acts as a "text utility" - converting natural language
    into structured data. No business logic, no decisions.

    Args:
        message: The user's natural language booking request

    Returns:
        ParsedIntent with extracted date/time

    Raises:
        ValueError: If message is empty or parsing fails
    """
    if not message:
        raise ValueError("No message provided")

    today = datetime.now().strftime("%Y-%m-%d (%A)")

    response = await _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(today=today)},
            {"role": "user", "content": message}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)

    return ParsedIntent(
        date=parsed.get("date"),
        time=parsed.get("time"),
        slot_preference=parsed.get("slot_preference"),
        raw_message=message
    )

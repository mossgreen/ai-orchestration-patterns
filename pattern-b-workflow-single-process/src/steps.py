"""
Workflow steps for Pattern B.

Step 1: IntentParserStep - Extract date/time from natural language
Step 2: AvailabilityStep - Check available slots
Step 3: BookingStep - Create reservation
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .models import ParsedIntent, SlotInfo, BookingResult

# Load .env from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from shared.booking_service import get_booking_service


INTENT_PARSER_PROMPT = """You are a booking intent parser. Extract booking details from user messages.

Today's date is {today}.

Return a JSON object with:
- date: extracted date in YYYY-MM-DD format (null if not specified)
- time: extracted time in HH:MM format (null if not specified)

Handle relative dates like "tomorrow", "next Monday", "this weekend", etc.
Handle time ranges like "afternoon" (14:00), "morning" (09:00), "evening" (17:00).

Examples:
- "Book tomorrow at 3pm" -> {{"date": "2024-01-16", "time": "15:00"}}
- "I need a court next Monday" -> {{"date": "2024-01-22", "time": null}}
- "Book for the afternoon" -> {{"date": null, "time": "14:00"}}

Return ONLY valid JSON, no other text."""


class IntentParserStep:
    """Step 1: Parse natural language to extract booking intent."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI()

    async def parse(self, message: str) -> ParsedIntent:
        if not message:
            raise ValueError("No message provided")

        today = datetime.now().strftime("%Y-%m-%d")
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": INTENT_PARSER_PROMPT.format(today=today)},
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
            raw_message=message
        )


class AvailabilityStep:
    """Step 2: Check tennis court availability."""

    def __init__(self) -> None:
        self._booking_service = get_booking_service()

    def check(self, intent: ParsedIntent) -> list[SlotInfo]:
        raw_slots = self._booking_service.check_availability(
            date=intent.date,
            time=intent.time
        )

        return [
            SlotInfo(
                slot_id=slot["slot_id"],
                court=slot["court"],
                date=slot["date"],
                time=slot["time"]
            )
            for slot in raw_slots
        ]


class BookingStep:
    """Step 3: Book a tennis court slot."""

    def __init__(self) -> None:
        self._booking_service = get_booking_service()

    def book(self, slot: SlotInfo) -> BookingResult:
        result = self._booking_service.book(slot.slot_id)

        if not result["success"]:
            raise ValueError(f"Booking failed: {result['error']}")

        return BookingResult(
            booking_id=result["booking_id"],
            court=result["court"],
            date=result["date"],
            time=result["time"],
            message=(
                f"Booking confirmed!\n"
                f"  Booking ID: {result['booking_id']}\n"
                f"  Court: {result['court']}\n"
                f"  Date: {result['date']}\n"
                f"  Time: {result['time']}"
            )
        )

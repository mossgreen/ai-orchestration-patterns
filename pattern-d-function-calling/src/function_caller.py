"""Function caller for Pattern D: LLM decides which functions to call."""

import json
import logging
from datetime import datetime
from typing import Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageToolCall

from shared import BookingService

from .settings import Settings, get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful tennis court booking assistant.
You help users check availability and book tennis courts.

Today's date is {today}.

When the user wants to book:
1. First check availability for the requested date/time
2. Present the available slots to the user
3. If the user confirms or you can infer their preference, book the slot

Always be helpful and confirm bookings with full details."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available tennis court slots for a given date and optional time",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format",
                    },
                    "time": {
                        "type": "string",
                        "description": "Optional time in HH:MM format to filter slots",
                    },
                },
                "required": ["date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book",
            "description": "Book a specific tennis court slot",
            "parameters": {
                "type": "object",
                "properties": {
                    "slot_id": {
                        "type": "string",
                        "description": "The unique slot ID to book",
                    },
                },
                "required": ["slot_id"],
            },
        },
    },
]


def _execute_tool(
    tool_call: ChatCompletionMessageToolCall,
    booking_service: BookingService,
) -> str:
    """Execute a tool call and return the result as a string."""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    logger.info("Executing tool: %s with args: %s", name, args)

    if name == "check_availability":
        slots = booking_service.check_availability(
            date=args["date"],
            time=args.get("time"),
        )
        if not slots:
            return "No available slots found for the requested date/time."

        result = f"Found {len(slots)} available slots:\n"
        for slot in slots:
            result += f"- {slot.slot_id}: {slot.court} at {slot.time}\n"
        return result

    elif name == "book":
        booking = booking_service.book(slot_id=args["slot_id"])
        return (
            f"Booking confirmed! "
            f"Booking ID: {booking.booking_id}, "
            f"Court: {booking.court}, "
            f"Date: {booking.date}, "
            f"Time: {booking.time}"
        )

    else:
        return f"Unknown function: {name}"


async def call(
    message: str,
    booking_service: BookingService,
    client: AsyncOpenAI | None = None,
    settings: Settings | None = None,
) -> str:
    """
    Process a user message using function calling.

    The LLM decides which functions to call in a loop until the task is complete.
    """
    settings = settings or get_settings()
    client = client or AsyncOpenAI(api_key=settings.get_openai_api_key())

    today = datetime.now().strftime("%Y-%m-%d")
    system_prompt = SYSTEM_PROMPT.format(today=today)

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    while True:
        logger.debug("Calling OpenAI with %d messages", len(messages))

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=TOOLS,
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            logger.info("No more tool calls, returning response")
            return assistant_message.content or ""

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            result = _execute_tool(tool_call, booking_service)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

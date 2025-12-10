"""
Pattern E: Single Agent - Tennis Court Booking

The agent autonomously manages the conversation loop, deciding when to:
- Check availability
- Book a slot
- Ask for clarification

Key difference from Pattern D: The agent controls the loop, not your code.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from agents import Agent, Runner, RunContextWrapper, function_tool

# Load .env from project root
load_dotenv(Path(__file__).parents[2] / ".env")

# Add parent directory to path for shared imports
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])
from shared.booking_service import get_booking_service


# Initialize the booking service
booking_service = get_booking_service()


@function_tool
def check_availability(date: str, time: Optional[str] = None) -> str:
    """
    Check available tennis court slots for a given date.

    Args:
        date: Date to check in YYYY-MM-DD format (e.g., "2024-12-15")
        time: Optional specific time in HH:MM format (e.g., "14:00")

    Returns:
        Available slots or a message if none found
    """
    slots = booking_service.check_availability(date, time)

    if not slots:
        return f"No available slots found for {date}" + (f" at {time}" if time else "")

    result = f"Available slots for {date}:\n"
    for slot in slots:
        result += f"  - {slot['court']} at {slot['time']} (ID: {slot['slot_id']})\n"

    return result


@function_tool
def book_slot(slot_id: str, user_id: str = "guest") -> str:
    """
    Book a specific tennis court slot.

    Args:
        slot_id: The slot ID from check_availability results
        user_id: User making the booking (defaults to "guest")

    Returns:
        Booking confirmation or error message
    """
    result = booking_service.book(slot_id, user_id)

    if result["success"]:
        return (
            f"Booking confirmed!\n"
            f"  Booking ID: {result['booking_id']}\n"
            f"  Court: {result['court']}\n"
            f"  Date: {result['date']}\n"
            f"  Time: {result['time']}"
        )
    else:
        return f"Booking failed: {result['error']}"


def get_instructions(
    context: RunContextWrapper[Any], agent: Agent[Any]
) -> str:
    """Generate dynamic instructions with current datetime."""
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M (%A)")

    return f"""You are a helpful tennis court booking assistant. Your job is to help users:

1. Find available tennis court slots
2. Book slots for them

CURRENT DATETIME: {current_datetime}

WORKFLOW:
- When a user wants to book, FIRST check availability for their preferred date/time
- Present the available options clearly
- If they confirm a slot, book it using the slot_id
- Always confirm the booking details

GUIDELINES:
- Convert relative dates ("tomorrow", "next Monday") to YYYY-MM-DD format
- If no time is specified, show all available slots for that day
- Be concise but friendly
- Always use the tools to check real availability - don't make up slots

IMPORTANT: You control the conversation flow. Decide autonomously when to check availability vs when to book."""


# Create the booking agent
booking_agent = Agent(
    name="Tennis Court Booking Agent",
    instructions=get_instructions,
    tools=[check_availability, book_slot],
)


async def run_agent(user_message: str) -> str:
    """
    Run the booking agent with a user message.

    Args:
        user_message: The user's request

    Returns:
        The agent's response
    """
    result = await Runner.run(booking_agent, user_message)
    return result.final_output


def run_agent_sync(user_message: str) -> str:
    """
    Synchronous version for simpler use cases.

    Args:
        user_message: The user's request

    Returns:
        The agent's response
    """
    result = Runner.run_sync(booking_agent, user_message)
    return result.final_output

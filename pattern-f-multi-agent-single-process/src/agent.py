"""
Pattern F: Multi-Agent (Shared Runtime) - Tennis Court Booking

A manager agent routes requests to specialized agents:
- Availability Specialist: Checks available slots
- Booking Specialist: Books confirmed slots

Key difference from Pattern E: Multiple focused agents instead of one agent with multiple tools.
"""

import os
from datetime import datetime
from typing import Any, Optional

from agents import Agent, Runner, RunContextWrapper, function_tool

from .settings import get_settings
from shared import create_booking_service

# Set OpenAI API key for the Agents SDK
settings = get_settings()
os.environ["OPENAI_API_KEY"] = settings.get_openai_api_key()

# Initialize the booking service
booking_service = create_booking_service()


# =============================================================================
# Tools for Specialist Agents
# =============================================================================


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
        result += f"  - {slot.court} at {slot.time} (ID: {slot.slot_id})\n"

    return result


@function_tool
def book_slot(slot_id: str) -> str:
    """
    Book a specific tennis court slot.

    Args:
        slot_id: The slot ID from check_availability results

    Returns:
        Booking confirmation or error message
    """
    try:
        booking = booking_service.book(slot_id)
        return (
            f"Booking confirmed!\n"
            f"  Booking ID: {booking.booking_id}\n"
            f"  Court: {booking.court}\n"
            f"  Date: {booking.date}\n"
            f"  Time: {booking.time}"
        )
    except Exception as e:
        return f"Booking failed: {e}"


# =============================================================================
# Specialist Agents
# =============================================================================


def get_availability_instructions(
    context: RunContextWrapper[Any], agent: Agent[Any]
) -> str:
    """Instructions for the Availability Specialist."""
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M (%A)")

    return f"""You are the Availability Specialist for tennis court bookings.

CURRENT DATETIME: {current_datetime}

YOUR ROLE:
- Check tennis court availability for requested dates/times
- Present available slots clearly to users
- Convert relative dates ("tomorrow", "next Monday") to YYYY-MM-DD format

GUIDELINES:
- Always use the check_availability tool - never make up slots
- If no time specified, show all available slots for the day
- Be concise and helpful
- After showing availability, let the user know they can book a slot"""


def get_booking_instructions(
    context: RunContextWrapper[Any], agent: Agent[Any]
) -> str:
    """Instructions for the Booking Specialist."""
    return """You are the Booking Specialist for tennis court bookings.

YOUR ROLE:
- Book tennis court slots when users confirm their choice
- You need a slot_id to make a booking

GUIDELINES:
- Use the book_slot tool with the provided slot_id
- Confirm booking details after successful booking
- If booking fails, explain the error clearly"""


availability_agent = Agent(
    name="Availability Specialist",
    instructions=get_availability_instructions,
    tools=[check_availability],
)


booking_agent = Agent(
    name="Booking Specialist",
    instructions=get_booking_instructions,
    tools=[book_slot],
)


# =============================================================================
# Manager Agent
# =============================================================================


def get_manager_instructions(
    context: RunContextWrapper[Any], agent: Agent[Any]
) -> str:
    """Instructions for the Manager Agent."""
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M (%A)")

    return f"""You are the Tennis Court Booking Manager. Your job is to route user requests to the right specialist.

CURRENT DATETIME: {current_datetime}

AVAILABLE SPECIALISTS:
1. Availability Specialist - Checks available tennis court slots
2. Booking Specialist - Books a specific slot (needs slot_id)

ROUTING RULES:
- User asks about availability, times, dates, or what's open → Hand off to Availability Specialist
- User wants to book a specific slot (provides slot_id) → Hand off to Booking Specialist
- User request is unclear → Ask clarifying questions first

WORKFLOW:
1. User typically starts by asking about availability
2. Availability Specialist shows options
3. User picks a slot and wants to book
4. Booking Specialist completes the booking

Be helpful and route requests efficiently."""


manager_agent = Agent(
    name="Tennis Court Booking Manager",
    instructions=get_manager_instructions,
    handoffs=[availability_agent, booking_agent],
)


# =============================================================================
# Runner Functions
# =============================================================================


async def run_manager(user_message: str) -> str:
    """
    Run the manager agent with a user message.

    Args:
        user_message: The user's request

    Returns:
        The final response after routing and specialist handling
    """
    result = await Runner.run(manager_agent, user_message)
    return result.final_output


def run_manager_sync(user_message: str) -> str:
    """
    Synchronous version for simpler use cases.

    Args:
        user_message: The user's request

    Returns:
        The final response after routing and specialist handling
    """
    result = Runner.run_sync(manager_agent, user_message)
    return result.final_output

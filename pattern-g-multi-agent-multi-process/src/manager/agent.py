"""
Manager Agent - Pattern G: Multi-Agent Multi-Process

Routes requests to specialist services via HTTP.
Key difference from Pattern F: Uses HTTP calls instead of in-process handoffs.
"""

import os
from datetime import datetime
from typing import Any, Optional

import httpx
from agents import Agent, Runner, RunContextWrapper, function_tool

from ..settings import get_settings

# Set OpenAI API key for the Agents SDK
settings = get_settings()
os.environ["OPENAI_API_KEY"] = settings.get_openai_api_key()


# =============================================================================
# HTTP Tools - Call Specialist Services
# =============================================================================


@function_tool
def check_availability(date: str, time: Optional[str] = None) -> str:
    """
    Check available tennis court slots by calling the Availability Specialist service.

    Args:
        date: Date to check in YYYY-MM-DD format (e.g., "2024-12-15")
        time: Optional specific time in HH:MM format (e.g., "14:00")

    Returns:
        Available slots or a message if none found
    """
    availability_url = settings.availability_url
    if not availability_url:
        return "Error: Availability service URL not configured"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{availability_url}/process",
                json={"date": date, "time": time},
            )
            response.raise_for_status()
            return response.json()["result"]
    except httpx.HTTPError as e:
        return f"Error calling availability service: {e}"


@function_tool
def book_slot(slot_id: str) -> str:
    """
    Book a tennis court slot by calling the Booking Specialist service.

    Args:
        slot_id: The slot ID from check_availability results

    Returns:
        Booking confirmation or error message
    """
    booking_url = settings.booking_url
    if not booking_url:
        return "Error: Booking service URL not configured"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{booking_url}/process",
                json={"slot_id": slot_id},
            )
            response.raise_for_status()
            return response.json()["result"]
    except httpx.HTTPError as e:
        return f"Error calling booking service: {e}"


# =============================================================================
# Manager Agent
# =============================================================================


def get_manager_instructions(
    context: RunContextWrapper[Any], agent: Agent[Any]
) -> str:
    """Instructions for the Manager Agent."""
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M (%A)")

    return f"""You are the Tennis Court Booking Manager. Your job is to help users book tennis courts.

CURRENT DATETIME: {current_datetime}

AVAILABLE ACTIONS:
1. check_availability - Check what tennis court slots are available (calls Availability Service)
2. book_slot - Book a specific slot by ID (calls Booking Service)

WORKFLOW:
1. When a user wants to book, FIRST check availability for their preferred date/time
2. Present the available options clearly with their slot IDs
3. If they confirm a slot, book it using the slot_id
4. Always confirm the booking details

GUIDELINES:
- Convert relative dates ("tomorrow", "next Monday") to YYYY-MM-DD format
- If no time is specified, show all available slots for that day
- Be concise but friendly
- Always use the tools to check real availability - don't make up slots

IMPORTANT: You control the conversation flow. Decide when to check availability vs when to book.
Each tool call goes to a separate specialist service via HTTP - this is Pattern G (multi-process)."""


manager_agent = Agent(
    name="Tennis Court Booking Manager",
    instructions=get_manager_instructions,
    tools=[check_availability, book_slot],
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
        The final response after routing to specialist services
    """
    result = await Runner.run(manager_agent, user_message)
    return result.final_output


def run_manager_sync(user_message: str) -> str:
    """
    Synchronous version for simpler use cases.

    Args:
        user_message: The user's request

    Returns:
        The final response after routing to specialist services
    """
    result = Runner.run_sync(manager_agent, user_message)
    return result.final_output

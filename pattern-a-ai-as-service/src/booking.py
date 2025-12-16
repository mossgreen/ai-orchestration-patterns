"""
Pattern A: YOUR Business Logic - No AI Here

This module contains YOUR hardcoded business logic.
NO AI is involved here - you control everything.

This is the key point of Pattern A:
- LLM only parses text into structured data (in parser.py)
- YOU write all the business logic (here)
- Full control, full auditability, no "black box" behavior
"""

import sys
from pathlib import Path

# Setup paths for imports
_src_dir = Path(__file__).parent
sys.path.insert(0, str(_src_dir))
sys.path.insert(0, str(_src_dir.parent.parent))

from models import ParsedIntent
from shared.booking_service import get_booking_service


# Initialize the booking service
_booking_service = get_booking_service()


def process_booking(intent: ParsedIntent) -> str:
    """
    Process a booking request using YOUR hardcoded logic.

    NO AI IS INVOLVED IN THIS FUNCTION.

    This is the key insight of Pattern A:
    - The AI already parsed the user's message (in parser.py)
    - Now YOUR code handles all the business logic
    - You have full control over what happens

    Args:
        intent: The parsed intent from the LLM (date, time extracted)

    Returns:
        Human-readable response (confirmation or error message)
    """
    # ============================================================
    # YOUR CODE: Check availability
    # ============================================================
    slots = _booking_service.check_availability(intent.date, intent.time)

    if not slots:
        date_str = intent.date or "your requested date"
        time_str = f" at {intent.time}" if intent.time else ""
        return f"Sorry, no tennis courts are available for {date_str}{time_str}. Please try a different date or time."

    # ============================================================
    # YOUR CODE: Select slot based on user preference
    # ============================================================
    if intent.slot_preference:
        # User specified a preference (1=first, 2=second, etc.)
        # Clamp to available slots if out of bounds
        index = min(intent.slot_preference - 1, len(slots) - 1)
        selected_slot = slots[index]
    else:
        # Default to first available
        selected_slot = slots[0]

    # ============================================================
    # YOUR CODE: Book the slot
    # ============================================================
    result = _booking_service.book(selected_slot["slot_id"])

    if not result["success"]:
        return f"Sorry, booking failed: {result['error']}"

    # ============================================================
    # YOUR CODE: Return confirmation
    # ============================================================
    return (
        f"Booking confirmed!\n"
        f"  Booking ID: {result['booking_id']}\n"
        f"  Court: {result['court']}\n"
        f"  Date: {result['date']}\n"
        f"  Time: {result['time']}"
    )

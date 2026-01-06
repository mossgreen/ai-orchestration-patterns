"""
Availability Specialist Agent - Pattern G

Runs as a separate service, handles availability queries.
"""

from datetime import datetime
from typing import Optional

from shared import create_booking_service

# Initialize the booking service
booking_service = create_booking_service()


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


def process_availability_request(date: str, time: Optional[str] = None) -> str:
    """
    Process an availability request.

    This is the main entry point for the availability specialist.
    """
    return check_availability(date, time)

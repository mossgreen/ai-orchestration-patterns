"""
Pattern A: YOUR Business Logic - No AI Here

This module contains YOUR hardcoded business logic.
NO AI is involved here - you control everything.

This is the key point of Pattern A:
- LLM only parses text into structured data (in parser.py)
- YOU write all the business logic (here)
- Full control, full auditability, no "black box" behavior
"""

import logging

from shared import Booking, BookingService, Slot, create_booking_service

from .exceptions import InvalidSlotPreferenceError, NoSlotsAvailableError
from .models import ParsedIntent

logger = logging.getLogger(__name__)


def process_booking(
    intent: ParsedIntent,
    *,
    booking_service: BookingService | None = None,
) -> str:
    """
    Process a booking request using YOUR hardcoded logic.

    NO AI IS INVOLVED IN THIS FUNCTION.

    Args:
        intent: The parsed intent from the LLM (date, time extracted)
        booking_service: Booking service (injected for testing)

    Returns:
        Human-readable response (confirmation or error message)

    Raises:
        NoSlotsAvailableError: If no slots match the criteria
        InvalidSlotPreferenceError: If requested slot number exceeds available
    """
    service = booking_service or create_booking_service()

    logger.info("Processing booking: date=%s, time=%s", intent.date, intent.time)

    # Check availability
    slots = service.check_availability(intent.date or "", intent.time)

    if not slots:
        date_str = intent.date or "your requested date"
        raise NoSlotsAvailableError(date_str, intent.time)

    # Select slot based on user preference
    selected_slot = _select_slot(slots, intent.slot_preference)

    # Book the slot
    booking = service.book(selected_slot.slot_id)

    logger.info("Booking confirmed: %s", booking.booking_id)

    return _format_confirmation(booking)


def _select_slot(slots: list[Slot], preference: int | None) -> Slot:
    """
    Select a slot based on user preference.

    Args:
        slots: Available slots (non-empty)
        preference: User's preferred slot number (1=first, 2=second, etc.)

    Returns:
        Selected Slot

    Raises:
        InvalidSlotPreferenceError: If preference exceeds available slots
    """
    if preference is None:
        return slots[0]

    if preference > len(slots):
        raise InvalidSlotPreferenceError(requested=preference, available=len(slots))

    return slots[preference - 1]


def _format_confirmation(booking: Booking) -> str:
    """Format a booking confirmation message."""
    return (
        f"Booking confirmed!\n"
        f"  Booking ID: {booking.booking_id}\n"
        f"  Court: {booking.court}\n"
        f"  Date: {booking.date}\n"
        f"  Time: {booking.time}"
    )

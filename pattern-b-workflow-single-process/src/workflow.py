"""
Workflow for Pattern B: Fixed sequence orchestration.

The workflow defines a predetermined sequence of steps.
AI assists within steps but doesn't decide the flow.
"""

import logging

from shared import Booking, BookingService

from .intent_parser import IntentParser
from .models import ParsedIntent

logger = logging.getLogger(__name__)


class Workflow:
    """
    Booking workflow with fixed sequence.

    Steps:
    1. Parse intent (extract date/time from message)
    2. Check availability (find matching slots)
    3. Book first available slot
    """

    def __init__(
        self,
        intent_parser: IntentParser,
        booking_service: BookingService,
    ) -> None:
        self._intent_parser = intent_parser
        self._booking_service = booking_service

    async def run(self, message: str) -> str:
        """Execute the workflow in fixed sequence."""
        logger.info("Workflow started: %s", message[:50])

        # Step 1: Parse intent
        logger.debug("Step 1: Parsing intent")
        intent: ParsedIntent = await self._intent_parser.parse(message)
        logger.info("Intent parsed: date=%s, time=%s", intent.date, intent.time)

        # Step 2: Check availability
        logger.debug("Step 2: Checking availability")
        slots = self._booking_service.check_availability(
            date=intent.date or "",
            time=intent.time,
        )
        logger.debug("Found %d available slots", len(slots))

        if not slots:
            logger.warning("No slots available for date=%s, time=%s", intent.date, intent.time)
            return f"No slots available for {intent.date} {intent.time or ''}".strip()

        # Step 3: Book first available slot
        logger.debug("Step 3: Booking slot")
        logger.debug("Selected slot: %s", slots[0].slot_id)
        booking: Booking = self._booking_service.book(slots[0].slot_id)

        logger.info("Workflow completed: booking_id=%s", booking.booking_id)

        return (
            f"Booked {booking.court} on {booking.date} at {booking.time}. "
            f"Booking ID: {booking.booking_id}"
        )

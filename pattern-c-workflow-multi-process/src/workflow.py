"""
Workflow for Pattern C.

Coordinates the fixed sequence of independent services:
1. Intent Parser -> 2. Availability Checker -> 3. Booking Handler

Each service is independent and could be deployed separately.
The workflow handles state passing between services.
"""

import logging

from shared import BookingService, create_booking_service

from .exceptions import AvailabilityError, BookingError, ParseError
from .services import AvailabilityService, BookingHandlerService, IntentParserService

logger = logging.getLogger(__name__)


class Workflow:
    """
    Booking workflow with fixed sequence of independent services.

    Steps:
    1. Parse user intent (extract date/time)
    2. Check availability (find matching slots)
    3. Book slot (create reservation)
    """

    def __init__(
        self,
        *,
        intent_parser: IntentParserService | None = None,
        availability_checker: AvailabilityService | None = None,
        booking_handler: BookingHandlerService | None = None,
        booking_service: BookingService | None = None,
    ) -> None:
        """Initialize workflow with optional dependency injection."""
        self._intent_parser = intent_parser or IntentParserService()

        # Create shared BookingService for services 2 and 3
        # This ensures slot found in availability check can be booked
        shared_service = booking_service or create_booking_service()

        # Inject shared service if using default services
        if availability_checker is None:
            self._availability_checker = AvailabilityService(
                booking_service=shared_service
            )
        else:
            self._availability_checker = availability_checker

        if booking_handler is None:
            self._booking_handler = BookingHandlerService(
                booking_service=shared_service
            )
        else:
            self._booking_handler = booking_handler

    async def run(self, user_message: str) -> str:
        """
        Execute the complete booking workflow.

        Args:
            user_message: Natural language booking request

        Returns:
            Human-readable response (confirmation or error)

        Raises:
            ParseError: If intent parsing fails
            AvailabilityError: If availability check fails
            BookingError: If booking fails
        """
        logger.info("Workflow started: %s", user_message[:50])

        # Step 1: Parse Intent
        logger.debug("Step 1: %s", self._intent_parser.name)
        intent_response = await self._intent_parser.execute({"message": user_message})

        if not intent_response.success:
            raise ParseError(intent_response.error or "Unknown error")

        intent = intent_response.data
        logger.debug("Parsed: date=%s, time=%s", intent.date, intent.time)

        # Step 2: Check Availability
        logger.debug("Step 2: %s", self._availability_checker.name)
        availability_response = await self._availability_checker.execute({
            "intent": intent.model_dump()
        })

        if not availability_response.success:
            raise AvailabilityError(availability_response.error or "Unknown error")

        availability = availability_response.data
        logger.debug("Found %d slots", len(availability.slots))

        if not availability.slots:
            return availability.message

        # Auto-select first available slot
        selected_slot = availability.slots[0]
        logger.debug("Selected: %s at %s", selected_slot.court, selected_slot.time)

        # Step 3: Book Slot
        logger.debug("Step 3: %s", self._booking_handler.name)
        booking_response = await self._booking_handler.execute({
            "slot": selected_slot.model_dump()
        })

        if not booking_response.success:
            raise BookingError(booking_response.error or "Unknown error")

        booking = booking_response.data
        logger.info("Workflow completed: %s", booking.booking_id)

        return booking.message


async def run_workflow(user_message: str) -> str:
    """Run the booking workflow for a user message."""
    workflow = Workflow()
    return await workflow.run(user_message)
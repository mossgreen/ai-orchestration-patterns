"""
Service 3: Booking Handler

Creates bookings for selected slots.
Uses the shared BookingService for persistence.
"""

import logging
from typing import Any

from shared import (
    Booking,
    BookingService,
    SlotNotAvailableError,
    SlotNotFoundError,
    create_booking_service,
)

from ..models import BookingResult, ServiceResponse, SlotInfo
from .base import BaseService

logger = logging.getLogger(__name__)


class BookingHandlerService(BaseService):
    """
    Handles slot booking requests.
    This service could be deployed as its own Lambda function.
    """

    def __init__(self, *, booking_service: BookingService | None = None) -> None:
        self._booking_service = booking_service or create_booking_service()

    @property
    def name(self) -> str:
        return "BookingHandler"

    async def execute(self, request: dict[str, Any]) -> ServiceResponse[BookingResult]:
        """
        Book a selected slot.

        Args:
            request: {"slot": SlotInfo} - The slot to book

        Returns:
            ServiceResponse containing BookingResult
        """
        slot_data = request.get("slot")

        if not slot_data:
            logger.warning("No slot provided for booking")
            return ServiceResponse(success=False, error="No slot provided for booking")

        # Convert dict to SlotInfo if needed
        if isinstance(slot_data, dict):
            slot = SlotInfo(**slot_data)
        else:
            slot = slot_data

        logger.debug("Booking slot: %s", slot.slot_id)

        try:
            # booking_service.book() now returns Booking object and raises on error
            booking: Booking = self._booking_service.book(slot.slot_id)

            booking_result = BookingResult(
                booking_id=booking.booking_id,
                court=booking.court,
                date=booking.date,
                time=booking.time,
                message=(
                    f"Booking confirmed! Your reservation:\n"
                    f"- Booking ID: {booking.booking_id}\n"
                    f"- Court: {booking.court}\n"
                    f"- Date: {booking.date}\n"
                    f"- Time: {booking.time}"
                ),
            )

            logger.info("Booking confirmed: %s", booking.booking_id)
            return ServiceResponse(success=True, data=booking_result)

        except SlotNotFoundError as e:
            logger.warning("Slot not found: %s", e)
            return ServiceResponse(success=False, error=str(e))

        except SlotNotAvailableError as e:
            logger.warning("Slot not available: %s", e)
            return ServiceResponse(success=False, error=str(e))

        except Exception as e:
            logger.error("Booking failed: %s", e)
            return ServiceResponse(success=False, error=f"Booking failed: {e}")

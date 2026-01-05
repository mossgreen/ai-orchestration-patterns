"""
Service 2: Availability Checker

Queries available tennis court slots based on parsed intent.
Uses the shared BookingService for data access.
"""

import logging
from datetime import datetime
from typing import Any

from shared import BookingService, Slot, create_booking_service

from ..models import AvailabilityResult, ParsedIntent, ServiceResponse, SlotInfo
from .base import BaseService

logger = logging.getLogger(__name__)


class AvailabilityService(BaseService):
    """
    Checks slot availability based on parsed booking intent.
    This service could be deployed as its own Lambda function.
    """

    def __init__(self, *, booking_service: BookingService | None = None) -> None:
        self._booking_service = booking_service or create_booking_service()

    @property
    def name(self) -> str:
        return "AvailabilityChecker"

    async def execute(self, request: dict[str, Any]) -> ServiceResponse[AvailabilityResult]:
        """
        Find available slots matching the booking intent.

        Args:
            request: {"intent": ParsedIntent} - Parsed booking intent

        Returns:
            ServiceResponse containing AvailabilityResult
        """
        intent_data = request.get("intent")
        if not intent_data:
            logger.warning("No intent data provided")
            return ServiceResponse(success=False, error="No intent data provided")

        # Convert dict to ParsedIntent if needed
        if isinstance(intent_data, dict):
            intent = ParsedIntent(**intent_data)
        else:
            intent = intent_data

        # Use today if no date specified
        date = intent.date or datetime.now().strftime("%Y-%m-%d")
        time = intent.time

        logger.debug("Checking availability for date=%s, time=%s", date, time)

        try:
            # booking_service now returns list[Slot] objects, not dicts
            available_slots: list[Slot] = self._booking_service.check_availability(date, time)

            # Convert Slot objects to SlotInfo models
            slots = [
                SlotInfo(
                    slot_id=slot.slot_id,
                    court=slot.court,
                    date=slot.date,
                    time=slot.time,
                    duration_minutes=slot.duration_minutes,
                )
                for slot in available_slots
            ]

            # Build human-readable message
            if slots:
                time_filter = f" at {time}" if time else ""
                message = f"Found {len(slots)} available slot(s) on {date}{time_filter}."
            else:
                message = f"No available slots found for {date}."

            logger.info("Found %d available slots", len(slots))
            result = AvailabilityResult(slots=slots, message=message)
            return ServiceResponse(success=True, data=result)

        except Exception as e:
            logger.error("Availability check failed: %s", e)
            return ServiceResponse(success=False, error=f"Availability check failed: {e}")

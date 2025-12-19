"""
Shared booking service for tennis court reservations.
Used across all orchestration patterns as the core business logic.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class BookingError(Exception):
    """Base exception for booking operations."""


class SlotNotFoundError(BookingError):
    """Requested slot does not exist."""

    def __init__(self, slot_id: str) -> None:
        self.slot_id = slot_id
        super().__init__(f"Slot '{slot_id}' not found")


class SlotNotAvailableError(BookingError):
    """Requested slot is already booked."""

    def __init__(self, slot_id: str) -> None:
        self.slot_id = slot_id
        super().__init__(f"Slot '{slot_id}' is already booked")


@dataclass
class Slot:
    """A bookable time slot."""

    slot_id: str
    court: str
    date: str
    time: str
    duration_minutes: int = 60
    is_available: bool = True


@dataclass
class Booking:
    """A confirmed booking."""

    booking_id: str
    slot_id: str
    court: str
    date: str
    time: str
    status: str = "confirmed"


class BookingService:
    """
    In-memory mock booking service for tennis courts.
    Simulates a real booking system with availability checks and reservations.
    """

    def __init__(self) -> None:
        self._slots: dict[str, Slot] = {}
        self._bookings: dict[str, Booking] = {}
        self._booking_counter: int = 0
        self._initialize_mock_data()

    def _initialize_mock_data(self) -> None:
        """Generate mock slots for the next 7 days."""
        courts = ["Court A", "Court B", "Court C"]
        times = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]

        today = datetime.now()
        for day_offset in range(7):
            date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            for court in courts:
                for time in times:
                    slot_id = f"{date}_{court.replace(' ', '')}_{time.replace(':', '')}"
                    self._slots[slot_id] = Slot(
                        slot_id=slot_id,
                        court=court,
                        date=date,
                        time=time,
                    )

        # Mark some slots as already booked for realism
        sample_booked = list(self._slots.keys())[:5]
        for slot_id in sample_booked:
            self._slots[slot_id].is_available = False

    def check_availability(self, date: str, time: Optional[str] = None) -> list[Slot]:
        """
        Check available slots for a given date and optional time.

        Args:
            date: Date in YYYY-MM-DD format
            time: Optional time in HH:MM format to filter specific slots

        Returns:
            List of available Slot objects, sorted by time then court
        """
        available: list[Slot] = []
        for slot in self._slots.values():
            if slot.date == date and slot.is_available:
                if time is None or slot.time == time:
                    available.append(slot)

        available.sort(key=lambda s: (s.time, s.court))
        logger.debug("Found %d available slots for %s", len(available), date)
        return available

    def book(self, slot_id: str) -> Booking:
        """
        Book a specific slot.

        Args:
            slot_id: The unique identifier of the slot to book

        Returns:
            Booking confirmation

        Raises:
            SlotNotFoundError: If the slot doesn't exist
            SlotNotAvailableError: If the slot is already booked
        """
        if slot_id not in self._slots:
            logger.warning("Attempted to book non-existent slot: %s", slot_id)
            raise SlotNotFoundError(slot_id)

        slot = self._slots[slot_id]
        if not slot.is_available:
            logger.warning("Attempted to book unavailable slot: %s", slot_id)
            raise SlotNotAvailableError(slot_id)

        # Create booking
        self._booking_counter += 1
        booking_id = f"BK{self._booking_counter:04d}"

        booking = Booking(
            booking_id=booking_id,
            slot_id=slot_id,
            court=slot.court,
            date=slot.date,
            time=slot.time,
        )

        # Update slot and store booking
        slot.is_available = False
        self._bookings[booking_id] = booking

        logger.info(
            "Booking confirmed: %s for %s on %s at %s",
            booking_id,
            slot.court,
            slot.date,
            slot.time,
        )
        return booking

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Retrieve booking details by ID."""
        return self._bookings.get(booking_id)


# Factory function for dependency injection
def create_booking_service() -> BookingService:
    """Create a new BookingService instance."""
    return BookingService()

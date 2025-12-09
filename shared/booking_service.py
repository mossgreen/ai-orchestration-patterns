"""
Shared booking service for tennis court reservations.
Used across all orchestration patterns as the core business logic.
"""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Slot:
    slot_id: str
    court: str
    date: str
    time: str
    duration_minutes: int = 60
    is_available: bool = True
    booked_by: Optional[str] = None


@dataclass
class Booking:
    booking_id: str
    slot_id: str
    user_id: str
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
            self._slots[slot_id].booked_by = "existing_user"

    def check_availability(self, date: str, time: Optional[str] = None) -> list[dict]:
        """
        Check available slots for a given date and optional time.

        Args:
            date: Date in YYYY-MM-DD format
            time: Optional time in HH:MM format to filter specific slots

        Returns:
            List of available slots with their details
        """
        available = []
        for slot in self._slots.values():
            if slot.date == date and slot.is_available:
                if time is None or slot.time == time:
                    available.append({
                        "slot_id": slot.slot_id,
                        "court": slot.court,
                        "date": slot.date,
                        "time": slot.time,
                        "duration_minutes": slot.duration_minutes,
                    })

        # Sort by time, then by court
        available.sort(key=lambda x: (x["time"], x["court"]))
        return available

    def book(self, slot_id: str, user_id: str) -> dict:
        """
        Book a specific slot for a user.

        Args:
            slot_id: The unique identifier of the slot to book
            user_id: The user making the booking

        Returns:
            Booking confirmation with details
        """
        if slot_id not in self._slots:
            return {
                "success": False,
                "error": f"Slot {slot_id} not found",
            }

        slot = self._slots[slot_id]
        if not slot.is_available:
            return {
                "success": False,
                "error": f"Slot {slot_id} is already booked",
            }

        # Create booking
        self._booking_counter += 1
        booking_id = f"BK{self._booking_counter:04d}"

        booking = Booking(
            booking_id=booking_id,
            slot_id=slot_id,
            user_id=user_id,
            court=slot.court,
            date=slot.date,
            time=slot.time,
        )

        # Update slot and store booking
        slot.is_available = False
        slot.booked_by = user_id
        self._bookings[booking_id] = booking

        return {
            "success": True,
            "booking_id": booking_id,
            "court": slot.court,
            "date": slot.date,
            "time": slot.time,
            "message": f"Successfully booked {slot.court} on {slot.date} at {slot.time}",
        }

    def get_booking(self, booking_id: str) -> Optional[dict]:
        """Retrieve booking details by ID."""
        if booking_id not in self._bookings:
            return None

        booking = self._bookings[booking_id]
        return {
            "booking_id": booking.booking_id,
            "court": booking.court,
            "date": booking.date,
            "time": booking.time,
            "user_id": booking.user_id,
            "status": booking.status,
        }


# Singleton instance for use across the application
_service_instance: Optional[BookingService] = None


def get_booking_service() -> BookingService:
    """Get or create the singleton booking service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = BookingService()
    return _service_instance

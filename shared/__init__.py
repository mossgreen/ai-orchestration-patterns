"""Shared services for AI orchestration patterns."""

from pathlib import Path

from .booking_service import (
    Booking,
    BookingError,
    BookingService,
    Slot,
    SlotNotAvailableError,
    SlotNotFoundError,
    create_booking_service,
)

def get_env_file() -> Path | None:
    """Find .env file by searching up from current working directory."""
    current = Path.cwd()
    for _ in range(5):
        env_path = current / ".env"
        if env_path.exists():
            return env_path
        current = current.parent
    return None


__all__ = [
    "Booking",
    "BookingError",
    "BookingService",
    "Slot",
    "SlotNotAvailableError",
    "SlotNotFoundError",
    "create_booking_service",
    "get_env_file",
]

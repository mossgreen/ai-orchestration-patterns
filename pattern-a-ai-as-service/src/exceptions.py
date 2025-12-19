"""Custom exceptions for Pattern A."""


class PatternAError(Exception):
    """Base exception for Pattern A."""


class ParseError(PatternAError):
    """Failed to parse user intent."""


class BookingError(PatternAError):
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


class NoSlotsAvailableError(BookingError):
    """No slots available for the requested date/time."""

    def __init__(self, date: str, time: str | None = None) -> None:
        self.date = date
        self.time = time
        time_str = f" at {time}" if time else ""
        super().__init__(f"No slots available for {date}{time_str}")


class InvalidSlotPreferenceError(BookingError):
    """User requested a slot number that doesn't exist."""

    def __init__(self, requested: int, available: int) -> None:
        self.requested = requested
        self.available = available
        super().__init__(
            f"Requested slot {requested}, but only {available} slots available"
        )

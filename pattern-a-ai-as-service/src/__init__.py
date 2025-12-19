"""
Pattern A: AI as Service

LLM parses text only, you control the business logic.
"""

from .booking import process_booking
from .exceptions import (
    BookingError,
    InvalidSlotPreferenceError,
    NoSlotsAvailableError,
    ParseError,
    PatternAError,
    SlotNotAvailableError,
    SlotNotFoundError,
)
from .models import ChatRequest, ChatResponse, HealthResponse, ParsedIntent
from .parser import parse_intent
from .settings import Settings, get_settings

__all__ = [
    # Models
    "ParsedIntent",
    "ChatRequest",
    "ChatResponse",
    "HealthResponse",
    # Functions
    "parse_intent",
    "process_booking",
    # Exceptions
    "PatternAError",
    "ParseError",
    "BookingError",
    "SlotNotFoundError",
    "SlotNotAvailableError",
    "NoSlotsAvailableError",
    "InvalidSlotPreferenceError",
    # Settings
    "Settings",
    "get_settings",
]

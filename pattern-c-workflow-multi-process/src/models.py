"""
Pydantic models defining service contracts.
These models define the input/output interfaces between independent services.
"""

import re
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class ServiceResponse(BaseModel, Generic[T]):
    """
    Standard response wrapper for all services.
    Enables consistent error handling across the workflow.
    """

    success: bool = Field(description="Whether the service call succeeded")
    data: T | None = Field(default=None, description="Service output data")
    error: str | None = Field(default=None, description="Error message if failed")


# ============ Service 1: Intent Parser ============


class ParsedIntent(BaseModel):
    """Output from the Intent Parser service."""

    date: str | None = Field(
        default=None,
        description="Extracted date in YYYY-MM-DD format",
    )
    time: str | None = Field(
        default=None,
        description="Extracted time in HH:MM format",
    )
    raw_message: str = Field(description="Original user message")

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")
        return v

    @field_validator("time")
    @classmethod
    def validate_time_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError(f"Time must be in HH:MM format, got: {v}")
        return v


# ============ Service 2: Availability Checker ============


class SlotInfo(BaseModel):
    """Available slot information."""

    slot_id: str
    court: str
    date: str
    time: str
    duration_minutes: int = 60


class AvailabilityResult(BaseModel):
    """Output from the Availability service."""

    slots: list[SlotInfo] = Field(default_factory=list)
    message: str = Field(description="Human-readable availability summary")


# ============ Service 3: Booking Handler ============


class BookingResult(BaseModel):
    """Output from the Booking service."""

    booking_id: str | None = Field(default=None, description="Booking ID if successful")
    court: str | None = None
    date: str | None = None
    time: str | None = None
    message: str = Field(description="Human-readable confirmation or error message")


# ============ API Models ============


class ChatRequest(BaseModel):
    """API request model."""

    message: str = Field(
        ...,
        min_length=1,
        description="User message for booking request",
        examples=["Book a tennis court for tomorrow at 3pm"],
    )


class ChatResponse(BaseModel):
    """API response model."""

    response: str = Field(description="System's response to the user")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(description="Service status")
    pattern: str = Field(description="Pattern identifier")
    name: str = Field(description="Pattern name")

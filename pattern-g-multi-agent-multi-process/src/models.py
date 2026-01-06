"""
Pydantic models for Pattern G: Multi-Agent Multi-Process.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint (Manager service)."""

    message: str = Field(
        ...,
        description="User message to the booking system",
        examples=["Book a tennis court for tomorrow at 3pm"],
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(
        ...,
        description="System response to the user",
    )


class AvailabilityRequest(BaseModel):
    """Request model for availability specialist."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: Optional[str] = Field(None, description="Optional time in HH:MM format")


class AvailabilityResponse(BaseModel):
    """Response model for availability specialist."""

    result: str = Field(..., description="Available slots or message")


class BookingRequest(BaseModel):
    """Request model for booking specialist."""

    slot_id: str = Field(..., description="Slot ID to book")


class BookingResponse(BaseModel):
    """Response model for booking specialist."""

    result: str = Field(..., description="Booking confirmation or error")

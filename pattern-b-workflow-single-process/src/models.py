"""
Pydantic models for Pattern B workflow.

Simple data classes - no ServiceResponse wrapper needed
since all steps run in shared memory.
"""

from pydantic import BaseModel, Field


# ============ Step 1: Intent Parser Output ============

class ParsedIntent(BaseModel):
    """Output from the intent parsing step."""
    date: str | None = Field(default=None, description="Extracted date in YYYY-MM-DD format")
    time: str | None = Field(default=None, description="Extracted time in HH:MM format")
    raw_message: str = Field(description="Original user message")


# ============ Step 2: Availability Check Output ============

class SlotInfo(BaseModel):
    """Available slot information."""
    slot_id: str
    court: str
    date: str
    time: str


# ============ Step 3: Booking Output ============

class BookingResult(BaseModel):
    """Output from the booking step."""
    booking_id: str
    court: str
    date: str
    time: str
    message: str = Field(description="Human-readable confirmation")


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

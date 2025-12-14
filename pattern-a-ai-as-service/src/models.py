"""
Pydantic models for Pattern A: AI as Service.

Simple data class for the parsed intent - the only output from the AI component.
"""

from pydantic import BaseModel, Field


class ParsedIntent(BaseModel):
    """
    Output from the LLM parser.

    This is the ONLY place where AI is involved in Pattern A.
    The LLM converts natural language into this structured format.
    """
    date: str | None = Field(default=None, description="Extracted date in YYYY-MM-DD format")
    time: str | None = Field(default=None, description="Extracted time in HH:MM format")
    slot_preference: int | None = Field(default=None, description="User's preferred slot (1=first, 2=second, etc.)")
    raw_message: str = Field(description="Original user message")


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

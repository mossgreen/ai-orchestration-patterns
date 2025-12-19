"""Pydantic models for Pattern A: AI as Service."""

import re

from pydantic import BaseModel, Field, field_validator


class ParsedIntent(BaseModel):
    """
    Output from the LLM parser.

    The LLM converts natural language into this structured format.
    """

    date: str | None = Field(
        default=None,
        description="Extracted date in YYYY-MM-DD format",
    )
    time: str | None = Field(
        default=None,
        description="Extracted time in HH:MM format",
    )
    slot_preference: int | None = Field(
        default=None,
        description="User's preferred slot (1=first, 2=second, etc.)",
        ge=1,
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

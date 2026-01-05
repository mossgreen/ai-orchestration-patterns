"""Pydantic models for Pattern D: Function Calling."""

from pydantic import BaseModel, Field


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

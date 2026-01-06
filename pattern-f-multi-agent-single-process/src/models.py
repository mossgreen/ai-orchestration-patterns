"""
Pydantic models for Pattern F: Multi-Agent (Shared Runtime).
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        description="User message to the booking system",
        examples=["What courts are available tomorrow?"],
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(
        ...,
        description="Response from the multi-agent system",
    )

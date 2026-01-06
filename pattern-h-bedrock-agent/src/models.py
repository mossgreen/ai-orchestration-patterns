"""
Pydantic models for Pattern H: Bedrock Agent.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        description="User message to the booking agent",
        examples=["Book a tennis court for tomorrow at 3pm"],
    )
    session_id: str = Field(
        default="default-session",
        description="Session ID for conversation continuity",
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(
        ...,
        description="Agent's response to the user",
    )
    session_id: str = Field(
        ...,
        description="Session ID used for this conversation",
    )

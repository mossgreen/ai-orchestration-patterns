"""Pydantic models for Pattern B."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str


class ChatResponse(BaseModel):
    """Outgoing chat response."""

    response: str


class ParsedIntent(BaseModel):
    """Parsed booking intent from user message."""

    date: str | None = None
    time: str | None = None

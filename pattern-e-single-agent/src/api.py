"""
FastAPI wrapper for the Tennis Court Booking Agent.

Run with: uvicorn pattern-e.src.api:app --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agent import run_agent


app = FastAPI(
    title="Tennis Court Booking Agent",
    description="Pattern E: Single Agent - The agent autonomously manages the booking workflow",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        description="User message to the booking agent",
        examples=["Book a tennis court for tomorrow at 3pm"],
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(
        ...,
        description="Agent's response to the user",
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the booking agent.

    The agent autonomously decides how to handle your request:
    - Checking availability
    - Booking slots
    - Asking for clarification

    This is Pattern E: the agent controls its own reasoning loop.
    """
    try:
        response = await run_agent(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "E - Single Agent"}

"""
FastAPI wrapper for the Tennis Court Booking Agent.

Run with: uvicorn pattern-e.src.api:app --reload
"""

from fastapi import FastAPI, HTTPException

from .agent import run_agent
from .models import ChatRequest, ChatResponse


app = FastAPI(
    title="Pattern E: Single Agent",
    description="The agent autonomously manages the booking workflow",
    version="1.0.0",
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
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "E"}

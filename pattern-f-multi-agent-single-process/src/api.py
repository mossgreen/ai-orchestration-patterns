"""
FastAPI wrapper for the Multi-Agent Tennis Court Booking system.

Run with: uvicorn pattern-f-multi-agent-single-process.src.api:app --reload
"""

from fastapi import FastAPI, HTTPException

from .agent import run_manager
from .models import ChatRequest, ChatResponse


app = FastAPI(
    title="Pattern F: Multi-Agent (Single Process)",
    description="Manager routes requests to specialized agents in shared runtime",
    version="1.0.0",
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the multi-agent booking system.

    The manager agent routes your request to the appropriate specialist:
    - Availability Specialist: for checking available slots
    - Booking Specialist: for booking a specific slot

    This is Pattern F: multiple agents in a shared runtime.
    """
    try:
        response = await run_manager(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "F"}

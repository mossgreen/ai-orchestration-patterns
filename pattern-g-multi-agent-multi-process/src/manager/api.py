"""
FastAPI for Manager Service - Pattern G

User-facing service that routes to specialist services via HTTP.
"""

from fastapi import FastAPI, HTTPException

from ..models import ChatRequest, ChatResponse
from .agent import run_manager


app = FastAPI(
    title="Pattern G: Multi-Agent (Multi-Process)",
    description="Manager routes requests to specialist services via HTTP",
    version="1.0.0",
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the multi-agent booking system.

    The manager agent routes your request to specialist services:
    - Availability Specialist (separate Lambda): for checking available slots
    - Booking Specialist (separate Lambda): for booking a specific slot

    This is Pattern G: multiple agents in separate processes, communicating via HTTP.
    """
    try:
        response = await run_manager(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "manager", "pattern": "G"}

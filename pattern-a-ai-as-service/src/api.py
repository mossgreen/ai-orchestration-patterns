"""
FastAPI wrapper for Pattern A: AI as Service.

Run with: uvicorn pattern-a-ai-as-service.src.api:app --reload
"""

from fastapi import FastAPI, HTTPException

from .models import ChatRequest, ChatResponse
from .parser import parse_intent
from .booking import process_booking


app = FastAPI(
    title="Tennis Court Booking - AI as Service (no agent)",
    description="Pattern A: LLM parses text only, YOU control the business logic",
    version="1.0.0",
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a booking request.

    Pattern A flow:
    1. LLM parses user message into structured data (ONLY AI here)
    2. YOUR code processes the booking (no AI)

    The AI understands your intent, but won't make any decision for you.
    """
    try:
        # Step 1: Parse with AI (the ONLY AI component)
        intent = await parse_intent(request.message)

        # Step 2: Process with YOUR code (no AI)
        response = process_booking(intent)

        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "A - AI as Service"}

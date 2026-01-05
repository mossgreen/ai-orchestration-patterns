"""FastAPI application for Pattern B: Workflow (Single Process)."""

import logging

from fastapi import FastAPI, HTTPException

from shared import BookingService

from .intent_parser import IntentParser
from .models import ChatRequest, ChatResponse
from .settings import get_settings
from .workflow import Workflow

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pattern B: Workflow (Single Process)",
    description="Fixed-sequence workflow orchestration",
    version="1.0.0",
)

# Wire dependencies at startup
_settings = get_settings()
_booking_service = BookingService()
_intent_parser = IntentParser(_settings)
_workflow = Workflow(_intent_parser, _booking_service)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a booking request through the fixed workflow."""
    logger.info("Chat request received: %s", request.message[:50])

    try:
        result = await _workflow.run(request.message)
        logger.info("Chat request successful")
        return ChatResponse(response=result)
    except Exception as e:
        logger.error("Chat request failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "B"}

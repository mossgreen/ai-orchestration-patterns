"""
FastAPI application for Pattern A: AI as Service.

Run with: uvicorn src.api:app --reload
"""

import logging
from typing import Awaitable, Callable

from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError

from shared import BookingError, BookingService

from .booking import process_booking
from .services import booking_service
from .exceptions import BookingError as PatternABookingError
from .exceptions import ParseError
from .models import ChatRequest, ChatResponse, HealthResponse, ParsedIntent
from .parser import parse_intent
from .settings import get_settings

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Pattern A: AI as Service",
    description="LLM parses text only, YOU control the business logic",
    version="1.0.0",
)


# ============================================================
# Dependency Providers
# ============================================================


def get_parser() -> Callable[[str], Awaitable[ParsedIntent]]:
    """
    Provide parser function for dependency injection.

    Returns the parse_intent function that can be overridden in tests.
    """
    return parse_intent


def get_booking_service() -> BookingService:
    """
    Provide BookingService singleton for dependency injection.

    Returns the singleton instance created at module load.
    """
    return booking_service


def get_booking_processor(
    service: BookingService = Depends(get_booking_service),
) -> Callable[[ParsedIntent], str]:
    """
    Provide booking processor function for dependency injection.

    Returns the process_booking function bound to the singleton BookingService.
    """
    return lambda intent: process_booking(intent, booking_service=service)


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    parser: Callable[[str], Awaitable[ParsedIntent]] = Depends(get_parser),
    booking_processor: Callable[[ParsedIntent], str] = Depends(get_booking_processor),
) -> ChatResponse:
    """
    Process a booking request.

    Pattern A flow:
    1. LLM parses user message into structured data (ONLY AI here)
    2. YOUR code processes the booking (no AI)

    The AI understands your intent, but won't make any decision for you.
    """
    logger.info("Received chat request: %s", request.message[:50])

    try:
        # Step 1: Parse with AI (the ONLY AI component)
        intent = await parser(request.message)

        # Step 2: Process with YOUR code (no AI)
        response = booking_processor(intent)

        return ChatResponse(response=response)

    except ParseError as e:
        logger.warning("Parse error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    except (PatternABookingError, BookingError) as e:
        logger.warning("Booking error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    except ValidationError as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=400, detail="Invalid data format")

    except Exception as e:
        # Log the full error for debugging, but don't expose details to client
        logger.exception("Unexpected error processing request")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred. Please try again later.",
        )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", pattern="A: AI as Service")

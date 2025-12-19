"""FastAPI application for Pattern A: AI as Service."""

from fastapi import FastAPI, HTTPException

from shared import BookingError, BookingService

from .booking import process_booking
from .exceptions import BookingError as PatternABookingError
from .exceptions import ParseError
from .models import ChatRequest, ChatResponse
from .parser import parse_intent

app = FastAPI(
    title="Pattern A: AI as Service",
    description="LLM parses text only, YOU control the business logic",
    version="1.0.0",
)

# Wire dependencies at startup
_booking_service = BookingService()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a booking request.

    Pattern A flow:
    1. LLM parses user message into structured data (ONLY AI here)
    2. YOUR code processes the booking (no AI)
    """
    try:
        # Step 1: Parse with AI (the ONLY AI component)
        intent = await parse_intent(request.message)

        # Step 2: Process with YOUR code (no AI)
        result = process_booking(intent, booking_service=_booking_service)

        return ChatResponse(response=result)

    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except (PatternABookingError, BookingError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "A"}

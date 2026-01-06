"""
FastAPI for Booking Specialist - Pattern G

Runs as a separate service, handles booking requests via HTTP.
"""

from fastapi import FastAPI, HTTPException

from ..models import BookingRequest, BookingResponse
from .agent import process_booking_request


app = FastAPI(
    title="Pattern G: Booking Specialist",
    description="Booking service (separate process)",
    version="1.0.0",
)


@app.post("/process", response_model=BookingResponse)
async def process(request: BookingRequest) -> BookingResponse:
    """
    Book a specific slot.

    Called by the Manager service via HTTP.
    """
    try:
        result = process_booking_request(request.slot_id)
        return BookingResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "booking-specialist", "pattern": "G"}

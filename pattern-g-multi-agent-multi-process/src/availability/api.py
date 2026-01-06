"""
FastAPI for Availability Specialist - Pattern G

Runs as a separate service, handles availability queries via HTTP.
"""

from fastapi import FastAPI, HTTPException

from ..models import AvailabilityRequest, AvailabilityResponse
from .agent import process_availability_request


app = FastAPI(
    title="Pattern G: Availability Specialist",
    description="Availability checking service (separate process)",
    version="1.0.0",
)


@app.post("/process", response_model=AvailabilityResponse)
async def process(request: AvailabilityRequest) -> AvailabilityResponse:
    """
    Check availability for a given date/time.

    Called by the Manager service via HTTP.
    """
    try:
        result = process_availability_request(request.date, request.time)
        return AvailabilityResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "availability-specialist", "pattern": "G"}

"""FastAPI application for Pattern D: Function Calling."""

from fastapi import FastAPI, HTTPException

from shared import BookingError, BookingService

from .function_caller import call
from .models import ChatRequest, ChatResponse

app = FastAPI(
    title="Pattern D: Function Calling",
    description="LLM decides which functions to call in a loop",
    version="1.0.0",
)

_booking_service = BookingService()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a booking request using function calling.

    Pattern D flow:
    1. Send user message to LLM with tool definitions
    2. LLM decides which tools to call
    3. Execute tools and return results to LLM
    4. Repeat until LLM returns final response
    """
    try:
        result = await call(request.message, _booking_service)
        return ChatResponse(response=result)

    except BookingError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "D"}

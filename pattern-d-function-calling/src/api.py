"""
FastAPI wrapper for Pattern D: Function Calling.

Run with:
    cd pattern-d-function-calling
    uv venv && source .venv/bin/activate
    uv pip install -r requirements.txt
    uvicorn src.api:app --reload --port 8001

Uses true async I/O - the event loop handles multiple requests concurrently
while waiting for OpenAI API responses.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .function_caller import run_conversation


app = FastAPI(
    title="Tennis Court Booking - Function Calling",
    description="Pattern D: You control the loop - LLM suggests functions, your code executes them",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        description="User message to the booking system",
        examples=["Book a tennis court for tomorrow at 3pm"],
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(
        ...,
        description="System's response to the user",
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the booking system.

    Pattern D: Function Calling
    - Your code receives the request
    - Calls OpenAI with available tools
    - OpenAI suggests function calls
    - YOUR CODE executes the functions
    - YOUR CODE sends results back
    - Loops until complete

    Uses true async - event loop is free while waiting for OpenAI.
    """
    try:
        response = await run_conversation(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred processing your request")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "D - Function Calling"}

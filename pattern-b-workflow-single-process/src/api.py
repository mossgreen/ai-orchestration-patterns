"""
FastAPI wrapper for Pattern B: Workflow (Shared Runtime).

Run with: uvicorn pattern-b-workflow-single-process.src.api:app --reload
"""

from fastapi import FastAPI, HTTPException

from .models import ChatRequest, ChatResponse
from .orchestrator import run_workflow


app = FastAPI(
    title="Tennis Court Booking - Workflow (Shared)",
    description="Pattern B: Fixed-sequence workflow in shared runtime",
    version="1.0.0",
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a booking request through the fixed workflow.

    The workflow always executes in this order:
    1. Parse intent (extract date/time from message)
    2. Check availability (find matching slots)
    3. Book first available slot

    This is Pattern B: deterministic, fixed-sequence workflow.
    """
    try:
        response = await run_workflow(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "B - Workflow (Shared Runtime)"}

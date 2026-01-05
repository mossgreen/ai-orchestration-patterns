"""FastAPI application for Pattern C: Workflow (Multi Process)."""

from fastapi import FastAPI, HTTPException

from .exceptions import ServiceError, WorkflowError
from .models import ChatRequest, ChatResponse
from .workflow import run_workflow

app = FastAPI(
    title="Pattern C: Workflow (Multi Process)",
    description="Fixed workflow with independent, deployable services",
    version="1.0.0",
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a booking request through the fixed workflow."""
    try:
        result = await run_workflow(request.message)
        return ChatResponse(response=result)

    except (ServiceError, WorkflowError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "C"}

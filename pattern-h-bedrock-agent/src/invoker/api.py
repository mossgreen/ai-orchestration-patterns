"""
FastAPI wrapper for Bedrock Agent Invoker - Pattern H

User-facing API that invokes the Bedrock Agent.
"""

from fastapi import FastAPI, HTTPException

from ..models import ChatRequest, ChatResponse
from .agent import invoke_bedrock_agent


app = FastAPI(
    title="Pattern H: Bedrock Agent",
    description="AWS-managed agent with action groups for tennis court booking",
    version="1.0.0",
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the Bedrock Agent.

    The agent autonomously decides how to handle your request using
    the defined action groups (check_availability, book_slot).

    This is Pattern H: AWS Bedrock manages the conversation loop.
    """
    try:
        response = invoke_bedrock_agent(request.message, request.session_id)
        return ChatResponse(response=response, session_id=request.session_id)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {e}")


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "pattern": "H", "agent": "bedrock"}

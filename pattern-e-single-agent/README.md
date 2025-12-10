# Pattern E: Single Agent

**Control Level:** Agent controls the loop
**Autonomy:** High - agent decides when to use tools and how to sequence actions

## Overview

In Pattern E, the agent autonomously manages its own reasoning loop. Unlike Pattern D (where you control the loop and execute functions), here the agent:

1. Receives user input
2. Decides which tool to call (if any)
3. Executes the tool
4. Processes results
5. Decides next action
6. Returns final response

This is the foundation for agentic AI systems.

## Architecture

```
User Request
     │
     ▼
┌─────────────────────────────────────┐
│         OpenAI Agent                │
│  ┌─────────────────────────────┐   │
│  │     Agent Loop (LLM)        │   │
│  │  - Reasoning                │   │
│  │  - Tool Selection           │   │
│  │  - Response Generation      │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │         Tools               │   │
│  │  - check_availability()     │   │
│  │  - book_slot()              │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│       Booking Service (Mock)        │
└─────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd pattern-e-single-agent
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Set OpenAI API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-api-key
```

Or export directly:

```bash
export OPENAI_API_KEY="your-api-key"
```

### 3. Run Demo

```bash
uv run src/demo.py
```

### 4. Run API Server

```bash
uv run uvicorn src.api:app --reload
```

### 5. Test with curl

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book a tennis court for tomorrow at 3pm"}'
```

## Key Differentiator

| Pattern D (Function Calling) | Pattern E (Single Agent) |
|------------------------------|--------------------------|
| You write the loop | Agent manages the loop |
| You decide when to call LLM | Agent decides autonomously |
| More control | More autonomous |
| Deterministic flow | Dynamic flow |

## Files

- `src/agent.py` - Agent definition with tools
- `src/api.py` - FastAPI wrapper
- `requirements.txt` - Dependencies

## Example Conversation

```
User: "Book a tennis court for tomorrow around 3pm"

Agent: [internally calls check_availability("2024-12-10", "15:00")]
       [sees available slots]
       [calls book_slot("2024-12-10_CourtA_1500", "guest")]

Agent Response:
  "I've booked Court A for you tomorrow at 3:00 PM.
   Booking ID: BK0001
   See you on the court!"
```

The agent autonomously decided to:
1. Check availability first
2. Select an appropriate slot
3. Complete the booking
4. Confirm with the user

No manual orchestration required.

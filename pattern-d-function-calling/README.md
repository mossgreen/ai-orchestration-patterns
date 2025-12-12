# Pattern D: Function Calling

**Control Level:** You control the loop
**Autonomy:** Medium - LLM suggests functions, your code executes them

## Overview

Pattern D demonstrates explicit function calling where **you control the conversation loop**. Unlike Pattern E (where the agent SDK handles everything), here you:

1. Call OpenAI API with tools defined
2. Check if OpenAI returns tool_calls
3. **Decide** whether to execute (your code controls this!)
4. Execute functions yourself
5. Send results back to OpenAI
6. Loop until no more tool_calls

This is what happens "under the hood" of agent SDKs like Pattern E.

## Architecture

```
User Request
     │
     ▼
┌──────────────────────────────────────────────────┐
│         YOUR CONTROL LOOP (function_caller.py)   │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  1. await client.chat.completions.create() │  │
│  │                  │                         │  │
│  │                  ▼                         │  │
│  │  2. Response has tool_calls?               │  │
│  │        │                    │              │  │
│  │       YES                   NO             │  │
│  │        │                    │              │  │
│  │        ▼                    ▼              │  │
│  │  3. Execute functions   Return response    │  │
│  │        │                                   │  │
│  │        ▼                                   │  │
│  │  4. Send results back                      │  │
│  │        │                                   │  │
│  │        └──────▶ (loop to step 1)           │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────┐
│     Booking Service (shared/booking_service.py)  │
└──────────────────────────────────────────────────┘
```

## Key Difference from Pattern E

| Aspect | Pattern D (Function Calling) | Pattern E (Single Agent) |
|--------|------------------------------|--------------------------|
| Loop control | **You** write the loop | Agent SDK handles it |
| Function execution | **You** call functions | SDK calls functions |
| Visibility | See every step | Black box |
| Customization | Full control | Limited hooks |
| Code complexity | More code | Less code |
| Use case | Need control/validation | Just want results |

## True Async I/O

This implementation uses **true async** with `AsyncOpenAI`:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def run_conversation(user_message: str) -> str:
    # await yields control to event loop while waiting for OpenAI
    response = await client.chat.completions.create(...)
```

**Why this matters:**
- Event loop is free while waiting for OpenAI API (2-5 seconds)
- FastAPI can handle other requests concurrently
- Proper non-blocking I/O for production use

## Quick Start

### 1. Install Dependencies

```bash
cd pattern-d-function-calling
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Set OpenAI API Key

The `.env` file in project root should have:

```
OPENAI_API_KEY=your-api-key
```

### 3. Run Demo

```bash
python src/demo.py
```

Watch the console output to see the control loop in action!

### 4. Run API Server

```bash
uvicorn src.api:app --reload --port 8001
```

### 5. Test with curl

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book a tennis court for tomorrow at 3pm"}'
```

## Example Session

```
You: Book a court for tomorrow at 2pm

[Calling OpenAI API...]
[LLM wants to call 1 function(s)]
  [Executing] check_availability({'date': '2024-12-13', 'time': '14:00'})

[Calling OpenAI API...]
[Final response received]
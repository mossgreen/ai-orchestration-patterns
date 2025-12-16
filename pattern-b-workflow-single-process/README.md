# Pattern B: Workflow (Shared Runtime)

A fixed-sequence workflow where steps always execute in the same order within a single process.

## Architecture

```
User Request
     |
     v
+------------------------------------------+
|         Workflow Orchestrator             |
|  (Fixed sequence, shared runtime)         |
+------------------------------------------+
     |
     | Step 1
     v
+------------------+
|   IntentParser   |  Uses OpenAI to extract date/time
+------------------+
     |
     | Step 2
     v
+------------------+
| AvailabilityStep |  Queries BookingService
+------------------+
     |
     | Step 3
     v
+------------------+
|   BookingStep    |  Creates reservation
+------------------+
     |
     v
  Response
```

## Key Difference from Other Patterns

| Pattern | Sequence | Runtime | Who Decides |
|---------|----------|---------|-------------|
| **B (This)** | Fixed | Shared | YOU define steps |
| C | Fixed | Independent | YOU define steps |
| D | Dynamic | Shared | LLM suggests |
| E | Dynamic | Shared | Agent controls |

## Performance

| Metric | Value |
|--------|-------|
| **LLM Calls** | 1 (Step 1: Intent Parser only) |
| **Expected Latency** | ~200-500ms |
| **Latency Breakdown** | LLM: ~200-500ms, Steps 2-3: <10ms |

Only Step 1 calls the LLM. Steps 2 and 3 are pure local operations with no AI overhead.

## When to Use Pattern B

- Workflow steps are well-defined and won't change
- Need fast execution (no network latency)
- Want simple orchestration
- Single deployment unit is acceptable
- Failure of one step can take down the system (acceptable trade-off)

## Quick Start

```bash
cd pattern-b-workflow-single-process
uv run src/demo.py
```

## API

```bash
uvicorn src.api:app --reload
```

Then:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book a tennis court for tomorrow at 3pm"}'
```

## Files

```
src/
├── models.py           # Pydantic models
├── steps.py            # All 3 workflow steps
├── orchestrator.py     # Fixed-sequence coordinator
├── api.py              # FastAPI wrapper
└── demo.py             # CLI demo
```

## How It Works

1. User sends booking request
2. **Step 1:** Intent Parser extracts date/time using OpenAI
3. **Step 2:** Availability Checker finds matching slots
4. **Step 3:** Booking Handler reserves first available slot
5. Response returned to user

The sequence is always the same - no dynamic routing, no branching.

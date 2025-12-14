# Pattern A: AI as Service (no agent)

The simplest and most controlled approach. LLM is used **only for parsing** - all business logic is YOUR code.

## Architecture

```
User Message: "Book Saturday afternoon, first slot please"
         |
         v
+------------------+
|   LLM Parser     |  <-- AI is ONLY used here
+------------------+
         |
         v
ParsedIntent {date: "2024-12-14", time: "14:00", slot_preference: 1}
         |
         v
+------------------------------------------+
|        YOUR APPLICATION CODE              |
|  (No AI - you control everything)         |
|  - Check availability                     |
|  - Book slot                              |
|  - Return confirmation                    |
+------------------------------------------+
         |
         v
    Response
```

## Key Insight

The LLM is just a **text utility** for discriminative tasks:
- Parsing text into structured data (date, time, slot preference)
- No decision-making
- No business logic
- Full auditability

## Key Difference from Pattern B

| Aspect | Pattern A (This) | Pattern B (Workflow) |
|--------|------------------|----------------------|
| **Structure** | Inline business logic | Separate step classes |
| **Abstraction** | None - raw code | WorkflowOrchestrator |
| **LLM Role** | Parse only | Parse in Step 1 |
| **Message** | "LLM is just a utility" | "Steps are modular" |

## When to Use Pattern A

- Compliance-heavy environments (banking, healthcare)
- When you need full audit trails
- Single-turn interactions
- When AI should be a "utility" not a "decision-maker"

## Quick Start

```bash
cd pattern-a-ai-as-service
source ../.venv/bin/activate
python -m src.demo
```

Or with a custom message:
```bash
python -m src.demo "Book tomorrow at 3pm, second slot"
```

## API

```bash
uvicorn src.api:app --reload
```

Then:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book Saturday afternoon, first slot please"}'
```

## Files

```
src/
├── models.py       # ParsedIntent model (date, time, slot_preference)
├── parser.py       # LLM parser (ONLY AI component)
├── booking.py      # YOUR business logic (no AI)
├── api.py          # FastAPI wrapper
└── demo.py         # CLI demo (auto-runs with default message)
```

## How It Works

1. User sends booking request (e.g., "Book Saturday afternoon, first slot")
2. **LLM Parser** extracts date, time, and slot preference (ONLY AI here)
3. **YOUR CODE** checks availability (no AI)
4. **YOUR CODE** selects slot based on user preference (no AI)
5. **YOUR CODE** books and returns confirmation (no AI)

The AI is minimal and transparent - just parsing text. One LLM call extracts everything needed to complete the booking.

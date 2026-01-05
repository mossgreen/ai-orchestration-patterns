# Pattern C: Workflow with Independent Runtime

A fixed workflow pattern where each step runs as an independent service that could be deployed separately (e.g., AWS Lambda).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                              │
│           (Coordinates fixed workflow sequence)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Service 1:    │  │   Service 2:    │  │   Service 3:    │
│  Intent Parser  │─▶│  Availability   │─▶│    Booking      │
│    (OpenAI)     │  │    Checker      │  │    Handler      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
      │                      │                    │
      ▼                      ▼                    ▼
  ParsedIntent         AvailabilityResult    BookingResult
  - date               - slots[]             - booking_id
  - time               - message             - confirmation
```

## Key Characteristics

| Aspect | Pattern C |
|--------|-----------|
| **Workflow** | Fixed sequence (you define the steps) |
| **Runtime** | Independent services |
| **Communication** | Request/Response between services |
| **Failure Isolation** | Yes - each service fails independently |
| **Deployment** | Can deploy each service separately |
| **AI Vendor** | Can use different vendors per service |

## vs Other Patterns

- **Pattern B (Workflow - Shared)**: Same fixed sequence, but all in one process
- **Pattern C (This)**: Fixed sequence with independent services
- **Pattern D (Function Calling)**: LLM decides which functions to call dynamically

## Services

### 1. Intent Parser Service
- **Input**: Natural language message
- **Output**: Structured intent (date, time)
- **AI**: OpenAI GPT-4o-mini
- **Example**: "Book tomorrow at 3pm" → `{date: "2024-01-16", time: "15:00"}`

### 2. Availability Service
- **Input**: Parsed intent
- **Output**: List of available slots
- **AI**: None (direct database query)
- **Uses**: Shared BookingService

### 3. Booking Handler Service
- **Input**: Selected slot + user ID
- **Output**: Booking confirmation
- **AI**: None (direct database operation)
- **Uses**: Shared BookingService

## Usage

### Interactive Demo

```bash
# From project root
cd pattern-c-workflow-multi-process
uv run python src/demo.py
```

### FastAPI Server

```bash
# From pattern-c-workflow-multi-process directory
cd pattern-c-workflow-multi-process
source ../.venv/bin/activate
uvicorn src.api:app --reload

# Test endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book a tennis court for tomorrow at 3pm"}'
```

## File Structure

```
pattern-c-workflow-multi-process/
├── README.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── models.py           # Service contracts (Pydantic)
    ├── orchestrator.py     # Workflow coordinator
    ├── api.py              # FastAPI server
    ├── demo.py             # Interactive CLI
    └── services/
        ├── __init__.py
        ├── base.py             # Base service interface
        ├── intent_parser.py    # Service 1
        ├── availability.py     # Service 2
        └── booking.py          # Service 3
```

## Lambda-Ready Design

Each service follows a pattern that enables easy extraction to AWS Lambda:

```python
# Current: In-process service
class IntentParserService(BaseService):
    async def execute(self, request: dict) -> ServiceResponse:
        ...

# Future: Lambda handler (minimal changes)
def lambda_handler(event, context):
    service = IntentParserService()
    result = asyncio.run(service.execute(event))
    return result.model_dump()
```

## Environment Variables

```bash
OPENAI_API_KEY=your-api-key-here
```

# Pattern F: Multi-Agent (Shared Runtime)

A manager agent dynamically routes user requests to specialized agents, all running in a single process.

## Architecture

```
User Request
     |
     v
+------------------------------------------+
|           Manager Agent                   |
|  (Analyzes intent, decides routing)       |
+--------------------+---------------------+
                     |
         +-----------+-----------+
         |                       |
         v                       v
+----------------+      +----------------+
|  Availability  |      |    Booking     |
|   Specialist   |      |   Specialist   |
+----------------+      +----------------+
         |                       |
         v                       v
check_availability()       book_slot()
```

## Key Difference from Pattern E

| Pattern E (Single Agent) | Pattern F (Multi-Agent) |
|--------------------------|-------------------------|
| One agent with multiple tools | Multiple focused agents |
| Agent decides which tool | Manager decides which agent |
| Simpler setup | Better separation of concerns |

## When to Use Pattern F

- User requests vary significantly
- Need dynamic decision-making about routing
- Want simple deployment (single process)
- Specialists benefit from focused instructions

## Quick Start

```bash
cd pattern-f-multi-agent-single-process
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
  -d '{"message": "What courts are available tomorrow?"}'
```

## Files

```
src/
├── agents.py   # Manager + Specialist agents with handoffs
├── api.py      # FastAPI wrapper
└── demo.py     # CLI demo
```

## How It Works

1. User sends a request
2. Manager Agent analyzes intent
3. Manager hands off to appropriate specialist:
   - Availability questions → Availability Specialist
   - Booking requests → Booking Specialist
4. Specialist handles the task using its tools
5. Response flows back to user

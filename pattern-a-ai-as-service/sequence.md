# Pattern A: AI as Service - Sequence Diagram

## Main Entities

| Entity | File | Responsibility | AI Involved? |
|--------|------|----------------|--------------|
| **API** | `api.py` | HTTP endpoint, orchestration, error handling | No |
| **Services** | `services.py` | Singleton BookingService (created at startup) | No |
| **Parser** | `parser.py` | Convert natural language → structured data | **YES (ONLY HERE)** |
| **OpenAI** | external | LLM service | External |
| **BookingProcessor** | `booking.py` | Business logic, slot selection | No |
| **BookingService** | `shared/` | Data layer (availability, booking) | No |

## Data Models (Contracts)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `ChatRequest` | API input | `message: str` |
| `ParsedIntent` | Parser → Processor | `date`, `time`, `slot_preference`, `raw_message` |
| `Slot` | Service → Processor | `slot_id`, `court`, `date`, `time` |
| `Booking` | Service → Processor | `booking_id`, `court`, `date`, `time` |
| `ChatResponse` | API output | `response: str` |

## Sequence Diagram (PlantUML)

```plantuml
@startuml
participant "User" as U
participant "API" as A
participant "Parser" as P
participant "OpenAI" as O
participant "BookingProcessor" as B
participant "BookingService" as S

== App Startup ==
note over A,S: BookingService singleton created (services.py)

== Request Flow ==
U -> A: POST /chat {message}

note over A: Step 1: Parse (AI)
A -> P: parse_intent(message)
P -> O: chat.completions.create()
O --> P: JSON {date, time, slot_preference}
P --> A: ParsedIntent

note over A: Step 2: Process (NO AI)
A -> B: process_booking(intent)
B -> S: check_availability(date, time)
S --> B: list[Slot]

alt No slots available
    B --> A: raise NoSlotsAvailableError
    A --> U: 400 Error
else Slots available
    note over B: _select_slot(slots, preference)
    B -> S: book(slot_id)
    S --> B: Booking
    note over B: _format_confirmation(booking)
    B --> A: confirmation string
    A --> U: ChatResponse
end
@enduml
```

## Simplified Flow (ASCII)

```
User                API                 Parser              OpenAI
  |                  |                    |                    |
  |--POST /chat----->|                    |                    |
  |                  |--parse_intent()--->|                    |
  |                  |                    |--completions()---->|
  |                  |                    |<---JSON response---|
  |                  |<--ParsedIntent-----|                    |
  |                  |
  |                  |                BookingProcessor                BookingService
  |                  |                      |                               |
  |                  |--process_booking()-->|                               |
  |                  |                      |--check_availability()-------->|
  |                  |                      |<------list[Slot]--------------|
  |                  |                      |--book(slot_id)--------------->|
  |                  |                      |<------Booking-----------------|
  |                  |<--confirmation------|
  |<--ChatResponse---|
```

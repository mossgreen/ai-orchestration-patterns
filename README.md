# AI Orchestration Patterns

Production-ready implementations of 8 AI orchestration patterns — from deterministic workflows to autonomous multi-agent systems.

Each pattern uses the same use case (tennis court booking) to highlight architectural differences, not domain complexity.

## 📖 Reference

This repo implements the patterns described in my blog post:

**[AI Orchestration Deep Dive: From No-Agent to Multi-Agent and Beyond](https://mossgreen.github.io/Booking-system-ai-orchestration/)**

Read the blog first for architecture diagrams, trade-offs, and decision guides.

## Patterns

| Pattern | Style | Runtime | Status |
|---------|-------|---------|--------|
| [A - AI as Service](./pattern-a-ai-as-service/) | No agent, LLM parses only | Shared | ✅ Done |
| [B - Workflow (Single-Process)](./pattern-b-workflow-single-process/) | Fixed sequence | Single-Process | ✅ Done |
| [C - Workflow (Multi-Process)](./pattern-c-workflow-multi-process/) | Fixed sequence | Multi-Process | ✅ Done |
| [D - Function Calling](./pattern-d-function-calling/) | LLM suggests, you control loop | Shared | ✅ Done |
| [E - Single Agent](./pattern-e-single-agent/) | Agent controls the loop | Shared | ✅ Done |
| [F - Multi-Agent (Single-Process)](./pattern-f-multi-agent-single-process/) | Manager routes dynamically | Single-Process | ✅ Done |
| [G - Multi-Agent (Multi-Process)](./pattern-g-multi-agent-multi-process/) | Manager routes dynamically | Multi-Process | ✅ Done |
| [H - Bedrock Agent](./pattern-h-bedrock-agent/) | AWS-managed agent | Managed | ✅ Done |

### Implementation Status

```
✅ Local Patterns: A → B → C → D → E → F → G → H (all done!)
☁️ AWS Deployed:   A → B → C → D → E → F → G → H (live on Lambda)
```

## The Spectrum

```
Control ←——————————————————————————————————————————→ Autonomy

  A       B       C       D       E       F       G       H
  │       │       │       │       │       │       │       │
  No    Workflow Workflow Function Single Multi  Multi  Bedrock
 Agent  (Single) (Multi)  Calling  Agent  Agent  Agent  (Managed)
  │       │       │       │       │       │       │       │
 You    Fixed   Fixed    LLM     Agent  Manager Manager  AWS
control steps   steps  suggests controls routes  routes manages
 all   (single) (multi)  you      loop
                        control
```

## Live Demo

Try the deployed patterns (AWS Lambda + API Gateway):

| Pattern | Health Check | Chat Endpoint |
|---------|--------------|---------------|
| A - AI as Service | [Health](https://7jtqo8ncu4.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://7jtqo8ncu4.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |
| B - Workflow (Single) | [Health](https://jwmoovw1se.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://jwmoovw1se.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |
| C - Workflow (Multi) | [Health](https://1ywzwz1hog.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://1ywzwz1hog.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |
| D - Function Calling | [Health](https://3sd40p0zz4.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://3sd40p0zz4.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |
| E - Single Agent | [Health](https://ok1ro2wdf1.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://ok1ro2wdf1.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |
| F - Multi-Agent (Single) | [Health](https://seymcwtuh9.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://seymcwtuh9.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |
| G - Multi-Agent (Multi) | [Health](https://nwnh1ys1u8.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://nwnh1ys1u8.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |
| H - Bedrock Agent | [Health](https://dck1pppjal.execute-api.us-east-1.amazonaws.com/health) | `curl -X POST https://dck1pppjal.execute-api.us-east-1.amazonaws.com/chat -H "Content-Type: application/json" -d '{"message": "Book tomorrow at 3pm"}'` |

## Tech Stack

- **Language:** Python
- **Package Manager:** UV
- **AI Providers:** OpenAI, Anthropic Claude, AWS Bedrock
- **Agent Framework:** OpenAI Agents SDK
- **API:** FastAPI
- **Infrastructure:** AWS Lambda, Terraform, AWS CDK
- **Database:** DynamoDB

## Use Case

All patterns implement a tennis court booking system:

```
check_availability(date, time) → returns available slots
book(slot_id, user_id)         → reserves a slot
```

The difference: **who decides which function to call and when**.

## Repo Structure

```
ai-orchestration-patterns/
├── README.md
├── pattern-a-ai-as-service/
├── pattern-b-workflow-single-process/
├── pattern-c-workflow-multi-process/
├── pattern-d-function-calling/
├── pattern-e-single-agent/
├── pattern-f-multi-agent-single-process/
├── pattern-g-multi-agent-multi-process/
├── pattern-h-bedrock-agent/
├── shared/
│   └── booking-db/           # Mock DynamoDB for all patterns
└── terraform/                # Infrastructure as code (coming soon)
```

Each pattern folder:

```
pattern-x/
├── README.md                 # Pattern-specific docs
├── src/                      # Implementation
├── infra/                    # Terraform / CDK
└── tests/
```

## Getting Started

```bash
cd pattern-d-function-calling
uv run src/demo.py
```

## Why This Repo?

- **Real infrastructure** — not just pseudocode
- **Clear progression** — deterministic → controlled → autonomous
- **Trade-off analysis** — when to use each pattern
- **Production patterns** — what actually works in enterprise

## Author

**Moss Gu**

- 🌐 [Blog](https://mossgreen.github.io)
- 💼 [LinkedIn](https://www.linkedin.com/in/mossgu)
- 🐙 [GitHub](https://github.com/mossgreen)

## License

MIT

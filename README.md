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
| [A - AI as Service](./pattern-a-ai-as-service/) | No agent, LLM parses only | Shared | ⏳ Planned |
| [B - Workflow (Shared)](./pattern-b-workflow-shared/) | Fixed sequence | Shared | ⏳ Planned |
| [C - Workflow (Independent)](./pattern-c-workflow-independent/) | Fixed sequence | Independent services | 🚧 In Progress |
| [D - Function Calling](./pattern-d-function-calling/) | LLM suggests, you control loop | Shared | ⏳ Planned |
| [E - Single Agent](./pattern-e-single-agent/) | Agent controls the loop | Shared | ⏳ Planned |
| [F - Multi-Agent (Shared)](./pattern-f-multi-agent-shared/) | Manager routes dynamically | Shared | ⏳ Planned |
| [G - Multi-Agent (Independent)](./pattern-g-multi-agent-independent/) | Manager routes dynamically | Independent services | ⏳ Planned |
| [H - Bedrock Agent](./pattern-h-bedrock-agent/) | AWS-managed agent | Managed | ⏳ Planned |

### Implementation Priority

```
Phase 1: C → D → E → G → H  (core patterns, in progress)
Phase 2: A → B → F          (simpler variants, later)
```

## The Spectrum

```
Control ←——————————————————————————————————————————→ Autonomy

  A       B       C       D       E       F       G       H
  │       │       │       │       │       │       │       │
  No    Workflow Workflow Function Single Multi  Multi  Bedrock
 Agent  (Shared) (Indep.) Calling  Agent  Agent  Agent  (Managed)
  │       │       │       │       │       │       │       │
 You    Fixed   Fixed    LLM     Agent  Manager Manager  AWS
control steps   steps  suggests controls routes  routes manages
 all   (shared) (indep.) you      loop
                        control
```

## Tech Stack

- **Language:** Python
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
├── pattern-b-workflow-shared/
├── pattern-c-workflow-independent/
├── pattern-d-function-calling/
├── pattern-e-single-agent/
├── pattern-f-multi-agent-shared/
├── pattern-g-multi-agent-independent/
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
cd pattern-c-workflow-independent
pip install -r requirements.txt
terraform init && terraform apply  # coming soon
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

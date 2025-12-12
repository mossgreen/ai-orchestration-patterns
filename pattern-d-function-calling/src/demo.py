"""
CLI demo for Pattern D: Function Calling.

Run with:
    cd pattern-d-function-calling
    uv venv && source .venv/bin/activate
    uv pip install -r requirements.txt
    python src/demo.py          # Interactive mode
    python src/demo.py --auto   # Auto demo: book a slot

Each request is stateless, but we pass the last response
for context (so "B" works after seeing options A, B, C).
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.function_caller import run_conversation


async def run_auto_demo() -> None:
    """Run a scripted demo showing the full booking flow."""
    print("=" * 60)
    print("Pattern D: Function Calling - Auto Demo")
    print("=" * 60)
    print()

    # Single request that triggers check_availability + book_slot
    user_message = "I want to book a tennis court this Saturday at 13:00, any court is fine"

    print(f"User: {user_message}")
    response = await run_conversation(user_message)
    print()
    print(f"Assistant: {response}")
    print()
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


async def run_interactive() -> None:
    """Run an interactive demo with lightweight context passing."""
    print("=" * 60)
    print("Pattern D: Function Calling Demo")
    print("=" * 60)
    print()
    print("Example: 'Book a court for tomorrow at 2pm'")
    print("Then: 'B' to select Court B")
    print()
    print("Type 'quit' to exit, 'clear' to reset context")
    print("=" * 60)

    # Track only the last response for context
    last_response = None

    while True:
        print()
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if user_input.lower() == "clear":
            last_response = None
            print("[Context cleared]")
            continue

        # Pass last response for context (so "B" works after seeing options)
        response = await run_conversation(user_input, previous_response=last_response)

        # Save for next turn
        last_response = response

        print()
        print(f"Assistant: {response}")


async def main() -> None:
    """Entry point - check for --auto flag."""
    if "--auto" in sys.argv:
        await run_auto_demo()
    else:
        await run_interactive()


if __name__ == "__main__":
    asyncio.run(main())

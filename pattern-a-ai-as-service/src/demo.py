"""
CLI demo for Pattern A: AI as Service.

Run with:
    cd pattern-a-ai-as-service
    source ../.venv/bin/activate
    python -m src.demo

This demo clearly shows the separation:
- AI is used ONLY for parsing
- YOUR code handles all business logic
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import parse_intent
from src.booking import process_booking


DEFAULT_MESSAGE = "Book tomorrow afternoon, first slot please"


async def run_demo(message: str):
    """Run the demo with a given message."""
    print("=" * 60)
    print("Pattern A: AI as Service Demo")
    print("=" * 60)
    print()
    print("Key insight: LLM is ONLY used for parsing text.")
    print("All business logic is YOUR code - no AI involved.")
    print()
    print(f"User message: \"{message}\"")
    print()
    print("-" * 40)

    # Step 1: Parse with AI (the ONLY AI component)
    print("[AI] Parsing your message...")
    intent = await parse_intent(message)
    print(f"[AI] Extracted:")
    print(f"       date = {intent.date}")
    print(f"       time = {intent.time}")
    print(f"       slot_preference = {intent.slot_preference}")
    print()

    # Step 2: Process with YOUR code (no AI)
    print("[YOUR CODE] Processing booking...")
    print("[YOUR CODE] Checking availability...")
    print("[YOUR CODE] Selecting slot...")
    print("[YOUR CODE] Booking...")
    result = process_booking(intent)

    print("-" * 40)
    print()
    print(f"Result:\n{result}")
    print()


def main():
    """Run the demo with default message or command line argument."""
    message = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MESSAGE
    asyncio.run(run_demo(message))


if __name__ == "__main__":
    main()

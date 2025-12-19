"""
CLI demo for Pattern A: AI as Service.

Run with:
    cd pattern-a-ai-as-service
    uv run python -m src.demo

This demo clearly shows the separation:
- AI is used ONLY for parsing
- YOUR code handles all business logic
"""

import asyncio
import logging
import sys

from .booking import process_booking
from .exceptions import BookingError, ParseError
from .parser import parse_intent
from .services import booking_service
from .settings import get_settings

DEFAULT_MESSAGE = "Book tomorrow afternoon, first slot please"


async def run_demo(message: str) -> None:
    """Run the demo with a given message."""
    print("=" * 60)
    print("Pattern A: AI as Service Demo")
    print("=" * 60)
    print()
    print("Key insight: LLM is ONLY used for parsing text.")
    print("All business logic is YOUR code - no AI involved.")
    print()
    print(f'User message: "{message}"')
    print()
    print("-" * 40)

    try:
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
        result = process_booking(intent, booking_service=booking_service)

        print("-" * 40)
        print()
        print(f"Result:\n{result}")
        print()

    except ParseError as e:
        print(f"\nParse Error: {e}")
        sys.exit(1)

    except BookingError as e:
        print(f"\nBooking Error: {e}")
        sys.exit(1)


def main() -> None:
    """Run the demo with default message or command line argument."""
    # Configure logging based on settings
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    message = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MESSAGE
    asyncio.run(run_demo(message))


if __name__ == "__main__":
    main()

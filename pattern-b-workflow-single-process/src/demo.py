"""
CLI demo for Pattern B: Workflow (Shared Runtime).

Run with: python -m pattern-b-workflow-single-process.src.demo
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import run_workflow

REQUEST = "Book a tennis court tomorrow afternoon, any slot"


def main():
    """Run a simple demo of the fixed workflow."""
    print("=" * 60)
    print("Pattern B: Workflow (Shared Runtime) Demo")
    print("=" * 60)
    print()
    print("This pattern runs a FIXED sequence of steps:")
    print("  1. Parse Intent  -> Extract date/time from message")
    print("  2. Check Availability -> Find available slots")
    print("  3. Book Slot -> Reserve first available")
    print()
    print(f"Request: {REQUEST}")
    print()

    result = asyncio.run(run_workflow(REQUEST, verbose=True))
    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()

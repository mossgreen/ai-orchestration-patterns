"""
CLI demo for Pattern F: Multi-Agent (Shared Runtime) booking system.

Run with: uv run src/demo.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import Runner
from src.agent import manager_agent


def main():
    """Run an interactive demo booking conversation."""
    print("=" * 60)
    print("Pattern F: Multi-Agent (Shared Runtime) Demo")
    print("=" * 60)
    print("Manager routes your requests to specialized agents:")
    print("  - Availability Specialist: checks available slots")
    print("  - Booking Specialist: books your chosen slot")
    print()
    print("Type 'quit' to exit")
    print()

    # Start with a booking request
    user_input = "I'd like to book a tennis court for tomorrow around 3pm"
    print(f"User: {user_input}")
    print()

    # Track conversation history
    conversation = None

    while True:
        # Run manager with conversation history
        if conversation is None:
            result = Runner.run_sync(manager_agent, user_input)
        else:
            # Append new user message to history
            conversation.append({"role": "user", "content": user_input})
            result = Runner.run_sync(manager_agent, conversation)

        print(f"Agent: {result.final_output}")
        print()

        # Update conversation history
        conversation = result.to_input_list()

        # Get next user input
        user_input = input("User: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()

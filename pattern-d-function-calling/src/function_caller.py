"""
Pattern D: Function Calling - Tennis Court Booking

KEY DIFFERENCE from Pattern E:
- Pattern E: Runner.run() handles everything automatically
- Pattern D: YOU write the loop, YOU execute functions, YOU control everything

This file demonstrates the explicit control loop that agent SDKs hide from you.
Uses true async I/O for non-blocking API calls.
"""

import json
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageToolCall
from pathlib import Path
from typing import Optional

# Load .env from project root (two levels up from src/function_caller.py)
load_dotenv(Path(__file__).parents[2] / ".env")

# Add parent directory to path for shared imports
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])
from shared.booking_service import get_booking_service

# Initialize clients
# AsyncOpenAI for true non-blocking I/O
client = AsyncOpenAI()  # Uses OPENAI_API_KEY from environment
booking_service = get_booking_service()

# ============================================================
# SECTION B: Tool Definitions (JSON Schema format)
# ============================================================
# These tell OpenAI what functions are available.
# OpenAI will return tool_calls suggesting which to use.
# YOUR CODE decides whether to actually execute them.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available tennis court slots for a given date. Call this FIRST before booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (e.g., '2024-12-15')"
                    },
                    "time": {
                        "type": "string",
                        "description": "Optional time in HH:MM format (e.g., '14:00')"
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_slot",
            "description": "Book a specific tennis court slot. Requires a slot_id from check_availability results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slot_id": {
                        "type": "string",
                        "description": "The slot ID from check_availability results (e.g., '2024-12-15_CourtA_1400')"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User making the booking (defaults to 'guest')"
                    }
                },
                "required": ["slot_id"]
            }
        }
    }
]


# ============================================================
# SECTION C: Function Implementations
# ============================================================
# These are the actual functions that YOUR CODE executes.
# They are NOT called by OpenAI - OpenAI just suggests them.

def check_availability(date: str, time: Optional[str] = None) -> str:
    """
    Check available tennis court slots for a given date.

    Args:
        date: Date in YYYY-MM-DD format
        time: Optional time in HH:MM format

    Returns:
        Formatted string of available slots
    """
    slots = booking_service.check_availability(date, time)

    if not slots:
        return f"No available slots found for {date}" + (f" at {time}" if time else "")

    result = f"Available slots for {date}:\n"
    for slot in slots:
        result += f"  - {slot['court']} at {slot['time']} (ID: {slot['slot_id']})\n"

    return result


def book_slot(slot_id: str, user_id: str = "guest") -> str:
    """
    Book a specific tennis court slot.

    Args:
        slot_id: The slot ID from check_availability
        user_id: User making the booking

    Returns:
        Booking confirmation or error message
    """
    result = booking_service.book(slot_id, user_id)

    if result["success"]:
        return (
            f"Booking confirmed!\n"
            f"  Booking ID: {result['booking_id']}\n"
            f"  Court: {result['court']}\n"
            f"  Date: {result['date']}\n"
            f"  Time: {result['time']}"
        )
    else:
        return f"Booking failed: {result['error']}"


# Map function names to implementations
# This lets us look up functions dynamically when OpenAI suggests them
AVAILABLE_FUNCTIONS = {
    "check_availability": check_availability,
    "book_slot": book_slot,
}


# ============================================================
# SECTION D: The Control Loop
# ============================================================
# THIS IS THE KEY DIFFERENCE FROM PATTERN E.
# You write every step. You control everything.

def get_system_prompt() -> str:
    """Generate system prompt with current datetime."""
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M (%A)")

    return f"""You are a tennis court booking assistant.

    CURRENT DATETIME: {current_datetime}
    
    You can check availability and book courts. Understand user intent and act accordingly.
    - Convert relative dates ("tomorrow", "this Saturday") to YYYY-MM-DD format
    - Always check availability before booking"""


def execute_tool_call(tool_call: ChatCompletionMessageToolCall) -> str:
    """
    Execute a single tool call and return the result.

    This is where YOUR CODE decides what to do with LLM's suggestion.
    You could:
    - Execute it directly (what we do here)
    - Log it first
    - Ask for user confirmation
    - Reject certain functions
    - Add rate limiting

    Args:
        tool_call: The tool call object from OpenAI response

    Returns:
        String result of the function execution
    """
    function_name = tool_call.function.name

    # Parse the arguments from JSON string
    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return f"Error: Could not parse arguments for {function_name}"

    # Look up the function
    if function_name not in AVAILABLE_FUNCTIONS:
        return f"Error: Unknown function {function_name}"

    # Get the function and call it
    func = AVAILABLE_FUNCTIONS[function_name]

    # Log what we're about to do (helpful for debugging and demos)
    print(f"  [Executing] {function_name}({arguments})")

    # Execute the function with the arguments
    try:
        result = func(**arguments)
        return result
    except Exception as e:
        return f"Error executing {function_name}: {str(e)}"


async def run_conversation(user_message: str, previous_response: Optional[str] = None) -> str:
    """
    Run a complete conversation with function calling.

    THIS IS THE MAIN CONTROL LOOP.

    Uses true async I/O - the event loop is free to handle other requests
    while waiting for OpenAI API responses.

    The loop:
    1. Send user message to OpenAI (with tools available)
    2. Check if OpenAI wants to call any functions
    3. If yes: execute functions, send results back, go to step 1
    4. If no: return the final text response

    Args:
        user_message: The user's input
        previous_response: Optional last assistant response for context

    Returns:
        The assistant's final response
    """
    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": get_system_prompt()},
    ]

    # Add previous response if provided
    if previous_response:
        messages.append({"role": "assistant", "content": previous_response})

    messages.append({"role": "user", "content": user_message})

    # Loop until we get a final response (no more tool calls)
    while True:
        print(f"\n[Calling OpenAI API...]")

        # Step 1: Call OpenAI with our messages and tools
        # await yields control to event loop - other requests can be handled
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"  # Let LLM decide when to use tools
        )

        # Get the assistant's message
        assistant_message = response.choices[0].message

        # Step 2: Check if there are tool calls
        if assistant_message.tool_calls:
            print(f"[LLM wants to call {len(assistant_message.tool_calls)} function(s)]")

            # Add the assistant's message to history (important!)
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in assistant_message.tool_calls
                ]
            })

            # Step 3: Execute each tool call
            for tool_call in assistant_message.tool_calls:
                result = execute_tool_call(tool_call)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Continue the loop - send results back to OpenAI
            continue

        # Step 4: No tool calls - we have a final response
        print("[Final response received]")
        return assistant_message.content

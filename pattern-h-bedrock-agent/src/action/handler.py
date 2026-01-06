"""
Action Group Handler for Bedrock Agent - Pattern H

Receives action invocations from Bedrock Agent and routes to booking service.
"""

import json
from typing import Any

from shared import create_booking_service

# Initialize the booking service
booking_service = create_booking_service()


def handle_action(event: dict) -> dict:
    """
    Handle Bedrock Agent action group invocation.

    Args:
        event: Bedrock Agent action event containing:
            - actionGroup: Name of the action group
            - apiPath: The API path being invoked
            - httpMethod: HTTP method (POST, GET, etc.)
            - parameters: List of parameters with name/value pairs
            - requestBody: Request body for POST operations

    Returns:
        Bedrock-formatted response with action results
    """
    api_path = event.get("apiPath", "")
    http_method = event.get("httpMethod", "POST")
    action_group = event.get("actionGroup", "")

    # Extract parameters from the event
    parameters = {}
    for param in event.get("parameters", []):
        parameters[param["name"]] = param.get("value")

    # Route to appropriate handler based on API path
    if api_path == "/check-availability":
        result = _check_availability(parameters)
    elif api_path == "/book":
        request_body = event.get("requestBody", {})
        result = _book_slot(request_body)
    else:
        result = {"error": f"Unknown API path: {api_path}"}

    # Return Bedrock-formatted response
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(result)
                }
            }
        }
    }


def _check_availability(params: dict) -> dict:
    """Check tennis court availability."""
    date = params.get("date")
    time = params.get("time")

    if not date:
        return {"error": "Date parameter is required"}

    slots = booking_service.check_availability(date, time)

    return {
        "slots": [
            {
                "slot_id": slot.slot_id,
                "court": slot.court,
                "date": slot.date,
                "time": slot.time
            }
            for slot in slots
        ]
    }


def _book_slot(request_body: dict) -> dict:
    """Book a tennis court slot."""
    # Extract slot_id from request body
    # Bedrock sends: {"content": {"application/json": {"properties": [{"name": "slot_id", "value": "..."}]}}}
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    properties = json_content.get("properties", [])

    slot_id = None
    for prop in properties:
        if prop.get("name") == "slot_id":
            slot_id = prop.get("value")
            break

    if not slot_id:
        return {"error": "slot_id is required in request body"}

    try:
        booking = booking_service.book(slot_id)
        return {
            "booking_id": booking.booking_id,
            "court": booking.court,
            "date": booking.date,
            "time": booking.time,
            "message": f"Successfully booked {booking.court} on {booking.date} at {booking.time}"
        }
    except Exception as e:
        return {"error": f"Booking failed: {str(e)}"}

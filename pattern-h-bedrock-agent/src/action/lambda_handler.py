"""AWS Lambda handler for Bedrock Agent Action Group."""

from .handler import handle_action


def handler(event: dict, context) -> dict:
    """
    Lambda handler for Bedrock Agent action group invocations.

    This handler receives events from Bedrock Agent when the agent
    decides to invoke an action from the action group.
    """
    return handle_action(event)

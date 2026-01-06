"""
Bedrock Agent Invoker - Pattern H

Invokes the AWS Bedrock Agent and collects the streaming response.
"""

import boto3

from ..settings import get_settings

settings = get_settings()


def invoke_bedrock_agent(message: str, session_id: str) -> str:
    """
    Invoke the Bedrock Agent and return the response.

    Args:
        message: User's input message
        session_id: Session ID for conversation continuity

    Returns:
        The agent's response text
    """
    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)

    if not settings.bedrock_agent_id or not settings.bedrock_agent_alias_id:
        raise ValueError(
            "BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID must be configured"
        )

    response = client.invoke_agent(
        agentId=settings.bedrock_agent_id,
        agentAliasId=settings.bedrock_agent_alias_id,
        sessionId=session_id,
        inputText=message,
    )

    # Collect the streaming response
    result = ""
    for event in response.get("completion", []):
        if "chunk" in event:
            chunk_data = event["chunk"]
            if "bytes" in chunk_data:
                result += chunk_data["bytes"].decode("utf-8")

    return result


async def invoke_bedrock_agent_async(message: str, session_id: str) -> str:
    """
    Async wrapper for invoke_bedrock_agent.

    Note: boto3 doesn't have native async support, so this runs synchronously.
    For true async, consider using aioboto3.
    """
    return invoke_bedrock_agent(message, session_id)

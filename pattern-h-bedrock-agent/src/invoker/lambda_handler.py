"""AWS Lambda handler for Bedrock Agent Invoker."""

from mangum import Mangum

from .api import app

handler = Mangum(app, lifespan="off")

"""AWS Lambda handler using Mangum adapter for FastAPI."""

from mangum import Mangum

from .api import app

handler = Mangum(app, lifespan="off")
"""AWS Lambda handler for Manager Service."""

from mangum import Mangum

from .api import app

handler = Mangum(app, lifespan="off")

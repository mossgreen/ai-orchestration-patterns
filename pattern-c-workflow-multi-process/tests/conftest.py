"""Pytest configuration for Pattern C tests."""

import os

# Set mock API key before any imports that need it
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-testing")

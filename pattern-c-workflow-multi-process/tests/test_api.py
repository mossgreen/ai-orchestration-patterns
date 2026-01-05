"""Integration tests for Pattern C API."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tomorrow_date():
    """Get tomorrow's date in YYYY-MM-DD format."""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


@pytest.fixture
def mock_openai_response(tomorrow_date):
    """Mock OpenAI response with parsed intent."""
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content=f'{{"date": "{tomorrow_date}", "time": "14:00"}}'))
    ]
    return mock_response


class TestChatEndpoint:
    """Integration tests for /chat endpoint."""

    def test_chat_books_slot_successfully(self, client, mock_openai_response):
        """Verify API can parse message and book a slot end-to-end."""
        with patch("src.services.intent_parser.AsyncOpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create = AsyncMock(
                return_value=mock_openai_response
            )

            response = client.post(
                "/chat",
                json={"message": "Book tomorrow afternoon please"}
            )

            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
            data = response.json()
            assert "response" in data
            assert "Booked" in data["response"] or "booking" in data["response"].lower()

    def test_health_endpoint(self, client):
        """Verify health endpoint works."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

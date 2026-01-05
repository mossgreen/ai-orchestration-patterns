"""Integration tests for Pattern D API."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

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
def mock_tool_call_response(tomorrow_date):
    """Mock OpenAI response with tool calls."""
    tool_call = MagicMock()
    tool_call.id = "call_123"
    tool_call.function.name = "check_availability"
    tool_call.function.arguments = f'{{"date": "{tomorrow_date}", "time": "14:00"}}'

    message = MagicMock()
    message.tool_calls = [tool_call]
    message.content = None

    response = MagicMock()
    response.choices = [MagicMock(message=message)]
    return response


@pytest.fixture
def mock_final_response():
    """Mock OpenAI final response (no tool calls)."""
    message = MagicMock()
    message.tool_calls = None
    message.content = "I found available slots. Would you like me to book one?"

    response = MagicMock()
    response.choices = [MagicMock(message=message)]
    return response


class TestChatEndpoint:
    """Integration tests for /chat endpoint."""

    def test_chat_with_function_calling(
        self, client, mock_tool_call_response, mock_final_response
    ):
        """Verify API handles function calling loop correctly."""
        with patch("src.function_caller.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=[mock_tool_call_response, mock_final_response]
            )
            mock_openai.return_value = mock_client

            response = client.post(
                "/chat", json={"message": "Check availability for tomorrow at 2pm"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert mock_client.chat.completions.create.call_count == 2

    def test_chat_direct_response(self, client, mock_final_response):
        """Verify API handles direct response (no tool calls)."""
        with patch("src.function_caller.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=mock_final_response
            )
            mock_openai.return_value = mock_client

            response = client.post("/chat", json={"message": "Hello"})

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert mock_client.chat.completions.create.call_count == 1

    def test_health_endpoint(self, client):
        """Verify health endpoint works."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["pattern"] == "D"

"""
Demo for Pattern C: Workflow (Multi Process).

Calls the real API endpoint (in-process, no server needed).

Run with:
    cd pattern-c-workflow-multi-process
    uv run python -m src.demo
"""

from fastapi.testclient import TestClient

from .api import app


def main() -> None:
    message = "Book tomorrow afternoon please"

    print(f'Message: "{message}"')
    print()

    client = TestClient(app)
    response = client.post("/chat", json={"message": message})

    if response.status_code == 200:
        print(response.json()["response"])
    else:
        print(f"Error {response.status_code}: {response.json()}")


if __name__ == "__main__":
    main()

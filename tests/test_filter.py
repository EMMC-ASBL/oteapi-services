"""Test data filter."""
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_filter(client: "TestClient") -> None:
    """Test creating a filter."""
    response = client.post(
        "/filter/",
        json={
            "filterType": "filter/demo",
            "query": "SELECT * FROM Test",
            "condition": "",
            "limit": 1,
            "configuration": {},
        },
    )
    # Ensure that session returns with a session id
    assert "filter_id" in response.json()
    assert response.status_code == 200, f"Response:\n{json.dumps(response.json())}"


def test_get_filter(client: "TestClient") -> None:
    """Test getting a filter."""
    response = client.get("/filter/filter-961f5314-9e8e-411e-a216-ba0eb8e8bc6e")
    assert response.status_code == 200, f"Response:\n{json.dumps(response.json())}"


def test_initialize_filter(client: "TestClient") -> None:
    """Test initializing a filter."""
    response = client.post(
        "/filter/filter-961f5314-9e8e-411e-a216-ba0eb8e8bc6e/initialize", json={}
    )
    assert response.status_code == 200, f"Response:\n{json.dumps(response.json())}\nResponse URL: {response.url}"

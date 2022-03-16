"""Test function."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_function(client: "TestClient") -> None:
    """Test creating a function."""
    response = client.post(
        "/function/",
        json={
            "functionType": "function/demo",
            "configuration": {},
        },
    )
    assert "function_id" in response.json()
    assert response.status_code == 200


def test_get_function(client: "TestClient") -> None:
    """Test getting a function."""
    response = client.get("/function/function-a647012a-7ab9-4f2c-9c13-2564aa6d95a1")
    assert response.status_code == 200


def test_initialize_function(client: "TestClient") -> None:
    """Test initializing a function."""
    response = client.post(
        "/function/function-a647012a-7ab9-4f2c-9c13-2564aa6d95a1/initialize", json={}
    )
    assert response.status_code == 200

"""Test mapping."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

def test_create_mapping(client: "TestClient") -> None:
    """Test creating a mapping."""
    response = client.post(
        "/mapping/",
        json={
            "mappingType": "mapping/demo",
            "prefixes": {},
            "triples": [["a", "b", "c"]],
            "configuration": {},
        },
    )
    assert "mapping_id" in response.json()
    assert response.status_code == 200


def test_get_mapping(client: "TestClient") -> None:
    """Test getting a mapping."""
    response = client.get("/mapping/mapping-a2d6b3d5-9b6b-48a3-8756-ae6d4fd6b81e")
    assert response.status_code == 200


def test_initialize_mapping(client: "TestClient") -> None:
    """Test initializing a mapping."""
    response = client.post(
        "/mapping/mapping-a2d6b3d5-9b6b-48a3-8756-ae6d4fd6b81e/initialize", json={}
    )
    assert response.status_code == 200

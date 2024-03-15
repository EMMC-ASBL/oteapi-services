"""Test session."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_list_session(client: "TestClient", test_data: "dict[str, dict]") -> None:
    """Test listing sessions."""
    response = client.get("/session")
    assert response.json() == {
        "keys": [entry for entry in test_data if entry.startswith("session-")]
    }
    assert response.status_code == 200


def test_create_session(client: "TestClient") -> None:
    """Test creating a session."""
    response = client.post(
        "/session/",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"foo": "bar"},
    )
    # Ensure that session returns with a session id
    assert "session_id" in response.json()
    assert response.status_code == 200

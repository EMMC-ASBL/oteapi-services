"""Test function."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Literal

    from fastapi.testclient import TestClient


def test_create_function(client: TestClient) -> None:
    """Test creating a function."""
    response = client.post(
        "/function/",
        json={
            "functionType": "function/demo",
            "configuration": {},
        },
        headers={"Content-Type": "application/json"},
    )
    assert "function_id" in response.json()
    assert response.status_code == 200


def test_create_function_auth_model(client: TestClient) -> None:
    """Test creating a function with a secret passed through the model."""
    dummy_secret = "Bearer 123"
    response = client.post(
        "/function/",
        json={
            "functionType": "function/demo",
            "configuration": {},
            "token": dummy_secret,
        },
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200

    response = client.get(f"/admin/redis/{response.json()['function_id']}")
    assert response.status_code == 200
    assert response.json().get("token") == dummy_secret


def test_create_function_auth_headers(client: TestClient) -> None:
    """Test creating a function with a secret passed through the request headers."""
    dummy_secret = "Bearer 123"
    response = client.post(
        "/function/",
        json={
            "functionType": "function/demo",
            "configuration": {},
        },
        headers={"Authorization": dummy_secret, "Content-Type": "application/json"},
    )
    assert response.status_code == 200

    response = client.get(f"/admin/redis/{response.json()['function_id']}")
    assert response.status_code == 200
    assert response.json().get("token") == dummy_secret


def test_get_function(client: TestClient, test_data: dict[str, str]) -> None:
    """Test getting a function."""
    function_id = next(_ for _ in test_data if _.startswith("function-"))
    response = client.get(
        f"/function/{function_id}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


def test_initialize_function(client: TestClient, test_data: dict[str, str]) -> None:
    """Test initializing a function."""
    function_id = next(_ for _ in test_data if _.startswith("function-"))
    response = client.post(
        f"/function/{function_id}/initialize",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


@pytest.mark.parametrize("method", ["initialize", "get"])
def test_session_config_merge(
    client: TestClient,
    test_data: dict[str, str],
    method: Literal["initialize", "get"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the current session is merged into the strategy configuration."""
    import json

    from oteapi.models import FunctionConfig
    from oteapi.plugins import create_strategy

    original_create_strategy = create_strategy

    function_id = next(_ for _ in test_data if _.startswith("function-"))
    session_id = next(_ for _ in test_data if _.startswith("session-"))

    expected_merged_config = json.loads(test_data[function_id])
    expected_merged_config["configuration"].update(json.loads(test_data[session_id]))

    def create_strategy_middleware(
        strategy_type: Literal["function"], config: FunctionConfig
    ):
        """Create a strategy middleware - do some testing."""
        assert strategy_type == "function"
        assert isinstance(config, FunctionConfig)

        # THIS is where we test the session has been properly merged into the strategy
        # configuration !
        assert (
            config.model_dump(mode="json", exclude_unset=True) == expected_merged_config
        )

        return original_create_strategy(strategy_type, config)

    monkeypatch.setattr(
        "app.routers.function.create_strategy", create_strategy_middleware
    )

    if method == "initialize":
        response = client.post(
            f"/function/{function_id}/initialize",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
        )
    else:  # method == "get"
        response = client.get(
            f"/function/{function_id}",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
        )

    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}\nResponse URL: {response.url}"

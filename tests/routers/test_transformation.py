"""Test transformation."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Literal

    from fastapi.testclient import TestClient


def test_create_transformation(client: "TestClient") -> None:
    """Test creating a transformation."""
    response = client.post(
        "/transformation/",
        json={
            "transformationType": "script/dummy",
            "name": "script/dummy",
            "configuration": {},
        },
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


def test_create_transformation_auth_model(client: "TestClient") -> None:
    """Test creating a transformation through the model."""
    dummy_secret = "Bearer 123"
    response = client.post(
        "/transformation/",
        json={
            "transformationType": "script/dummy",
            "name": "script/dummy",
            "configuration": {},
            "token": dummy_secret,
        },
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200

    response = client.get(f"/redis/{response.json()['transformation_id']}")
    assert response.status_code == 200
    assert response.json().get("token") == dummy_secret


def test_create_transformation_auth_headers(client: "TestClient") -> None:
    """Test creating a transformation through the request headers."""
    dummy_secret = "Bearer 123"
    response = client.post(
        "/transformation/",
        json={
            "transformationType": "script/dummy",
            "name": "script/dummy",
            "configuration": {},
        },
        headers={"Authorization": dummy_secret, "Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200

    response = client.get(f"/redis/{response.json()['transformation_id']}")
    assert response.status_code == 200
    assert response.json().get("token") == dummy_secret


def test_get_transformation(client: "TestClient", test_data: dict[str, str]) -> None:
    """Test getting a transformation."""
    transformation_id = next(_ for _ in test_data if _.startswith("transformation-"))
    response = client.get(
        f"/transformation/{transformation_id}",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


def test_initialize_transformation(
    client: "TestClient", test_data: dict[str, str]
) -> None:
    """Test initializing a transformation."""
    transformation_id = next(_ for _ in test_data if _.startswith("transformation-"))
    response = client.post(
        f"/transformation/{transformation_id}/initialize",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


def test_get_transformation_status(
    client: "TestClient", test_data: dict[str, str]
) -> None:
    """Test getting a transformation status."""
    from oteapi.models.transformationconfig import TransformationStatus
    from pydantic import ValidationError

    transformation_id = next(_ for _ in test_data if _.startswith("transformation-"))
    response = client.get(
        f"/transformation/{transformation_id}/status?task_id=",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    try:
        TransformationStatus(**response.json())
    except ValidationError as exc:
        pytest.fail(f"Failed to validate as a `TransformationStatus`. Exc: {exc}")
    assert response.status_code == 200


def test_execute_transformation(
    client: "TestClient", test_data: dict[str, str]
) -> None:
    """Test executing a transformation."""
    transformation_id = next(_ for _ in test_data if _.startswith("transformation-"))
    response = client.post(
        f"/transformation/{transformation_id}/execute",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


@pytest.mark.parametrize("method", ["initialize", "get"])
def test_session_config_merge(
    client: "TestClient",
    test_data: dict[str, str],
    method: 'Literal["initialize", "get"]',
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """Test the current session is merged into the strategy configuration."""
    import json

    from oteapi.models import TransformationConfig
    from oteapi.plugins import create_strategy

    original_create_strategy = create_strategy

    transformation_id = next(_ for _ in test_data if _.startswith("transformation-"))
    session_id = next(_ for _ in test_data if _.startswith("session-"))

    expected_merged_config = json.loads(test_data[transformation_id])
    expected_merged_config["configuration"].update(json.loads(test_data[session_id]))

    def create_strategy_middleware(
        strategy_type: 'Literal["transformation"]', config: TransformationConfig
    ):
        """Create a strategy middleware - do some testing."""
        assert strategy_type == "transformation"
        assert isinstance(config, TransformationConfig)

        # THIS is where we test the session has been properly merged into the strategy
        # configuration !
        assert (
            config.model_dump(mode="json", exclude_unset=True) == expected_merged_config
        )

        return original_create_strategy(strategy_type, config)

    monkeypatch.setattr(
        "app.routers.transformation.create_strategy", create_strategy_middleware
    )

    if method == "initialize":
        response = client.post(
            f"/transformation/{transformation_id}/initialize",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=(3.0, 27.0),
        )
    else:  # method == "get"
        response = client.get(
            f"/transformation/{transformation_id}",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=(3.0, 27.0),
        )

    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}\nResponse URL: {response.url}"

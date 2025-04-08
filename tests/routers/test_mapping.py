"""Test mapping."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Literal

    from fastapi.testclient import TestClient


def test_create_mapping(client: TestClient) -> None:
    """Test creating a mapping."""
    response = client.post(
        "/mapping/",
        json={
            "mappingType": "mapping/demo",
            "prefixes": {},
            "triples": [["a", "b", "c"]],
            "configuration": {},
        },
        headers={"Content-Type": "application/json"},
    )
    assert "mapping_id" in response.json()
    assert response.status_code == 200


def test_get_mapping(client: TestClient, test_data: dict[str, str]) -> None:
    """Test getting a mapping."""
    mapping_id = next(_ for _ in test_data if _.startswith("mapping-"))
    response = client.get(
        f"/mapping/{mapping_id}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


def test_initialize_mapping(client: TestClient, test_data: dict[str, str]) -> None:
    """Test initializing a mapping."""
    mapping_id = next(_ for _ in test_data if _.startswith("mapping-"))
    response = client.post(
        f"/mapping/{mapping_id}/initialize",
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

    from oteapi.models import MappingConfig
    from oteapi.plugins import create_strategy

    original_create_strategy = create_strategy

    mapping_id = next(_ for _ in test_data if _.startswith("mapping-"))
    session_id = next(_ for _ in test_data if _.startswith("session-"))

    expected_merged_config = json.loads(test_data[mapping_id])
    expected_merged_config["configuration"].update(json.loads(test_data[session_id]))

    def create_strategy_middleware(
        strategy_type: Literal["mapping"], config: MappingConfig
    ):
        """Create a strategy middleware - do some testing."""
        assert strategy_type == "mapping"
        assert isinstance(config, MappingConfig)

        # THIS is where we test the session has been properly merged into the strategy
        # configuration !
        assert (
            config.model_dump(mode="json", exclude_unset=True) == expected_merged_config
        )

        return original_create_strategy(strategy_type, config)

    monkeypatch.setattr(
        "app.routers.mapping.create_strategy", create_strategy_middleware
    )

    if method == "initialize":
        response = client.post(
            f"/mapping/{mapping_id}/initialize",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
        )
    else:  # method == "get"
        response = client.get(
            f"/mapping/{mapping_id}",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
        )

    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}\nResponse URL: {response.url}"

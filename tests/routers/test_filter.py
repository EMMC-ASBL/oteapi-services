"""Test data filter."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Literal

    from fastapi.testclient import TestClient


def test_create_filter(client: TestClient) -> None:
    """Test creating a filter."""
    import json

    response = client.post(
        "/filter/",
        json={
            "filterType": "filter/demo",
            "query": "SELECT * FROM Test",
            "condition": "",
            "limit": 1,
            "configuration": {},
        },
        headers={"Content-Type": "application/json"},
    )
    # Ensure that session returns with a session id
    assert "filter_id" in response.json()
    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}"


def test_get_filter(client: TestClient, test_data: dict[str, str]) -> None:
    """Test getting a filter."""
    import json

    filter_id = next(_ for _ in test_data if _.startswith("filter-"))
    response = client.get(
        f"/filter/{filter_id}",
        headers={"Content-Type": "application/json"},
    )
    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}"


def test_initialize_filter(client: TestClient, test_data: dict[str, str]) -> None:
    """Test initializing a filter."""
    import json

    filter_id = next(_ for _ in test_data if _.startswith("filter-"))
    response = client.post(
        f"/filter/{filter_id}/initialize",
        headers={"Content-Type": "application/json"},
    )
    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}\nResponse URL: {response.url}"


@pytest.mark.parametrize("method", ["initialize", "get"])
def test_session_config_merge(
    client: TestClient,
    test_data: dict[str, str],
    method: Literal["initialize", "get"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the current session is merged into the strategy configuration."""
    import json

    from oteapi.models import FilterConfig
    from oteapi.plugins import create_strategy

    original_create_strategy = create_strategy

    filter_id = next(_ for _ in test_data if _.startswith("filter-"))
    session_id = next(_ for _ in test_data if _.startswith("session-"))

    expected_merged_config = json.loads(test_data[filter_id])
    expected_merged_config["configuration"].update(json.loads(test_data[session_id]))

    def create_strategy_middleware(
        strategy_type: Literal["filter"], config: FilterConfig
    ):
        """Create a strategy middleware - do some testing."""
        assert strategy_type == "filter"
        assert isinstance(config, FilterConfig)

        # THIS is where we test the session has been properly merged into the strategy
        # configuration !
        assert (
            config.model_dump(mode="json", exclude_unset=True) == expected_merged_config
        )

        return original_create_strategy(strategy_type, config)

    monkeypatch.setattr(
        "app.routers.datafilter.create_strategy", create_strategy_middleware
    )

    if method == "initialize":
        response = client.post(
            f"/filter/{filter_id}/initialize",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
        )
    else:  # method == "get"
        response = client.get(
            f"/filter/{filter_id}",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
        )

    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}\nResponse URL: {response.url}"

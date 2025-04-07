"""Test dataresource"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Literal

    from fastapi.testclient import TestClient


def test_create_dataresource(client: "TestClient") -> None:
    """Test create dataresource."""
    response = client.post(
        "/dataresource/",
        json={
            "downloadUrl": "https://filesamples.com/sample2.json",
            "mediaType": "application/json",
            "resourceType": "resource/demo",
        },
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


def test_get_dataresource_info(client: "TestClient", test_data: dict[str, str]) -> None:
    """Test get dataresource info."""
    dataresource_id = next(_ for _ in test_data if _.startswith("dataresource-"))
    response = client.get(
        f"/dataresource/{dataresource_id}/info",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


def test_read_dataresource(client: "TestClient", test_data: dict[str, str]) -> None:
    """Test read dataresource."""
    dataresource_id = next(_ for _ in test_data if _.startswith("dataresource-"))
    response = client.get(
        f"/dataresource/{dataresource_id}",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


def test_initialize_dataresource(
    client: "TestClient", test_data: dict[str, str]
) -> None:
    """Test initialize dataresource."""
    dataresource_id = next(_ for _ in test_data if _.startswith("dataresource-"))
    response = client.post(
        f"/dataresource/{dataresource_id}/initialize",
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

    from oteapi.models import ResourceConfig
    from oteapi.plugins import create_strategy

    original_create_strategy = create_strategy

    dataresource_id = next(_ for _ in test_data if _.startswith("dataresource-"))
    session_id = next(_ for _ in test_data if _.startswith("session-"))

    expected_merged_config = json.loads(test_data[dataresource_id])
    assert "configuration" not in expected_merged_config
    expected_merged_config["configuration"] = json.loads(test_data[session_id])

    def create_strategy_middleware(
        strategy_type: 'Literal["resource"]', config: ResourceConfig
    ):
        """Create a strategy middleware - do some testing."""
        assert strategy_type == "resource"
        assert isinstance(config, ResourceConfig)

        # THIS is where we test the session has been properly merged into the strategy
        # configuration !
        # Cannot use exclude_unset because the 'configuration' is not set originally.
        # When 'configuration' is updated, this does not change the original pydantic
        # model understanding that the 'configuration' is not set.
        # So instead, we use exclude_none to include the 'configuration' key in the
        # dumped dict, but exclude the non-overwritten/snon-set 'description' value.
        assert (
            config.model_dump(mode="json", exclude_none=True, exclude=["description"])
            == expected_merged_config
        )

        return original_create_strategy(strategy_type, config)

    monkeypatch.setattr(
        "app.routers.dataresource.create_strategy", create_strategy_middleware
    )

    if method == "initialize":
        response = client.post(
            f"/dataresource/{dataresource_id}/initialize",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=(3.0, 27.0),
        )
    else:  # method == "get"
        response = client.get(
            f"/dataresource/{dataresource_id}",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=(3.0, 27.0),
        )

    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}\nResponse URL: {response.url}"

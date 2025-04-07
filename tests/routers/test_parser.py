"""Test parser"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Literal

    from fastapi.testclient import TestClient


def test_create_parser(client: "TestClient") -> None:
    """Test creating a parser"""
    response = client.post(
        "/parser/",
        json={
            "parserType": "parser/demo",
            "entity": "http://example.com/entity",
            "configuration": {
                "downloadUrl": "https://filesamples.com/sample2.json",
                "mediaType": "application/json",
            },
        },
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert "parser_id" in response.json()
    assert response.status_code == 200


def test_info_parser(client: "TestClient", test_data: dict[str, str]) -> None:
    """Test getting information about a parser"""
    parser_id = next(_ for _ in test_data if _.startswith("parser-"))
    response = client.get(
        f"/parser/{parser_id}/info",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200
    assert "parserType" in response.json()
    assert "configuration" in response.json()


def test_get_parser(client: "TestClient", test_data: dict[str, str]) -> None:
    """Test getting and parsing data using a specified parser"""
    parser_id = next(_ for _ in test_data if _.startswith("parser-"))
    response = client.get(
        f"/parser/{parser_id}",
        headers={"Content-Type": "application/json"},
        timeout=(3.0, 27.0),
    )
    assert response.status_code == 200


def test_initialize_parser(client: "TestClient", test_data: dict[str, str]) -> None:
    """Test initializing a parser."""
    parser_id = next(_ for _ in test_data if _.startswith("parser-"))
    response = client.post(
        f"/parser/{parser_id}/initialize",
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

    from oteapi.models import ParserConfig
    from oteapi.plugins import create_strategy

    original_create_strategy = create_strategy

    parser_id = next(_ for _ in test_data if _.startswith("parser-"))
    session_id = next(_ for _ in test_data if _.startswith("session-"))

    expected_merged_config = json.loads(test_data[parser_id])
    expected_merged_config["configuration"].update(json.loads(test_data[session_id]))

    def create_strategy_middleware(
        strategy_type: 'Literal["parse"]', config: ParserConfig
    ):
        """Create a strategy middleware - do some testing."""
        assert strategy_type == "parse"
        assert isinstance(config, ParserConfig)

        # THIS is where we test the session has been properly merged into the strategy
        # configuration !
        assert (
            config.model_dump(mode="json", exclude_unset=True) == expected_merged_config
        )

        return original_create_strategy(strategy_type, config)

    monkeypatch.setattr(
        "app.routers.parser.create_strategy", create_strategy_middleware
    )

    if method == "initialize":
        response = client.post(
            f"/parser/{parser_id}/initialize",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=(3.0, 27.0),
        )
    else:  # method == "get"
        response = client.get(
            f"/parser/{parser_id}",
            params={"session_id": session_id},
            headers={"Content-Type": "application/json"},
            timeout=(3.0, 27.0),
        )

    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}\nResponse URL: {response.url}"

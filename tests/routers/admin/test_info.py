"""Test /admin/info endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_get_info(
    client: TestClient, strategies_to_register: list[dict[str, str]]
) -> None:
    """Test get_info."""
    import json

    from app import __version__

    response = client.get(
        "/admin/info/",
        headers={"Content-Type": "application/json"},
    )
    assert (
        response.status_code == 200
    ), f"Response:\n{json.dumps(response.json(), indent=2)}"

    loaded_response = response.json()

    assert "version" in loaded_response
    assert "registered_strategies" in loaded_response
    assert "installed_plugin_packages" in loaded_response

    assert loaded_response["version"] == __version__

    test_strategies: dict[str, list[dict[str, str]]] = {}
    for strategy in strategies_to_register:
        strategy_type = strategy["group"].split(".", maxsplit=1)[1]

        if strategy_type not in test_strategies:
            test_strategies[strategy_type] = []

        package, name = strategy["name"].split(".", maxsplit=1)
        import_module, class_name = strategy["value"].split(":", maxsplit=1)

        test_strategies[strategy_type].append(
            {
                "name": name,
                "package": package,
                "import_module": import_module,
                "class_name": class_name,
            }
        )

    for strategy_type, registered_strategies in test_strategies.items():
        test_strategies[strategy_type] = sorted(
            registered_strategies, key=lambda x: x["name"]
        )

    test_strategy_packages = {
        strategy["name"].split(".", maxsplit=1)[0]
        for strategy in strategies_to_register
    }

    # Check all the test strategies (from statci/test_strategies/**) are loaded.
    assert (
        test_strategies == loaded_response["registered_strategies"]
    ), f"Loaded strategies: {loaded_response['registered_strategies']}\n\nExpected strategies: {test_strategies}"

    # Check the expected packages are listed (test strategies).
    assert sorted(test_strategy_packages) == sorted(
        loaded_response["installed_plugin_packages"]
    )

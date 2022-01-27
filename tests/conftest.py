"""Fixtures and configuration for PyTest."""
# pylint: disable=invalid-name,redefined-builtin,unused-argument,comparison-with-callable
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from typing import Dict, List


class DummyCache:
    """Mock cache for RedisCache."""

    obj = {}

    def __init__(self, o=None):
        self.obj = o or {}

    async def set(self, id, data) -> None:
        """Mock `set()` method."""
        if data:
            self.obj[id] = data

    async def get(self, id) -> dict:
        """Mock `get()` method."""
        import json

        return json.dumps(self.obj[id])

    async def keys(self, pattern: str) -> "List[bytes]":
        """Mock `keys()` method."""
        # https://stackoverflow.com/questions/44026515/python-redis-keys-returns-list-of-bytes-objects-instead-of-strings
        return [str.encode(item) for item in self.obj.keys()]

    async def exists(self, key: str) -> bool:
        """Mock `exists()` method."""
        return key in self.obj.keys()


def pytest_configure(config):
    """Method that runs before pytest collects tests so no modules are imported"""
    os.environ["OTEAPI_prefix"] = ""


@pytest.fixture(scope="session")
def top_dir() -> Path:
    """Resolved path to repository directory."""
    return Path(__file__).resolve().parent.parent.resolve()


@pytest.fixture(scope="session")
def test_data() -> "Dict[str, dict]":
    """Test data stored in DummyCache."""
    return {
        # filter
        "filter-961f5314-9e8e-411e-a216-ba0eb8e8bc6e": {
            "filterType": "filter/demo",
            "configuration": {"demo_data": [1, 2]},
        },
        # mapping
        "mapping-a2d6b3d5-9b6b-48a3-8756-ae6d4fd6b81e": {
            "mappingType": "mapping/demo",
            "prefixes": {":": "<http://namespace.example.com/ns#"},
            "triples": [[":a", ":has", ":b"]],
            "configuration": {},
        },
        # sessions
        "1": {"foo": "bar"},
        "2": {"foo": "bar"},
        # transformation
        "transformation-f752c613-fde0-4d43-a7f6-c50f68642daa": {
            "transformationType": "script/demo",
            "name": "script/dummy",
            "configuration": {},
        },
    }


def load_test_strategies() -> None:
    """Load test strategies."""
    from importlib.metadata import EntryPoint

    from oteapi.plugins.entry_points import (
        EntryPointStrategy,
        EntryPointStrategyCollection,
        StrategyType,
    )
    from oteapi.plugins.factories import StrategyFactory

    test_strategies = [
        {
            "name": "tests.file",
            "value": "tests.static.test_strategies.download:FileStrategy",
            "group": "oteapi.download",
        },
        {
            "name": "tests.filter/demo",
            "value": "tests.static.test_strategies.filter:DemoFilter",
            "group": "oteapi.filter",
        },
        {
            "name": "tests.mapping/demo",
            "value": "tests.static.test_strategies.mapping:DemoMappingStrategy",
            "group": "oteapi.mapping",
        },
        {
            "name": "tests.text/json",
            "value": "tests.static.test_strategies.parse:DemoJSONDataParseStrategy",
            "group": "oteapi.parse",
        },
        {
            "name": "tests.demo-access-service",
            "value": "tests.static.test_strategies.resource:DemoResourceStrategy",
            "group": "oteapi.resource",
        },
        {
            "name": "tests.script/demo",
            "value": "tests.static.test_strategies.transformation:DummyTransformationStrategy",
            "group": "oteapi.transformation",
        },
    ]
    generated_entry_points = [EntryPoint(**_) for _ in test_strategies]

    StrategyFactory.strategy_create_func = {
        strategy_type: EntryPointStrategyCollection(
            *(EntryPointStrategy(_) for _ in generated_entry_points)
        )
        for strategy_type in StrategyType
    }


@pytest.fixture(scope="session")
def client(test_data: "Dict[str, dict]") -> TestClient:
    """Return a test client."""
    from fastapi_plugins import depends_redis

    from asgi import app

    async def override_depends_redis() -> DummyCache:
        """Helper method for overriding RedisCache.

        Add sample data.
        """
        return DummyCache(test_data)

    app.dependency_overrides[depends_redis] = override_depends_redis

    load_test_strategies()

    return TestClient(app)

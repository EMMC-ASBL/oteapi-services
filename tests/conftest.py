"""Fixtures and configuration for PyTest."""
import json
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

import pytest

if TYPE_CHECKING:
    from typing import Dict, List


class DummyCache:
    """Mock cache for RedisCache."""

    obj = {}

    def __init__(self, o={}):
        self.obj = o

    async def set(self, id, data) -> None:
        """Mock `set()` method."""
        if data:
            self.obj[id] = data

    async def get(self, id) -> dict:
        """Mock `get()` method."""
        return json.dumps(self.obj[id])

    async def keys(self, pattern: str) -> "List[str]":
        """Mock `keys()` method."""
        return self.obj.keys()


def pytest_configure(config):
    """Method that runs before pytest collects tests so no modules are imported"""
    import os

    os.environ["OTEAPI_prefix"] = ""


@pytest.fixture(scope="session")
def test_data() -> "Dict[str, dict]":
    return {
        # filter
        "filter-961f5314-9e8e-411e-a216-ba0eb8e8bc6e": {
            "filterType": "filter/demo",
            "configuration": {"demoData": [1, 2]},
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
            "transformation_type": "script/demo",
            "name": "script/dummy",
            "configuration": {},
        }
    }


@pytest.fixture(scope="session")
def client(test_data: "Dict[str, dict]") -> TestClient:
    """Return a test client."""
    from pathlib import Path

    from fastapi_plugins import depends_redis
    from oteapi.plugins.plugins import import_module, load_plugins

    from asgi import app

    async def override_depends_redis() -> DummyCache:
        """Helper method for overriding RedisCache.

        Add sample data.
        """
        return DummyCache(test_data)

    app.dependency_overrides[depends_redis] = override_depends_redis
    for index, func in enumerate(tuple(app.router.on_startup)):
        if func == load_plugins:
            app.router.on_startup.pop(index)

    TOP_DIR = Path(__file__).resolve().parent.parent.resolve()
    for strategy_file in (TOP_DIR / "tests" / "static" / "test_strategies").glob("*.py"):
        import_module(str(strategy_file.resolve().with_suffix("").relative_to(TOP_DIR)).replace("/", "."))

    return TestClient(app)

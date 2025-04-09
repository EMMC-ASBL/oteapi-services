"""Fixtures and configuration for PyTest."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from fastapi import FastAPI
    from fastapi.testclient import TestClient


## Pytest configuration functions and hooks ##


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the command line option to run the tests, expecting a live Redis instance."""
    parser.addoption(
        "--live-redis",
        action="store_true",
        default=False,
        help=(
            "Run the tests with a live Redis server instance. WARNING: This will wipe "
            "out existing data."
        ),
    )


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """Method that runs before pytest collects tests so no modules are imported"""
    import os

    os.environ["OTEAPI_PREFIX"] = ""
    os.environ["OTEAPI_INCLUDE_REDISADMIN"] = "True"
    os.environ["OTEAPI_EXPOSE_SECRETS"] = "True"


## Pytest fixtures ##


@pytest.fixture(scope="session")
def live_redis(request: pytest.FixtureRequest) -> bool:
    """Return whether to run the tests, expecting a live Redis instance."""
    return request.config.getoption("--live-redis")


@pytest.fixture(scope="session")
def top_dir() -> Path:
    """Resolved path to repository directory."""
    from pathlib import Path

    return Path(__file__).resolve().parent.parent.resolve()


@pytest.fixture
def test_data() -> dict[str, str]:
    """Test data stored in DummyCache."""
    import json

    return {
        key: json.dumps(value)
        for key, value in {
            # filter
            "filter-961f5314-9e8e-411e-a216-ba0eb8e8bc6e": {
                "filterType": "filter/demo",
                "configuration": {"demo_data": [1, 2]},
            },
            # function
            "function-a647012a-7ab9-4f2c-9c13-2564aa6d95a1": {
                "functionType": "function/demo",
                "configuration": {},
            },
            # dataresource
            "dataresource-910c9965-a318-4ac4-9123-9c55d5b86f2e": {
                "downloadUrl": "https://filesamples.com/sample.json",
                "mediaType": "application/json",
                "resourceType": "resource/demo",
            },
            # mapping
            "mapping-a2d6b3d5-9b6b-48a3-8756-ae6d4fd6b81e": {
                "mappingType": "mapping/demo",
                "prefixes": {":": "<http://namespace.example.com/ns#"},
                "triples": [[":a", ":has", ":b"]],
                "configuration": {},
            },
            # sessions
            "session-f752c613-fde0-4d43-a7f6-c50f68642daa": {"foo": "bar"},
            "session-a2d6b3d5-9b6b-48a3-8756-ae6d4fd6b81e": {"foo": ["bar", "baz"]},
            # transformation
            "transformation-f752c613-fde0-4d43-a7f6-c50f68642daa": {
                "transformationType": "script/demo",
                "name": "script/dummy",
                "configuration": {},
            },
            # parser
            "parser-f752c613-fde0-4d43-a7f6-c50f68642daa": {
                "parserType": "parser/demo",
                "entity": "http://example.com/entity",
                "configuration": {
                    "downloadUrl": ("https://example.org/sample2.json"),
                    "mediaType": "application/json",
                },
            },
        }.items()
    }


@pytest.fixture(scope="session")
def strategies_to_register() -> list[dict[str, str]]:
    """Test strategies to register as entry points."""
    return [
        {
            "name": "tests.https",
            "value": "tests.static.test_strategies.download:HTTPSStrategy",
            "group": "oteapi.download",
        },
        {
            "name": "tests.filter/demo",
            "value": "tests.static.test_strategies.filter:DemoFilter",
            "group": "oteapi.filter",
        },
        {
            "name": "tests.function/demo",
            "value": "tests.static.test_strategies.function:DemoFunctionStrategy",
            "group": "oteapi.function",
        },
        {
            "name": "tests.mapping/demo",
            "value": "tests.static.test_strategies.mapping:DemoMappingStrategy",
            "group": "oteapi.mapping",
        },
        {
            "name": "tests.parser/demo",
            "value": "tests.static.test_strategies.parse:DemoJSONDataParseStrategy",
            "group": "oteapi.parse",
        },
        {
            "name": "tests.resource/demo",
            "value": "tests.static.test_strategies.resource:DemoResourceStrategy",
            "group": "oteapi.resource",
        },
        {
            "name": "tests.script/demo",
            "value": "tests.static.test_strategies.transformation:DummyTransformationStrategy",
            "group": "oteapi.transformation",
        },
    ]


@pytest.fixture
def load_test_strategies(
    strategies_to_register: list[dict[str, str]],
) -> Callable[[], None]:
    """Wrapper function for returning function to load test strategies."""
    from importlib.metadata import EntryPoint

    from oteapi.plugins.entry_points import (
        EntryPointStrategy,
        EntryPointStrategyCollection,
        StrategyType,
    )
    from oteapi.plugins.factories import StrategyFactory

    def _load_test_strategies() -> None:
        """Load test strategies."""
        generated_entry_points = [EntryPoint(**_) for _ in strategies_to_register]

        StrategyFactory.strategy_create_func = {
            strategy_type: EntryPointStrategyCollection(
                *(
                    EntryPointStrategy(_)
                    for _ in generated_entry_points
                    if _.group.split(".", maxsplit=1)[1] == strategy_type.value
                )
            )
            for strategy_type in StrategyType
        }

    return _load_test_strategies


@pytest.fixture
def client(
    test_data: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    live_redis: bool,
    load_test_strategies: Callable[[], None],
) -> TestClient:
    """Return a test client."""
    from contextlib import asynccontextmanager
    from warnings import catch_warnings, simplefilter

    from fastapi.testclient import TestClient

    from app.logging import setup_logging
    from app.main import create_app
    from app.settings import get_settings

    @asynccontextmanager
    async def lifespan_with_test_data(app: FastAPI):
        """Initialize Redis upon app startup."""
        from app import main

        # Initialize the Redis cache
        await main.redis_plugin.init_app(app, config=get_settings())

        # Test a warning of falling back to fakeredis is emitted (if Redis is not
        # available)
        original_redis_type = main.redis_plugin.config.redis_type

        with catch_warnings(record=True) as warns:
            simplefilter("always")

            await main.redis_plugin.init()

            if (
                original_redis_type != "fakeredis"
                and main.redis_plugin.config.redis_type == "fakeredis"
            ):
                assert warns
                user_warnings = [
                    user_warn
                    for user_warn in warns
                    if issubclass(user_warn.category, UserWarning)
                ]
                assert len(user_warnings) == 1
                assert (
                    "No live Redis server found - falling back to fakeredis !"
                    in str(user_warnings[0].message)
                )

        if live_redis:
            help_message = (
                "Expected a live Redis to be used in testing, however, the server has "
                "fallen back to using 'fakeredis', since it could not connect to a "
                "live Redis. Please make sure your Redis server is running at the "
                "intended address and that you have set all relevant environment "
                "variables/configurations."
            )
            assert original_redis_type != "fakeredis", help_message
            assert (
                original_redis_type == main.redis_plugin.config.redis_type
            ), help_message
        else:
            assert main.redis_plugin.config.redis_type == "fakeredis", (
                "A live Redis has been found on the system and used for testing. If "
                "this was the intention, please add the '--live-redis' option to your "
                "'pytest' call. If this was not the intention, please set the "
                "appropriate environment variables to direct the tests to use "
                "'fakeredis'."
            )

        # Get redis client
        redis_client = await main.redis_plugin()

        # Clear db and load test data
        await redis_client.flushdb(asynchronous=True)
        await redis_client.mset(test_data)

        # Load OTEAPI strategies
        load_test_strategies()

        # Run server
        yield

        # Terminate the Redis cache
        await main.redis_plugin.terminate()

    monkeypatch.setattr("app.main.lifespan", lifespan_with_test_data)

    # Setup logging
    setup_logging()

    # Yield client from within a context to ensure the lifespan is used
    with TestClient(create_app()) as client:
        yield client

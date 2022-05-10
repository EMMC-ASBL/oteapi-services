"""Administrative endpoint."""
import platform
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from oteapi.plugins.entry_points import (
    EntryPointStrategyCollection,
    StrategyType,
    get_strategy_entry_points,
)

from app import __version__

ROUTER = APIRouter(prefix="/admin", include_in_schema=False)


@ROUTER.get("/info", include_in_schema=False)
async def get_info(request: Request) -> JSONResponse:
    """Write out introspective information about the service."""
    top_dir = Path(__file__).resolve().parent.parent.parent.resolve()

    py_dependencies = dict(
        line.split("==", maxsplit=1)
        for line in (top_dir / "requirements.txt")
        .read_text(encoding="utf8")
        .splitlines()
    )

    oteapi_strategies = EntryPointStrategyCollection()
    for strategy_type in StrategyType:
        oteapi_strategies.add(*get_strategy_entry_points(strategy_type=strategy_type))
    strategies_dict: "dict[str, list[str]]" = {}.fromkeys(
        (_.value for _ in StrategyType), []
    )
    for oteapi_strategy in oteapi_strategies:
        strategies_dict[oteapi_strategy.type.value].append(
            f"{oteapi_strategy.name} = {oteapi_strategy.module}:"
            f"{oteapi_strategy.implementation_name}"
        )

    JSONResponse(
        content={
            "version": {
                "API": __version__.split(".", maxsplit=1)[0],
                "OTEAPI Services": __version__,
                "OTEAPI Core": py_dependencies["oteapi-core"],
            },
            "environment": {
                "architecture": platform.architecture() + (platform.machine(),),
                "node": platform.node(),
                "platform": platform.platform(),
                "python": {
                    "compiler": platform.python_compiler(),
                    "dependencies": py_dependencies,
                    "version": platform.python_version(),
                    "build": platform.python_build(),
                    "implementation": platform.python_implementation(),
                },
            },
            "oteapi": {
                "registered_strategies": strategies_dict,
                "plugins": {
                    strategy.package: py_dependencies[strategy.package]
                    for strategy in oteapi_strategies
                },
            },
            "routes": [
                {"path": route.path, "name": route.name} for route in request.app.routes
            ],
        }
    )

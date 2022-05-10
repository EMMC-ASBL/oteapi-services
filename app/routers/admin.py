"""Administrative endpoint."""
import asyncio
import platform
from collections import defaultdict
from importlib.metadata import distributions

# from pathlib import Path
from urllib.parse import urlparse

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
async def get_info(request: Request) -> JSONResponse:  # pylint: disable=too-many-locals
    """Write out introspective information about the service."""
    # top_dir = Path(__file__).resolve().parent.parent.parent.resolve()

    process = await asyncio.create_subprocess_shell(
        "pip freeze", stdout=asyncio.subprocess.PIPE
    )
    pip_freeze, _ = await process.communicate()

    py_dependencies = {}
    for line in pip_freeze.decode().splitlines():
        if "==" in line:
            split_line = line.split("==", maxsplit=1)
            py_dependencies[split_line[0]] = split_line[1]
        elif "://" in line:
            for line_part in line.split():
                url = urlparse(line_part)
                if url.scheme:
                    break
            else:
                raise ValueError(f"Could not parse any part of line as URL: {line}")
            if "egg" in url.fragment and "@" in url.path:
                py_dependencies[
                    url.fragment.split("egg=", maxsplit=1)[-1]
                ] = url.path.split("@", maxsplit=1)[-1]

    package_to_dist: dict[str, list[str]] = defaultdict(list)
    for distribution in distributions():
        if distribution.files and "top_level.txt" in [
            _.name for _ in distribution.files
        ]:
            for package in distribution.read_text("top_level.txt").splitlines():  # type: ignore
                package_to_dist[package].append(distribution.metadata["Name"])

    oteapi_strategies = EntryPointStrategyCollection()
    for strategy_type in StrategyType:
        oteapi_strategies.add(*get_strategy_entry_points(strategy_type=strategy_type))
    strategies_dict: "dict[str, list[dict[str, str]]]" = defaultdict(list)
    for oteapi_strategy in oteapi_strategies:
        strategies_dict[oteapi_strategy.type.value].append(
            {
                "name": oteapi_strategy.name,
                "module": oteapi_strategy.module,
                "cls": oteapi_strategy.implementation_name,
            }
        )

    return JSONResponse(
        content={
            "version": {
                "API": __version__.split(".", maxsplit=1)[0],
                "OTEAPI Services": __version__,
                "OTEAPI Core": py_dependencies.get(
                    "oteapi-core", py_dependencies.get("oteapi_core", "Unknown")
                ),
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
                    package_to_dist[strategy.package][0]: py_dependencies.get(
                        package_to_dist[strategy.package][0],
                        py_dependencies.get(
                            package_to_dist[strategy.package][0].replace("-", "_"),
                            "Unknown",
                        ),
                    )
                    for strategy in oteapi_strategies
                },
            },
            "routes": [route.path for route in request.app.routes],
        }
    )

"""Administrative endpoint."""

import asyncio
import platform
from collections import defaultdict
from importlib.metadata import distributions

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
    process_pip_freeze = await asyncio.create_subprocess_shell(
        "pip freeze --all", stdout=asyncio.subprocess.PIPE
    )
    process_pip_list = await asyncio.create_subprocess_shell(
        "pip list --format=freeze", stdout=asyncio.subprocess.PIPE
    )
    pip_freeze_out, _ = await process_pip_freeze.communicate()
    pip_list_out, _ = await process_pip_list.communicate()

    pip_freeze = pip_freeze_out.decode().splitlines()
    pip_list = [
        line for line in pip_list_out.decode().splitlines() if line not in pip_freeze
    ]

    py_dependencies: dict[str, dict[str, str]] = {
        "std": {},
        "editable": {},
        "external": {},
    }
    for line in pip_freeze:
        if "==" in line:
            split_line = line.split("==", maxsplit=1)
            py_dependencies["std"][split_line[0]] = split_line[1]
        else:
            py_dependencies["external"][line] = ""
    for line in pip_list:
        split_line = line.split("==", maxsplit=1)
        py_dependencies["editable"][split_line[0]] = split_line[1]

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
                "OTEAPI Core": py_dependencies["std"].get(
                    "oteapi-core",
                    py_dependencies["editable"].get(
                        "oteapi-core", _get_local_oteapi_version()
                    ),
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
                    package_to_dist[strategy.package][0]: py_dependencies["std"].get(
                        package_to_dist[strategy.package][0],
                        py_dependencies["editable"].get(
                            package_to_dist[strategy.package][0],
                            "Unknown",
                        ),
                    )
                    for strategy in oteapi_strategies
                },
            },
            "routes": [route.path for route in request.app.routes],
        }
    )


def _get_local_oteapi_version() -> str:
    """Import `oteapi` and return `__version__`."""
    # pylint: disable=import-outside-toplevel
    from oteapi import __version__ as __oteapi_version__

    return __oteapi_version__

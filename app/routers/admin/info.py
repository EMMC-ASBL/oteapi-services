"""System information routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from oteapi.plugins.factories import StrategyFactory

from app import __version__

ROUTER = APIRouter(prefix="/info")


@ROUTER.get("/")
async def get_info() -> dict[str, Any]:
    """Get system information."""
    loaded_strategies: dict[str, list[dict[str, str]]] = {
        strategy_type.value: [
            {
                "name": strategy.name,
                "package": strategy.package,
                "import_module": strategy.module,
                "class_name": strategy.implementation_name,
            }
            for strategy in strategy_collection
        ]
        for strategy_type, strategy_collection in StrategyFactory.strategy_create_func.items()
    }

    installed_plugin_packages: set[str] = {
        strategy.package
        for strategy_collection in StrategyFactory.strategy_create_func.values()
        for strategy in strategy_collection
    }

    return {
        "version": __version__,
        "registered_strategies": loaded_strategies,
        "installed_plugin_packages": installed_plugin_packages,
    }

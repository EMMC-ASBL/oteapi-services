"""Function."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, status
from oteapi.models import FunctionConfig
from oteapi.plugins import create_strategy
from oteapi.utils.config_updater import populate_config_from_session

from app.models.error import HTTPNotFoundError
from app.models.function import (
    IDPREFIX,
    CreateFunctionResponse,
    GetFunctionResponse,
    InitializeFunctionResponse,
)
from app.redis_cache import TRedisPlugin
from app.redis_cache._cache import _fetch_cache_value, _validate_cache_key
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from oteapi.interfaces import IFunctionStrategy

ROUTER = APIRouter(
    prefix=f"/{IDPREFIX}",
    tags=["function"],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)


@ROUTER.post("/", response_model=CreateFunctionResponse)
async def create_function(
    cache: TRedisPlugin,
    config: FunctionConfig,
    request: Request,
    session_id: str | None = None,
) -> CreateFunctionResponse:
    """Create a new function configuration."""
    new_function = CreateFunctionResponse()

    if request.headers.get("Authorization") or config.token:
        config.token = request.headers.get("Authorization") or config.token

    function_config = config.model_dump_json(exclude_unset=True)

    await cache.set(new_function.function_id, function_config)

    if session_id:
        await _validate_cache_key(cache, session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="function_info",
            list_items=[new_function.function_id],
            redis=cache,
        )

    return new_function


@ROUTER.get("/{function_id}", response_model=GetFunctionResponse)
async def get_function(
    cache: TRedisPlugin,
    function_id: str,
    session_id: str | None = None,
) -> GetFunctionResponse:
    """Get (execute) function."""
    cache_value = await _fetch_cache_value(cache, function_id, "function_id")
    config = FunctionConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    function_strategy: IFunctionStrategy = create_strategy("function", config)
    session_update = function_strategy.get()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetFunctionResponse(**session_update)


@ROUTER.post("/{function_id}/initialize", response_model=InitializeFunctionResponse)
async def initialize_function(
    cache: TRedisPlugin,
    function_id: str,
    session_id: str | None = None,
) -> InitializeFunctionResponse:
    """Initialize and update function."""
    cache_value = await _fetch_cache_value(cache, function_id, "function_id")
    config = FunctionConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    function_strategy: IFunctionStrategy = create_strategy("function", config)
    session_update = function_strategy.initialize()

    if session_update and session_id:
        await _update_session(
            session_id=session_id,
            updated_session=session_update,
            redis=cache,
        )

    return InitializeFunctionResponse(**session_update)

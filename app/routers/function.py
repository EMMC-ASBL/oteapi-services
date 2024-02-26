"""Function."""

import json
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, Request, status
from oteapi.models import FunctionConfig
from oteapi.plugins import create_strategy

from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.models.function import (
    IDPREFIX,
    CreateFunctionResponse,
    GetFunctionResponse,
    InitializeFunctionResponse,
)
from app.redis_cache import TRedisPlugin
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

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
    session_id: Optional[str] = None,
) -> CreateFunctionResponse:
    """Create a new function configuration."""
    new_function = CreateFunctionResponse()

    config.token = request.headers.get("Authorization") or config.token

    function_config = config.model_dump_json()

    await cache.set(new_function.function_id, function_config)

    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
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
    session_id: Optional[str] = None,
) -> GetFunctionResponse:
    """Get (execute) function."""
    if not await cache.exists(function_id):
        raise httpexception_404_item_id_does_not_exist(function_id, "function_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(function_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {function_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = FunctionConfig(**json.loads(cache_value))

    function_strategy = create_strategy("function", config)

    if session_id:
        cache_value = await cache.get(session_id)
        if not isinstance(cache_value, (str, bytes)):
            raise TypeError(
                f"Expected cache value of {session_id} to be a string or bytes, "
                f"found it to be of type {type(cache_value)!r}."
            )
    session_data: "Optional[dict[str, Any]]" = (
        None if not session_id else json.loads(cache_value)
    )
    session_update = function_strategy.get(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetFunctionResponse(**session_update)


@ROUTER.post("/{function_id}/initialize", response_model=InitializeFunctionResponse)
async def initialize_function(
    cache: TRedisPlugin,
    function_id: str,
    session_id: Optional[str] = None,
) -> InitializeFunctionResponse:
    """Initialize and update function."""
    if not await cache.exists(function_id):
        raise httpexception_404_item_id_does_not_exist(function_id, "function_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(function_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {function_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = FunctionConfig(**json.loads(cache_value))

    function_strategy = create_strategy("function", config)

    if session_id:
        cache_value = await cache.get(session_id)
        if not isinstance(cache_value, (str, bytes)):
            raise TypeError(
                f"Expected cache value of {session_id} to be a string or bytes, "
                f"found it to be of type {type(cache_value)!r}."
            )
    session_data: "Optional[dict[str, Any]]" = (
        None if not session_id else json.loads(cache_value)
    )
    session_update = function_strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id,
            updated_session=session_update,
            redis=cache,
        )

    return InitializeFunctionResponse(**session_update)

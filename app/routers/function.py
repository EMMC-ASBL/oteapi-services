"""Function."""
import json
from typing import TYPE_CHECKING, Optional

from aioredis import Redis
from fastapi import APIRouter, Depends, Request, status
from fastapi_plugins import depends_redis
from oteapi.models import FunctionConfig
from oteapi.plugins import create_strategy

from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.models.function import (
    IDPREFIX,
    CreateFunctionResponse,
    GetFunctionResponse,
    InitializeFunctionResponse,
)
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict

ROUTER = APIRouter(prefix=f"/{IDPREFIX}")


@ROUTER.post(
    "/",
    response_model=CreateFunctionResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def create_function(
    config: FunctionConfig,
    request: Request,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> CreateFunctionResponse:
    """Create a new function configuration."""
    new_function = CreateFunctionResponse()

    function_config = config.dict()

    function_config["secret"] = request.headers.get(
        "Authorization"
    ) or function_config.get("secret")

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


@ROUTER.get(
    "/{function_id}",
    response_model=GetFunctionResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_function(
    function_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> GetFunctionResponse:
    """Get (execute) function."""
    if not await cache.exists(function_id):
        raise httpexception_404_item_id_does_not_exist(function_id, "function_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    config = FunctionConfig(**json.loads(await cache.get(function_id)))

    function_strategy = create_strategy("function", config)
    session_data: "Optional[Dict[str, Any]]" = (
        None if not session_id else json.loads(await cache.get(session_id))
    )
    session_update = function_strategy.get(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetFunctionResponse(**session_update)


@ROUTER.post(
    "/{function_id}/initialize",
    response_model=InitializeFunctionResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_function(
    function_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> InitializeFunctionResponse:
    """Initialize and update function."""
    if not await cache.exists(function_id):
        raise httpexception_404_item_id_does_not_exist(function_id, "function_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    config = FunctionConfig(**json.loads(await cache.get(function_id)))

    function_strategy = create_strategy("function", config)
    session_data: "Optional[Dict[str, Any]]" = (
        None if not session_id else json.loads(await cache.get(session_id))
    )
    session_update = function_strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id,
            updated_session=session_update,
            redis=cache,
        )

    return InitializeFunctionResponse(**session_update)

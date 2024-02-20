"""Data Filter."""

import json
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, status
from oteapi.models import FilterConfig
from oteapi.plugins import create_strategy

from app.models.datafilter import (
    IDPREFIX,
    CreateFilterResponse,
    GetFilterResponse,
    InitializeFilterResponse,
)
from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.redis_cache import TRedisPlugin
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from oteapi.interfaces import IFilterStrategy

ROUTER = APIRouter(prefix=f"/{IDPREFIX}")


@ROUTER.post(
    "/",
    response_model=CreateFilterResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
    tags=["datafilter"],
)
async def create_filter(
    cache: TRedisPlugin,
    config: FilterConfig,
    session_id: Optional[str] = None,
) -> CreateFilterResponse:
    """Define a new filter configuration (data operation)"""
    new_filter = CreateFilterResponse()

    await cache.set(new_filter.filter_id, config.model_dump_json())

    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="filter_info",
            list_items=[new_filter.filter_id],
            redis=cache,
        )

    return new_filter


@ROUTER.get(
    "/{filter_id}",
    response_model=GetFilterResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
    tags=["datafilter"],
)
async def get_filter(
    cache: TRedisPlugin,
    filter_id: str,
    session_id: Optional[str] = None,
) -> GetFilterResponse:
    """Run and return data from a filter (data operation)"""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(filter_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {filter_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = FilterConfig(**json.loads(cache_value))

    strategy: "IFilterStrategy" = create_strategy("filter", config)

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
    session_update = strategy.get(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetFilterResponse(**session_update)


@ROUTER.post(
    "/{filter_id}/initialize",
    response_model=InitializeFilterResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
    tags=["datafilter"],
)
async def initialize_filter(
    cache: TRedisPlugin,
    filter_id: str,
    session_id: Optional[str] = None,
) -> InitializeFilterResponse:
    """Initialize and return data to update session."""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(filter_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {filter_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = FilterConfig(**json.loads(cache_value))

    strategy: "IFilterStrategy" = create_strategy("filter", config)

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
    session_update = strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeFilterResponse(**session_update)

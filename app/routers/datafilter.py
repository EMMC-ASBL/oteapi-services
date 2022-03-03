"""Data Filter."""
import json
from typing import Optional

from aioredis import Redis
from fastapi import APIRouter, Depends, status
from fastapi_plugins import depends_redis
from oteapi.models import FilterConfig
from oteapi.plugins import create_strategy

from app.models.datafilter import (
    IDPREFIX,
    CreateFilterResponse,
    GetFilterResponse,
    InitializeFilterResponse,
)
from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.routers.session import _update_session, _update_session_list_item

ROUTER = APIRouter(prefix=f"/{IDPREFIX}")


@ROUTER.post(
    "/",
    response_model=CreateFilterResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def create_filter(
    config: FilterConfig,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> CreateFilterResponse:
    """Define a new filter configuration (data operation)"""
    new_filter = CreateFilterResponse()

    await cache.set(new_filter.filter_id, config.json())

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
)
async def get_filter(
    filter_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> GetFilterResponse:
    """Run and return data from a filter (data operation)"""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    config = FilterConfig(**json.loads(await cache.get(filter_id)))

    strategy = create_strategy("filter", config)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
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
)
async def initialize_filter(
    filter_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> InitializeFilterResponse:
    """Initialize and return data to update session."""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    config = FilterConfig(**json.loads(await cache.get(filter_id)))

    strategy = create_strategy("filter", config)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    session_update = strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeFilterResponse(**session_update)

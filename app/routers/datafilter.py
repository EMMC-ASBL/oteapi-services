"""Data Filter."""

import json
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, status
from oteapi.models import FilterConfig
from oteapi.plugins import create_strategy
from oteapi.utils.config_updater import populate_config_from_session

from app.models.datafilter import (
    IDPREFIX,
    CreateFilterResponse,
    GetFilterResponse,
    InitializeFilterResponse,
)
from app.models.error import HTTPNotFoundError
from app.redis_cache import TRedisPlugin
from app.redis_cache._cache import _fetch_cache_value, _validate_cache_key
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from oteapi.interfaces import IFilterStrategy

ROUTER = APIRouter(
    prefix=f"/{IDPREFIX}",
    tags=["datafilter"],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)


@ROUTER.post("/", response_model=CreateFilterResponse)
async def create_filter(
    cache: TRedisPlugin,
    config: FilterConfig,
    session_id: Optional[str] = None,
) -> CreateFilterResponse:
    """Define a new filter configuration (data operation)"""
    new_filter = CreateFilterResponse()

    await cache.set(new_filter.filter_id, config.model_dump_json())

    if session_id:
        await _validate_cache_key(cache, session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="filter_info",
            list_items=[new_filter.filter_id],
            redis=cache,
        )

    return new_filter


@ROUTER.get("/{filter_id}", response_model=GetFilterResponse)
async def get_filter(
    cache: TRedisPlugin,
    filter_id: str,
    session_id: Optional[str] = None,
) -> GetFilterResponse:
    """Run and return data from a filter (data operation)"""
    cache_value = await _fetch_cache_value(cache, filter_id, "filter_id")
    config = FilterConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    strategy: "IFilterStrategy" = create_strategy("filter", config)
    session_update = strategy.get()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetFilterResponse(**session_update)


@ROUTER.post("/{filter_id}/initialize", response_model=InitializeFilterResponse)
async def initialize_filter(
    cache: TRedisPlugin,
    filter_id: str,
    session_id: Optional[str] = None,
) -> InitializeFilterResponse:
    """Initialize and return data to update session."""
    cache_value = await _fetch_cache_value(cache, filter_id, "filter_id")
    config = FilterConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    strategy: "IFilterStrategy" = create_strategy("filter", config)
    session_update = strategy.initialize()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeFilterResponse(**session_update)

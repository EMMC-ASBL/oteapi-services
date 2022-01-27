"""Data Filter."""
import json
from typing import Any, Dict, Optional
from uuid import uuid4

from aioredis import Redis
from fastapi import APIRouter, Depends
from fastapi_plugins import depends_redis
from oteapi.models import FilterConfig
from oteapi.plugins import create_strategy
from starlette.status import HTTP_404_NOT_FOUND

from app.models.response import (
    HTTPNotFoundError,
    Status,
    httpexception_404_item_id_does_not_exist,
)

from .session import _update_session, _update_session_list_item

router = APIRouter(prefix="/filter")

IDPREDIX = "filter-"


@router.post(
    "/",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def create_filter(
    config: FilterConfig,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, Any]:
    """Define a new filter configuration (data operation)"""

    filter_id = IDPREDIX + str(uuid4())

    await cache.set(filter_id, config.json())
    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(session_id, "filter_info", [filter_id], cache)
    return dict(filter_id=filter_id)


@router.get(
    "/{filter_id}",
    response_model=Status,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_filter(
    filter_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, Any]:
    """Run and return data from a filter (data operation)"""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    filter_info_json = json.loads(await cache.get(filter_id))
    filter_info = FilterConfig(**filter_info_json)
    filter_strategy = create_strategy("filter", filter_info)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    result = filter_strategy.get(session_data)
    if result and session_id:
        await _update_session(session_id, result, cache)

    return result


@router.post(
    "/{filter_id}/initialize",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_filter(
    filter_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, Any]:
    """Initialize and return data to update session"""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    filter_info_json = json.loads(await cache.get(filter_id))
    filter_info = FilterConfig(**filter_info_json)
    filter_strategy = create_strategy("filter", filter_info)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    result = filter_strategy.initialize(session_data)
    if result and session_id:
        await _update_session(session_id, result, cache)

    return result

"""Transformation."""

import json
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, Request, status
from oteapi.models import TransformationConfig, TransformationStatus
from oteapi.plugins import create_strategy
from oteapi.utils.config_updater import populate_config_from_session

from app.models.error import HTTPNotFoundError
from app.models.transformation import (
    IDPREFIX,
    CreateTransformationResponse,
    ExecuteTransformationResponse,
    GetTransformationResponse,
    InitializeTransformationResponse,
)
from app.redis_cache import TRedisPlugin
from app.redis_cache._cache import _fetch_cache_value, _validate_cache_key
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from oteapi.interfaces import ITransformationStrategy

ROUTER = APIRouter(
    prefix=f"/{IDPREFIX}",
    tags=["transformation"],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)


@ROUTER.post("/", response_model=CreateTransformationResponse)
async def create_transformation(
    cache: TRedisPlugin,
    config: TransformationConfig,
    request: Request,
    session_id: Optional[str] = None,
) -> CreateTransformationResponse:
    """Create a new transformation configuration."""
    new_transformation = CreateTransformationResponse()

    if request.headers.get("Authorization") or config.token:
        config.token = request.headers.get("Authorization") or config.token

    transformation_config = config.model_dump_json(exclude_unset=True)

    await cache.set(new_transformation.transformation_id, transformation_config)

    if session_id:
        await _validate_cache_key(cache, session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="transformation_info",
            list_items=[new_transformation.transformation_id],
            redis=cache,
        )

    return new_transformation


@ROUTER.get("/{transformation_id}/status", response_model=TransformationStatus)
async def get_transformation_status(
    cache: TRedisPlugin,
    transformation_id: str,
    task_id: str,
) -> TransformationStatus:
    """Get the current status of a defined transformation."""
    cache_value = await _fetch_cache_value(
        cache, transformation_id, "transformation_id"
    )
    config = TransformationConfig(**json.loads(cache_value))

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    return strategy.status(task_id=task_id)


@ROUTER.get("/{transformation_id}", response_model=GetTransformationResponse)
async def get_transformation(
    cache: TRedisPlugin,
    transformation_id: str,
    session_id: Optional[str] = None,
) -> GetTransformationResponse:
    """Get transformation."""
    cache_value = await _fetch_cache_value(
        cache, transformation_id, "transformation_id"
    )
    config = TransformationConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    session_update = strategy.get()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetTransformationResponse(**session_update)


@ROUTER.post(
    "/{transformation_id}/execute", response_model=ExecuteTransformationResponse
)
async def execute_transformation(
    cache: TRedisPlugin,
    transformation_id: str,
    session_id: Optional[str] = None,
) -> ExecuteTransformationResponse:
    """Execute (run) a transformation."""
    # Fetch transformation info from cache
    cache_value = await _fetch_cache_value(
        cache, transformation_id, "transformation_id"
    )
    config = TransformationConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    session_update = strategy.get()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return ExecuteTransformationResponse(**session_update)


@ROUTER.post(
    "/{transformation_id}/initialize", response_model=InitializeTransformationResponse
)
async def initialize_transformation(
    cache: TRedisPlugin,
    transformation_id: str,
    session_id: Optional[str] = None,
) -> InitializeTransformationResponse:
    """Initialize a transformation."""
    # Fetch transformation info from cache
    cache_value = await _fetch_cache_value(
        cache, transformation_id, "transformation_id"
    )
    config = TransformationConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    session_update = strategy.initialize()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeTransformationResponse(**session_update)

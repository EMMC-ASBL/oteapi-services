"""Transformation."""
import json
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, Request, status
from oteapi.models import TransformationConfig, TransformationStatus
from oteapi.plugins import create_strategy

from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.models.transformation import (
    IDPREFIX,
    CreateTransformationResponse,
    ExecuteTransformationResponse,
    GetTransformationResponse,
    InitializeTransformationResponse,
)
from app.redis_cache import TRedisPlugin
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from oteapi.interfaces import ITransformationStrategy

ROUTER = APIRouter(prefix=f"/{IDPREFIX}")


@ROUTER.post(
    "/",
    response_model=CreateTransformationResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def create_transformation(
    cache: TRedisPlugin,
    config: TransformationConfig,
    request: Request,
    session_id: Optional[str] = None,
) -> CreateTransformationResponse:
    """Create a new transformation configuration."""
    new_transformation = CreateTransformationResponse()

    config.token = request.headers.get("Authorization") or config.token

    transformation_config = config.model_dump_json()

    await cache.set(new_transformation.transformation_id, transformation_config)

    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="transformation_info",
            list_items=[new_transformation.transformation_id],
            redis=cache,
        )

    return new_transformation


@ROUTER.get(
    "/{transformation_id}/status",
    response_model=TransformationStatus,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_transformation_status(
    cache: TRedisPlugin,
    transformation_id: str,
    task_id: str,
) -> TransformationStatus:
    """Get the current status of a defined transformation."""
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )

    config = TransformationConfig(**json.loads(await cache.get(transformation_id)))

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    return strategy.status(task_id=task_id)


@ROUTER.get(
    "/{transformation_id}",
    response_model=GetTransformationResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_transformation(
    cache: TRedisPlugin,
    transformation_id: str,
    session_id: Optional[str] = None,
) -> GetTransformationResponse:
    """Get transformation."""
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    config = TransformationConfig(**json.loads(await cache.get(transformation_id)))

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    session_data: "Optional[dict[str, Any]]" = (
        None if not session_id else json.loads(await cache.get(session_id))
    )
    session_update = strategy.get(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetTransformationResponse(**session_update)


@ROUTER.post(
    "/{transformation_id}/execute",
    response_model=ExecuteTransformationResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def execute_transformation(
    cache: TRedisPlugin,
    transformation_id: str,
    session_id: Optional[str] = None,
) -> ExecuteTransformationResponse:
    """Execute (run) a transformation."""
    # Fetch transformation info from cache
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    config = TransformationConfig(**json.loads(await cache.get(transformation_id)))

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    session_data: "Optional[dict[str, Any]]" = (
        None if not session_id else json.loads(await cache.get(session_id))
    )
    session_update = strategy.get(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return ExecuteTransformationResponse(**session_update)


@ROUTER.post(
    "/{transformation_id}/initialize",
    response_model=InitializeTransformationResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_transformation(
    cache: TRedisPlugin,
    transformation_id: str,
    session_id: Optional[str] = None,
) -> InitializeTransformationResponse:
    """Initialize a transformation."""
    # Fetch transformation info from cache
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    config = TransformationConfig(**json.loads(await cache.get(transformation_id)))

    strategy: "ITransformationStrategy" = create_strategy("transformation", config)
    session_data: "Optional[dict[str, Any]]" = (
        None if not session_id else json.loads(await cache.get(session_id))
    )
    session_update = strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeTransformationResponse(**session_update)

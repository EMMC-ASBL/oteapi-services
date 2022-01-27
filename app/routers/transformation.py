"""Transformation."""
import json
from typing import Dict, Literal, Optional
from uuid import uuid4

from aioredis import Redis
from fastapi import APIRouter, Depends
from fastapi_plugins import depends_redis
from oteapi.models import TransformationConfig
from oteapi.plugins import create_strategy
from starlette.status import HTTP_404_NOT_FOUND

from app.models.response import (
    HTTPNotFoundError,
    Status,
    httpexception_404_item_id_does_not_exist,
)

from .session import _update_session, _update_session_list_item

router = APIRouter(prefix="/transformation")

IDPREDIX = "transformation-"


@router.post(
    "/",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def create_transformation(
    config: TransformationConfig,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> Dict[Literal["transformation_id"], str]:
    """Create a new transformation configuration"""
    transformation_id = IDPREDIX + str(uuid4())

    await cache.set(transformation_id, config.json())
    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(
            session_id, "transformation_info", [transformation_id], cache
        )
    return {"transformation_id": transformation_id}


@router.get(
    "/{transformation_id}/status",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_transformation_status(
    # transformation_id might be removed in the future
    # but is needed to create the strategy
    transformation_id: str,
    task_id: str,
    cache: Redis = Depends(depends_redis),
) -> dict:
    """Get the current status of a defined transformation"""
    # Fetch transformation info from cache and populate the pydantic model
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )
    json_doc = await cache.get(transformation_id)
    transformation_info_json = json.loads(json_doc)
    transformation_info = TransformationConfig(**transformation_info_json)

    # Apply the appropriate transformation strategy (plugin) using the factory
    transformation_strategy = create_strategy("transformation", transformation_info)

    status = transformation_strategy.status(task_id)
    return status


@router.get(
    "/{transformation_id}",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_transformation(
    transformation_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> dict:
    """Get transformation"""

    # Fetch transformation info from cache and populate the pydantic model
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )
    json_doc = await cache.get(transformation_id)
    transformation_info_json = json.loads(json_doc)
    transformation_info = TransformationConfig(**transformation_info_json)

    # Apply the appropriate transformation strategy (plugin) using the factory
    transformation_strategy = create_strategy("transformation", transformation_info)

    session_data = None if not session_id else json.loads(await cache.get(session_id))
    result = transformation_strategy.get(session_data)
    if result and session_id:
        await _update_session(session_id, result, cache)

    return result


@router.post(
    "/{transformation_id}/execute",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def execute_transformation(
    transformation_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> dict:
    """Execute (run) a transformation"""
    # Fetch transformation info from cache
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )
    transformation_info = json.loads(await cache.get(transformation_id))

    # Apply the appropriate transformation strategy (plugin) using the factory
    transformation_strategy = create_strategy(
        "transformation",
        TransformationConfig(**transformation_info),
    )

    # If session id is given, pass the object to the strategy create function
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    run_result = transformation_strategy.run(session_data)

    if session_id and run_result:
        await _update_session(session_id, run_result, cache)

    return run_result


@router.post(
    "/{transformation_id}/initialize",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_transformation(
    transformation_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> dict:
    """Initialize a transformation"""
    # Fetch transformation info from cache
    if not await cache.exists(transformation_id):
        raise httpexception_404_item_id_does_not_exist(
            transformation_id, "transformation_id"
        )
    transformation_info = json.loads(await cache.get(transformation_id))

    # Apply the appropriate transformation strategy (plugin) using the factory
    transformation_strategy = create_strategy(
        "transformation",
        TransformationConfig(**transformation_info),
    )

    # If session id is given, pass the object to the strategy create function
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    init_result = transformation_strategy.initialize(session_data)

    if session_id and init_result:
        await _update_session(session_id, init_result, cache)

    return init_result

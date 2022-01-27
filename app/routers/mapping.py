"""Mapping."""
import json
from typing import Any, Dict, Optional
from uuid import uuid4

from aioredis import Redis
from fastapi import APIRouter, Depends
from fastapi_plugins import depends_redis
from oteapi.models import MappingConfig
from oteapi.plugins import create_strategy
from starlette.status import HTTP_404_NOT_FOUND

from app.models.response import (
    HTTPNotFoundError,
    Status,
    httpexception_404_item_id_does_not_exist,
)

from .session import _update_session, _update_session_list_item

router = APIRouter(prefix="/mapping")

IDPREDIX = "mapping-"


@router.post(
    "/",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def create_mapping(
    config: MappingConfig,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, Any]:
    """Define a new mapping configuration (ontological representation)
    Mapping (ontology alignment), is the process of defining
    relationships between concepts in ontologies.
    """
    mapping_id = IDPREDIX + str(uuid4())

    await cache.set(mapping_id, config.json())
    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(session_id, "mapping_info", [mapping_id], cache)
    return dict(mapping_id=mapping_id)


@router.get(
    "/{mapping_id}",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_mapping(
    mapping_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, Any]:
    """Run and return data"""
    if not await cache.exists(mapping_id):
        raise httpexception_404_item_id_does_not_exist(mapping_id, "mapping_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    mapping_info_json = json.loads(await cache.get(mapping_id))
    mapping_info = MappingConfig(**mapping_info_json)

    mapping_strategy = create_strategy("mapping", mapping_info)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    result = mapping_strategy.get(session_data)
    if result and session_id:
        await _update_session(session_id, result, cache)

    return result


@router.post(
    "/{mapping_id}/initialize",
    response_model=Status,
    response_model_exclude_unset=True,
    responses={
        HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_mapping(
    mapping_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, Any]:
    """Initialize and update session"""
    if not await cache.exists(mapping_id):
        raise httpexception_404_item_id_does_not_exist(mapping_id, "mapping_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    mapping_info_json = json.loads(await cache.get(mapping_id))
    mapping_info = MappingConfig(**mapping_info_json)

    mapping_strategy = create_strategy("mapping", mapping_info)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    result = mapping_strategy.initialize(session_data)
    if result and session_id:
        await _update_session(session_id, result, cache)

    return result

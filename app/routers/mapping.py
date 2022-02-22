"""Mapping."""
import json
from typing import TYPE_CHECKING, Optional

from aioredis import Redis
from fastapi import APIRouter, Depends, status
from fastapi_plugins import depends_redis
from oteapi.models import MappingConfig
from oteapi.plugins import create_strategy

from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.models.mapping import (
    IDPREFIX,
    CreateMappingResponse,
    GetMappingResponse,
    InitializeMappingResponse,
)
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict

ROUTER = APIRouter(prefix=f"/{IDPREFIX}")


@ROUTER.post(
    "/",
    response_model=CreateMappingResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def create_mapping(
    config: MappingConfig,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> CreateMappingResponse:
    """Define a new mapping configuration (ontological representation)
    Mapping (ontology alignment), is the process of defining
    relationships between concepts in ontologies.
    """
    new_mapping = CreateMappingResponse()

    await cache.set(new_mapping.mapping_id, config.json())

    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="mapping_info",
            list_items=[new_mapping.mapping_id],
            redis=cache,
        )

    return new_mapping


@ROUTER.get(
    "/{mapping_id}",
    response_model=GetMappingResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_mapping(
    mapping_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> GetMappingResponse:
    """Run and return data"""
    if not await cache.exists(mapping_id):
        raise httpexception_404_item_id_does_not_exist(mapping_id, "mapping_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    # Using `.construct` here to avoid validation of already validated data.
    # This is a slight speed up.
    # https://pydantic-docs.helpmanual.io/usage/models/#creating-models-without-validation
    config = MappingConfig.construct(**json.loads(await cache.get(mapping_id)))

    mapping_strategy = create_strategy("mapping", config)
    session_data: "Optional[Dict[str, Any]]" = (
        None if not session_id else json.loads(await cache.get(session_id))
    )
    session_update = mapping_strategy.get(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetMappingResponse(**session_update)


@ROUTER.post(
    "/{mapping_id}/initialize",
    response_model=InitializeMappingResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_mapping(
    mapping_id: str,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> InitializeMappingResponse:
    """Initialize and update session."""
    if not await cache.exists(mapping_id):
        raise httpexception_404_item_id_does_not_exist(mapping_id, "mapping_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    # Using `.construct` here to avoid validation of already validated data.
    # This is a slight speed up.
    # https://pydantic-docs.helpmanual.io/usage/models/#creating-models-without-validation
    config = MappingConfig.construct(**json.loads(await cache.get(mapping_id)))

    mapping_strategy = create_strategy("mapping", config)
    session_data: "Optional[Dict[str, Any]]" = (
        None if not session_id else json.loads(await cache.get(session_id))
    )
    session_update = mapping_strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id,
            updated_session=session_update,
            redis=cache,
        )

    return InitializeMappingResponse(**session_update)

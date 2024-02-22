"""Mapping."""

import json
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, status
from oteapi.models import MappingConfig
from oteapi.plugins import create_strategy

from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.models.mapping import (
    IDPREFIX,
    CreateMappingResponse,
    GetMappingResponse,
    InitializeMappingResponse,
)
from app.redis_cache import TRedisPlugin
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

ROUTER = APIRouter(prefix=f"/{IDPREFIX}", tags=["mapping"])


@ROUTER.post(
    "/",
    response_model=CreateMappingResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def create_mapping(
    cache: TRedisPlugin,
    config: MappingConfig,
    session_id: Optional[str] = None,
) -> CreateMappingResponse:
    """Define a new mapping configuration (ontological representation)
    Mapping (ontology alignment), is the process of defining
    relationships between concepts in ontologies.
    """
    new_mapping = CreateMappingResponse()

    await cache.set(new_mapping.mapping_id, config.model_dump_json())

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
    cache: TRedisPlugin,
    mapping_id: str,
    session_id: Optional[str] = None,
) -> GetMappingResponse:
    """Run and return data"""
    if not await cache.exists(mapping_id):
        raise httpexception_404_item_id_does_not_exist(mapping_id, "mapping_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(mapping_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {mapping_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = MappingConfig(**json.loads(cache_value))

    mapping_strategy = create_strategy("mapping", config)

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
    cache: TRedisPlugin,
    mapping_id: str,
    session_id: Optional[str] = None,
) -> InitializeMappingResponse:
    """
    Initialize and update session.

    - **mapping_id**: Unique identifier of a mapping configuration
    - **session_id**: Optional reference to a session object
    """
    if not await cache.exists(mapping_id):
        raise httpexception_404_item_id_does_not_exist(mapping_id, "mapping_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(mapping_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {mapping_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = MappingConfig(**json.loads(cache_value))

    mapping_strategy = create_strategy("mapping", config)

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
    session_update = mapping_strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id,
            updated_session=session_update,
            redis=cache,
        )

    return InitializeMappingResponse(**session_update)

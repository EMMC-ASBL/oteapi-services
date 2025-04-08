"""Mapping."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from fastapi import APIRouter, status
from oteapi.models import MappingConfig
from oteapi.plugins import create_strategy
from oteapi.utils.config_updater import populate_config_from_session

from app.models.error import HTTPNotFoundError
from app.models.mapping import (
    IDPREFIX,
    CreateMappingResponse,
    GetMappingResponse,
    InitializeMappingResponse,
)
from app.redis_cache import TRedisPlugin
from app.redis_cache._cache import _fetch_cache_value, _validate_cache_key
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from oteapi.interfaces import IMappingStrategy

ROUTER = APIRouter(
    prefix=f"/{IDPREFIX}",
    tags=["mapping"],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)


@ROUTER.post("/", response_model=CreateMappingResponse)
async def create_mapping(
    cache: TRedisPlugin,
    config: MappingConfig,
    session_id: str | None = None,
) -> CreateMappingResponse:
    """Define a new mapping configuration (ontological representation)
    Mapping (ontology alignment), is the process of defining
    relationships between concepts in ontologies.
    """
    new_mapping = CreateMappingResponse()

    await cache.set(new_mapping.mapping_id, config.model_dump_json())

    if session_id:
        await _validate_cache_key(cache, session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="mapping_info",
            list_items=[new_mapping.mapping_id],
            redis=cache,
        )

    return new_mapping


@ROUTER.get("/{mapping_id}", response_model=GetMappingResponse)
async def get_mapping(
    cache: TRedisPlugin,
    mapping_id: str,
    session_id: str | None = None,
) -> GetMappingResponse:
    """Run and return data"""
    cache_value = await _fetch_cache_value(cache, mapping_id, "mapping_id")
    config = MappingConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    mapping_strategy: IMappingStrategy = create_strategy("mapping", config)
    session_update = mapping_strategy.get()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetMappingResponse(**session_update)


@ROUTER.post("/{mapping_id}/initialize", response_model=InitializeMappingResponse)
async def initialize_mapping(
    cache: TRedisPlugin,
    mapping_id: str,
    session_id: str | None = None,
) -> InitializeMappingResponse:
    """
    Initialize and update session.

    - **mapping_id**: Unique identifier of a mapping configuration
    - **session_id**: Optional reference to a session object
    """
    cache_value = await _fetch_cache_value(cache, mapping_id, "mapping_id")
    config = MappingConfig(**json.loads(cache_value))

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    mapping_strategy: IMappingStrategy = create_strategy("mapping", config)
    session_update = mapping_strategy.initialize()

    if session_update and session_id:
        await _update_session(
            session_id=session_id,
            updated_session=session_update,
            redis=cache,
        )

    return InitializeMappingResponse(**session_update)

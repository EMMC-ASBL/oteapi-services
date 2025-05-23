"""Parser"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, status
from oteapi.models import ParserConfig
from oteapi.plugins import create_strategy
from oteapi.utils.config_updater import populate_config_from_session

from app.models.error import HTTPNotFoundError
from app.models.parser import (
    IDPREFIX,
    CreateParserResponse,
    GetParserResponse,
    InitializeParserResponse,
)
from app.redis_cache import TRedisPlugin
from app.redis_cache._cache import _fetch_cache_value, _validate_cache_key
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from oteapi.interfaces import IParseStrategy

LOGGER = logging.getLogger(__name__)

ROUTER = APIRouter(
    prefix=f"/{IDPREFIX}",
    tags=["parser"],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)


# Create parser
@ROUTER.post("/", response_model=CreateParserResponse)
async def create_parser(
    cache: TRedisPlugin, config: ParserConfig, session_id: str | None = None
) -> CreateParserResponse:
    """Create a new parser and store its configuration in cache."""
    new_parser = CreateParserResponse()

    await cache.set(new_parser.parser_id, config.model_dump_json())

    if session_id:
        await _validate_cache_key(cache, session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="resource_info",
            list_items=[new_parser.parser_id],
            redis=cache,
        )

    return new_parser


# Get parser info
@ROUTER.get("/{parser_id}/info", response_model=ParserConfig, include_in_schema=False)
async def info_parser(cache: TRedisPlugin, parser_id: str) -> ParserConfig:
    """Get information about a specific parser."""
    cache_value = await _fetch_cache_value(cache, parser_id, "parser_id")
    config_dict = json.loads(cache_value)
    return ParserConfig(**config_dict)


# Run `get` on parser
@ROUTER.get("/{parser_id}", response_model=GetParserResponse)
async def get_parser(
    cache: TRedisPlugin, parser_id: str, session_id: str | None = None
) -> GetParserResponse:
    """Retrieve and parse data using a specified parser."""
    cache_value = await _fetch_cache_value(cache, parser_id, "parser_id")
    config_dict = json.loads(cache_value)
    config = ParserConfig(**config_dict)

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    strategy: IParseStrategy = create_strategy("parse", config)

    LOGGER.debug(str(strategy.parse_config.model_dump()))
    session_update = strategy.get()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetParserResponse(**session_update)


@ROUTER.post("/{parser_id}/initialize", response_model=InitializeParserResponse)
async def initialize_parser(
    cache: TRedisPlugin,
    parser_id: str,
    session_id: str | None = None,
) -> InitializeParserResponse:
    """Initialize parser."""
    cache_value = await _fetch_cache_value(cache, parser_id, "parser_id")
    config_dict = json.loads(cache_value)
    config = ParserConfig(**config_dict)

    if session_id:
        session_data = await _fetch_cache_value(cache, session_id, "session_id")
        populate_config_from_session(json.loads(session_data), config)

    strategy: IParseStrategy = create_strategy("parse", config)

    LOGGER.debug(str(strategy.parse_config.model_dump()))
    session_update = strategy.initialize()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeParserResponse(**session_update)

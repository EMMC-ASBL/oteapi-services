"""Parser"""

import json
import logging
from typing import TYPE_CHECKING, Optional

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
from app.redis_cache._cache import _fetch_cache_value
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from oteapi.interfaces import IParseStrategy

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.routers.parser")

ROUTER = APIRouter(
    prefix=f"/{IDPREFIX}",
    tags=["parser"],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)


# Create parser
@ROUTER.post("/", response_model=CreateParserResponse)
async def create_parser(
    cache: TRedisPlugin, config: ParserConfig, session_id: Optional[str] = None
) -> CreateParserResponse:
    """Create a new parser and store its configuration in cache."""
    new_parser = CreateParserResponse()

    await cache.set(new_parser.parser_id, config.model_dump_json())

    if session_id:
        await _fetch_cache_value(cache, session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="resource_info",
            list_items=[new_parser.parser_id],
            redis=cache,
        )

    return new_parser


# Get parser info
@ROUTER.get("/{parser_id}/info", response_model=ParserConfig)
async def info_parser(cache: TRedisPlugin, parser_id: str) -> ParserConfig:
    """Get information about a specific parser."""
    await _fetch_cache_value(cache, parser_id, "parser_id")
    cache_value = await cache.get(parser_id)
    if cache_value is None:
        raise ValueError("Cache value is None")
    config_dict = json.loads(cache_value)
    return ParserConfig(**config_dict)


# Run `get` on parser
@ROUTER.get("/{parser_id}", response_model=GetParserResponse)
async def get_parser(
    cache: TRedisPlugin, parser_id: str, session_id: Optional[str] = None
) -> GetParserResponse:
    """Retrieve and parse data using a specified parser."""
    await _fetch_cache_value(cache, parser_id, "parser_id")
    cache_value = await cache.get(parser_id)
    if cache_value is None:
        raise ValueError("Cache value is None")
    config_dict = json.loads(cache_value)
    config = ParserConfig(**config_dict)

    if session_id:
        await _fetch_cache_value(cache, session_id, "session_id")
        session_data = await cache.get(session_id)
        if session_data is None:
            raise ValueError("Session data is None")
        populate_config_from_session(json.loads(session_data), config)

    strategy: "IParseStrategy" = create_strategy("parse", config)

    logger.debug(str(strategy.parse_config.model_dump()))
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
    session_id: Optional[str] = None,
) -> InitializeParserResponse:
    """Initialize parser."""
    await _fetch_cache_value(cache, parser_id, "parser_id")
    cache_value = await cache.get(parser_id)
    if cache_value is None:
        raise ValueError("Cache value is None")
    config_dict = json.loads(cache_value)
    config = ParserConfig(**config_dict)

    if session_id:
        await _fetch_cache_value(cache, session_id, "session_id")
        session_data = await cache.get(session_id)
        if session_data is None:
            raise ValueError("Session data is None")
        populate_config_from_session(json.loads(session_data), config)

    strategy: "IParseStrategy" = create_strategy("parse", config)

    logger.debug(str(strategy.parse_config.model_dump()))
    session_update = strategy.initialize()

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeParserResponse(**session_update)

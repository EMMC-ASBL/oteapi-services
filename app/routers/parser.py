"""Parser"""

import json
import logging
from typing import TYPE_CHECKING, Any, Optional

from fastapi import APIRouter, status
from oteapi.models import ParserConfig
from oteapi.plugins import create_strategy
from oteapi.utils.config_updater import populate_config_from_session

from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.models.parser import (
    IDPREFIX,
    CreateParserResponse,
    DeleteAllParsersResponse,
    GetParserResponse,
    InitializeParserResponse,
    ListParsersResponse,
)
from app.redis_cache import TRedisPlugin
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from oteapi.interfaces import IParseStrategy

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.routers.parser")

ROUTER = APIRouter(prefix=f"/{IDPREFIX}", tags=["parser"])


async def _validate_cache_key(cache: TRedisPlugin, key: str, key_type: str) -> None:
    """Validate if a key exists in cache and is of expected type (str or bytes)."""
    if not await cache.exists(key):
        raise httpexception_404_item_id_does_not_exist(key, key_type)

    cache_value = await cache.get(key)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {key} to be a string or bytes, "
            f"found it to be of type: `{type(cache_value)!r}`."
        )


# Create parser
@ROUTER.post(
    "/",
    response_model=CreateParserResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def create_parser(
    cache: TRedisPlugin, config: ParserConfig, session_id: Optional[str] = None
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


@ROUTER.delete(
    "/",
    response_model=DeleteAllParsersResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def delete_all_parsers(
    cache: TRedisPlugin,
) -> DeleteAllParsersResponse:
    """
    Delete all parser configurations in the current memory database
    """
    keylist = await cache.keys(pattern=f"{IDPREFIX}*")
    if not keylist:
        return DeleteAllParsersResponse(number_of_deleted_parsers=0)
    return DeleteAllParsersResponse(
        number_of_deleted_parsers=await cache.delete(*keylist)
    )


# List parsers
@ROUTER.get(
    "/",
    response_model=ListParsersResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def list_parsers(cache: TRedisPlugin) -> ListParsersResponse:
    """Retrieve all parser IDs from cache."""
    keylist = [
        key
        for key in await cache.keys(pattern=f"{IDPREFIX}*")
        if isinstance(key, (str, bytes))
    ]
    return ListParsersResponse(keys=keylist)


# Get parser info
@ROUTER.get(
    "/{parser_id}/info",
    response_model=ParserConfig,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def info_parser(cache: TRedisPlugin, parser_id: str) -> ParserConfig:
    """Get information about a specific parser."""
    await _validate_cache_key(cache, parser_id, "parser_id")
    cache_value = await cache.get(parser_id)
    if cache_value is None:
        raise ValueError("Cache value is None")
    config_dict = json.loads(cache_value)
    return ParserConfig(**config_dict)


# Run `get` on parser
@ROUTER.get(
    "/{parser_id}",
    response_model=GetParserResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def get_parser(
    cache: TRedisPlugin, parser_id: str, session_id: Optional[str] = None
) -> GetParserResponse:
    """Retrieve and parse data using a specified parser."""
    await _validate_cache_key(cache, parser_id, "parser_id")
    cache_value = await cache.get(parser_id)
    if cache_value is None:
        raise ValueError("Cache value is None")
    config_dict = json.loads(cache_value)
    config = ParserConfig(**config_dict)
    session_data: "Optional[dict[str, Any]]" = None
    if session_id:
        await _validate_cache_key(cache, session_id, "session_id")
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


@ROUTER.post(
    "/{parser_id}/initialize",
    response_model=InitializeParserResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_parser(
    cache: TRedisPlugin,
    parser_id: str,
    session_id: Optional[str] = None,
) -> InitializeParserResponse:
    """Initialize parser."""
    await _validate_cache_key(cache, parser_id, "parser_id")
    cache_value = await cache.get(parser_id)
    if cache_value is None:
        raise ValueError("Cache value is None")
    config_dict = json.loads(cache_value)
    config = ParserConfig(**config_dict)
    session_data: "Optional[dict[str, Any]]" = None
    if session_id:
        await _validate_cache_key(cache, session_id, "session_id")
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

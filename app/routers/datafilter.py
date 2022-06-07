"""Data Filter."""
import importlib
import json
import logging
from typing import TYPE_CHECKING, Optional

from aioredis import Redis
from fastapi import APIRouter, Depends, Query, status
from fastapi_plugins import depends_redis
from oteapi.models import FilterConfig
from oteapi.plugins import create_strategy

from app.models.datafilter import (
    IDPREFIX,
    CreateFilterResponse,
    GetFilterResponse,
    InitializeFilterResponse,
)
from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:
    from typing import Type

ROUTER = APIRouter(prefix=f"/{IDPREFIX}")

LOGGER = logging.getLogger("app.routers")
LOGGER.setLevel(logging.DEBUG)


@ROUTER.post(
    "/",
    response_model=CreateFilterResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def create_filter(
    config: FilterConfig,
    session_id: Optional[str] = None,
    cache: Redis = Depends(depends_redis),
) -> CreateFilterResponse:
    """Define a new filter configuration (data operation)"""
    new_filter = CreateFilterResponse()

    json_encoder = None
    if hasattr(config, "json_encoder") and config.json_encoder:
        json_encoder = getattr(
            importlib.import_module(config.json_encoder[0]),
            config.json_encoder[2],
            None,
        )
        if json_encoder is None:
            LOGGER.debug(
                "Tried to set json_encoder from %s, but failed.", config.json_encoder
            )
        else:
            LOGGER.debug("Set json_encoder to %s", config.json_encoder)

    await cache.set(new_filter.filter_id, config.json(encoder=json_encoder))

    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="filter_info",
            list_items=[new_filter.filter_id],
            redis=cache,
        )

    return new_filter


@ROUTER.get(
    "/{filter_id}",
    response_model=GetFilterResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def get_filter(
    filter_id: str,
    session_id: Optional[str] = None,
    json_decoder: Optional[str] = Query(
        None,
        description=(
            "An importable path to a JSONDecoder. This JSON decoder is for decoding "
            "the strategy configuration model only."
        ),
        regex=r"^[a-zA-Z]+[a-zA-Z0-9_]*(?:\.[a-zA-Z]+[a-zA-Z0-9_]*)*:[a-zA-Z]+[a-zA-Z0-9_]*$",
        example="oteapi_plugin.utils.json:JSONDecoder",
    ),
    cache: Redis = Depends(depends_redis),
) -> GetFilterResponse:
    """Run and return data from a filter (data operation)"""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    json_decoder_cls: "Optional[Type[json.JSONDecoder]]" = None
    if json_decoder:
        json_decoder_cls = getattr(
            importlib.import_module(".".join(json_decoder.split(":")[0])),
            json_decoder.split(":")[1],
            None,
        )
        if json_decoder_cls is None:
            LOGGER.debug(
                "Tried to set json_decoder_cls from %s, but failed.", json_decoder
            )
        else:
            LOGGER.debug("Set json_decoder_cls to %s", json_decoder)

    config = FilterConfig(
        **json.loads(await cache.get(filter_id), cls=json_decoder_cls)
    )

    strategy = create_strategy("filter", config)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    session_update = strategy.get(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return GetFilterResponse(**session_update)


@ROUTER.post(
    "/{filter_id}/initialize",
    response_model=InitializeFilterResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
)
async def initialize_filter(
    filter_id: str,
    session_id: Optional[str] = None,
    json_decoder: Optional[str] = Query(
        None,
        description=(
            "An importable path to a JSONDecoder. This JSON decoder is for decoding "
            "the strategy configuration model only."
        ),
        regex=r"^[a-zA-Z]+[a-zA-Z0-9_]*(?:\.[a-zA-Z]+[a-zA-Z0-9_]*)*:[a-zA-Z]+[a-zA-Z0-9_]*$",
        example="oteapi_plugin.utils.json:JSONDecoder",
    ),
    cache: Redis = Depends(depends_redis),
) -> InitializeFilterResponse:
    """Initialize and return data to update session."""
    if not await cache.exists(filter_id):
        raise httpexception_404_item_id_does_not_exist(filter_id, "filter_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    json_decoder_cls: "Optional[Type[json.JSONDecoder]]" = None
    if json_decoder:
        json_decoder_cls = getattr(
            importlib.import_module(".".join(json_decoder.split(":")[0])),
            json_decoder.split(":")[1],
            None,
        )
        if json_decoder_cls is None:
            LOGGER.debug(
                "Tried to set json_decoder_cls from %s, but failed.", json_decoder
            )
        else:
            LOGGER.debug("Set json_decoder_cls to %s", json_decoder)

    config = FilterConfig(
        **json.loads(await cache.get(filter_id), cls=json_decoder_cls)
    )

    strategy = create_strategy("filter", config)
    session_data = None if not session_id else json.loads(await cache.get(session_id))
    session_update = strategy.initialize(session=session_data)

    if session_update and session_id:
        await _update_session(
            session_id=session_id, updated_session=session_update, redis=cache
        )

    return InitializeFilterResponse(**session_update)

"""Data Resource."""
import json
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, Request, status
from oteapi.models import ResourceConfig
from oteapi.plugins import create_strategy

from app.models.dataresource import (
    IDPREFIX,
    CreateResourceResponse,
    GetResourceResponse,
    InitializeResourceResponse,
)
from app.models.error import (
    HTTPNotFoundError,
    HTTPValidationError,
    httpexception_404_item_id_does_not_exist,
    httpexception_422_resource_id_is_unprocessable,
)
from app.redis_cache import TRedisPlugin
from app.routers.session import _update_session, _update_session_list_item

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

ROUTER = APIRouter(prefix=f"/{IDPREFIX}")


@ROUTER.post(
    "/",
    response_model=CreateResourceResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
    tags=["dataresource"],
)
async def create_dataresource(
    cache: TRedisPlugin,
    config: ResourceConfig,
    request: Request,
    session_id: Optional[str] = None,
) -> CreateResourceResponse:
    """### Register an external data resource.

    An external data resource can be any data distribution provider
    that provides services of obtaining information through queries,
    REST APIs or other protocol, or directly downloadable artifacts
    (files) through data exchange procolols (such as sftp, https
    etc...)

    If the resource URL is as direct link to a downloadable file, set
    the downloadURL property, otherwise set the accessURL the service
    and specify the service name with the mediaType property.

    """
    new_resource = CreateResourceResponse()

    config.token = request.headers.get("Authorization") or config.token

    resource_config = config.model_dump_json()

    await cache.set(new_resource.resource_id, resource_config)

    if session_id:
        if not await cache.exists(session_id):
            raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
        await _update_session_list_item(
            session_id=session_id,
            list_key="resource_info",
            list_items=[new_resource.resource_id],
            redis=cache,
        )

    return new_resource


@ROUTER.get(
    "/{resource_id}/info",
    response_model=ResourceConfig,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
    },
    tags=["dataresource"],
)
async def info_dataresource(
    cache: TRedisPlugin,
    resource_id: str,
) -> ResourceConfig:
    """Get data resource info."""
    if not await cache.exists(resource_id):
        raise httpexception_404_item_id_does_not_exist(resource_id, "resource_id")

    cache_value = await cache.get(resource_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {resource_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    return ResourceConfig(**json.loads(cache_value))


@ROUTER.get(
    "/{resource_id}",
    response_model=GetResourceResponse,
    response_model_exclude_unset=True,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPValidationError},
    },
    tags=["dataresource"],
)
async def read_dataresource(
    cache: TRedisPlugin,
    resource_id: str,
    session_id: Optional[str] = None,
) -> GetResourceResponse:
    """Read data from dataresource using the appropriate download strategy.

    Parse data information using the appropriate parser.
    """
    if not await cache.exists(resource_id):
        raise httpexception_404_item_id_does_not_exist(resource_id, "resource_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(resource_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {resource_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = ResourceConfig(**json.loads(cache_value))

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

    if config.downloadUrl and config.mediaType:
        # Download strategy
        session_update = create_strategy("download", config).get(session=session_data)
        if session_update and session_id:
            session_data = await _update_session(session_id, session_update, cache)

        # Parse strategy
        session_update = create_strategy("parse", config).get(session=session_data)
        if session_update and session_id:
            await _update_session(session_id, session_update, cache)

    elif config.accessUrl and config.accessService:
        # Resource strategy
        session_update = create_strategy("resource", config).get(session=session_data)
        if session_update and session_id:
            await _update_session(session_id, session_update, cache)

    else:
        raise httpexception_422_resource_id_is_unprocessable(resource_id)

    return GetResourceResponse(**session_update)


@ROUTER.post(
    "/{resource_id}/initialize",
    response_model=InitializeResourceResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPValidationError},
    },
    tags=["dataresource"],
)
async def initialize_dataresource(
    cache: TRedisPlugin,
    resource_id: str,
    session_id: Optional[str] = None,
) -> InitializeResourceResponse:
    """Initialize data resource."""
    if not await cache.exists(resource_id):
        raise httpexception_404_item_id_does_not_exist(resource_id, "resource_id")
    if session_id and not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(resource_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {resource_id} to be a string or bytes, "
            f"found it to be of type {type(cache_value)!r}."
        )
    config = ResourceConfig(**json.loads(cache_value))

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

    if config.downloadUrl and config.mediaType:
        # Download strategy
        session_update = create_strategy("download", config).initialize(
            session=session_data
        )
        if session_update and session_id:
            session_data = await _update_session(
                session_id=session_id, updated_session=session_update, redis=cache
            )

        # Parse strategy
        session_update = create_strategy("parse", config).initialize(
            session=session_data
        )
        if session_update and session_id:
            session_data = await _update_session(
                session_id=session_id, updated_session=session_update, redis=cache
            )

    elif config.accessUrl and config.accessService:
        # Resource strategy
        session_update = create_strategy("resource", config).initialize(
            session=session_data
        )
        if session_update and session_id:
            session_data = await _update_session(
                session_id=session_id, updated_session=session_update, redis=cache
            )

    else:
        raise httpexception_422_resource_id_is_unprocessable(resource_id)

    return InitializeResourceResponse(**session_update)

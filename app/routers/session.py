"""Microservice Session."""

import json
from typing import TYPE_CHECKING

from fastapi import APIRouter, status
from oteapi.models import AttrDict

from app.models.error import HTTPNotFoundError, httpexception_404_item_id_does_not_exist
from app.models.response import Session
from app.models.session import (
    IDPREFIX,
    CreateSessionResponse,
    DeleteAllSessionsResponse,
    DeleteSessionResponse,
    ListSessionsResponse,
)
from app.redis_cache import TRedisPlugin

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Union


ROUTER = APIRouter(
    prefix=f"/{IDPREFIX}",
    tags=["session"],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)


@ROUTER.post("/", response_model=CreateSessionResponse)
async def create_session(
    cache: TRedisPlugin,
    session: Session,
) -> CreateSessionResponse:
    """## Create a new session

    The session allows for storing keyword/value pairs of information
    on the OTE server. The session can be shared between different OTE
    microservices.

    Attributes:
        session: A key/value object to be created as a session object.
        cache: The in-memory storage engine to be used (default Redis).

    Returns:
        Object containing the session identifier.

    """
    new_session = CreateSessionResponse()
    await cache.set(new_session.session_id, session.model_dump_json())
    return new_session


@ROUTER.get("/", response_model=ListSessionsResponse)
async def list_sessions(
    cache: TRedisPlugin,
) -> ListSessionsResponse:
    """Get all session keys"""
    keylist: list[Union[str, bytes]] = []
    for key in await cache.keys(pattern=f"{IDPREFIX}*"):
        if not isinstance(key, (str, bytes)):
            raise TypeError(
                "Found a key that is not stored as bytes (stored as type "
                f"{type(key)!r})."
            )
        if isinstance(key, bytes):
            key = key.decode(encoding="utf-8")
        keylist.append(key)

    return ListSessionsResponse(keys=keylist)


@ROUTER.delete("/", response_model=DeleteAllSessionsResponse)
async def delete_all_sessions(
    cache: TRedisPlugin,
) -> DeleteAllSessionsResponse:
    """Delete all session keys.

    Danger:
        Data stored in sessions cannot be recovered after calling this endpoint.

    """
    keylist = await cache.keys(pattern=f"{IDPREFIX}*")
    # Check if the keylist is empty
    if not keylist:
        return DeleteAllSessionsResponse(
            number_of_deleted_sessions=0, message="No session keys found to delete."
        )

    return DeleteAllSessionsResponse(
        number_of_deleted_sessions=await cache.delete(*keylist)
    )


async def _get_session(
    session_id: str,
    redis: TRedisPlugin,
) -> Session:
    """Return the session contents given a `session_id`."""
    if not await redis.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")
    cache_value = await redis.get(session_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {session_id} to be a string or bytes, found it "
            f"to be of type {type(cache_value)!r}."
        )
    return Session(**json.loads(cache_value))


async def _update_session(
    session_id: str,
    updated_session: "Union[AttrDict, dict[str, Any]]",
    redis: TRedisPlugin,
) -> Session:
    """Update an existing session (to be called internally)."""
    session = await _get_session(session_id, redis)
    session.update(updated_session)
    await redis.set(session_id, session.model_dump_json().encode("utf-8"))
    return session


async def _update_session_list_item(
    session_id: str,
    list_key: str,
    list_items: list,
    redis: TRedisPlugin,
) -> Session:
    """Append to or create list items in an existing session."""
    session = await _get_session(session_id, redis)

    if not isinstance(list_items, list):
        raise TypeError(
            "Expected `list_items` to be a list, found it to be of type "
            f"{type(list_items)!r}."
        )

    if list_key in session:
        if not isinstance(session[list_key], list):
            raise TypeError(
                f"Expected type for {list_key!r} field in session to be a list, found "
                f"{type(session[list_key])!r}."
            )
        session[list_key].extend(list_items)
    else:
        session[list_key] = list_items
    await redis.set(session_id, session.model_dump_json().encode("utf-8"))
    return session


@ROUTER.put("/{session_id}", response_model=Session)
async def update_session(
    cache: TRedisPlugin,
    session_id: str,
    updated_session: AttrDict,
) -> Session:
    """Update session object."""
    if not await cache.exists(session_id):
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(session_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {session_id} to be a string or bytes, found it "
            f"to be of type {type(cache_value)!r}."
        )
    session = Session(**json.loads(cache_value))
    session.update(updated_session)
    await cache.set(session_id, session.model_dump_json().encode("utf-8"))
    return session


@ROUTER.get("/{session_id}", response_model=Session)
async def get_session(
    cache: TRedisPlugin,
    session_id: str,
) -> Session:
    """Fetch the entire session object."""
    cache_exists: int = await cache.exists(session_id)
    if not cache_exists:
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    cache_value = await cache.get(session_id)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {session_id} to be a string or bytes, found it "
            f"to be of type {type(cache_value)!r}."
        )
    return Session(**json.loads(cache_value))


@ROUTER.delete("/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(
    cache: TRedisPlugin,
    session_id: str,
) -> DeleteSessionResponse:
    """Delete a session object."""
    cache_exists: int = await cache.exists(session_id)
    if not cache_exists:
        raise httpexception_404_item_id_does_not_exist(session_id, "session_id")

    await cache.delete(session_id)
    return DeleteSessionResponse(success=True)

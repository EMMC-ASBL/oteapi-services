"""Helper service for viewing redis objects."""
import json
from typing import Any

from fastapi import APIRouter

from app.models.error import httpexception_404_item_id_does_not_exist
from app.redis_cache import TRedisPlugin

ROUTER = APIRouter(prefix="/redis")


@ROUTER.get("/{key}", include_in_schema=False)
async def get_key(
    cache: TRedisPlugin,
    key: str,
) -> dict[str, Any]:
    """Low-level cache interface to retrieve the object-value
    stored with key 'key'
    """
    if not await cache.exists(key):
        raise httpexception_404_item_id_does_not_exist(key, "key")

    cache_value = await cache.get(key)
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {key} to be a string or bytes, found it "
            f"to be of type {type(cache_value)!r}."
        )
    return json.loads(cache_value)

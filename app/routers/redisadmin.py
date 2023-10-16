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
    return json.loads(await cache.get(key))

"""Helper service for viewing redis objects."""
import json
from typing import Any, Dict

from aioredis import Redis
from fastapi import APIRouter, Depends
from fastapi_plugins import depends_redis

from app.models.error import httpexception_404_item_id_does_not_exist

ROUTER = APIRouter(prefix="/redis")


@ROUTER.get("/{key}", include_in_schema=False)
async def get_key(
    key: str,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, Any]:
    """Low-level cache interface to retrieve the object-value
    stored with key 'key'
    """
    if not await cache.exists(key):
        raise httpexception_404_item_id_does_not_exist(key, "key")
    return json.loads(await cache.get(key))

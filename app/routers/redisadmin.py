"""Helper service for viewing redis objects."""
import json
from typing import Dict, List

from aioredis import Redis
from fastapi import APIRouter, Depends
from fastapi_plugins import depends_redis

ROUTER = APIRouter(prefix="/redis")


@ROUTER.get("/{key}", include_in_schema=False)
async def get_gey(
    key: str,
    cache: Redis = Depends(depends_redis),
) -> Dict[str, List[str]]:
    """Low-level cache interface to retrieve the object-value
    stored with key 'key'
    """
    return json.loads(await cache.get(key))

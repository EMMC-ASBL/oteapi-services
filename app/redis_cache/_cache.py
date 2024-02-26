"Cache operations"
from typing import Any

from app.models.error import httpexception_404_item_id_does_not_exist
from app.redis_cache import TRedisPlugin


async def _fetch_cache_value(cache: TRedisPlugin, key: str, key_type: str) -> Any:
    """Validate if a key exists in cache and is of expected type (str or bytes)."""
    if not await cache.exists(key):
        raise httpexception_404_item_id_does_not_exist(key, key_type)

    cache_value = await cache.get(key)
    if cache_value is None:
        raise ValueError(f"Cache value for key '{key}' is None.")
    elif not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {key} to be a string or bytes, "
            f"found it to be of type: `{type(cache_value)!r}`."
        )
    else:
        return cache_value

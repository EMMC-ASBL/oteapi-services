"""Cache operations."""

from __future__ import annotations

from typing import Any

from app.models.error import httpexception_404_item_id_does_not_exist
from app.redis_cache import TRedisPlugin


async def _fetch_cache_value(cache: TRedisPlugin, key: str, key_type: str) -> Any:
    """Fetch key value from Cache and check if its of expected type (str or bytes)."""
    await _validate_cache_key(cache, key, key_type)

    cache_value = await cache.get(key)
    if cache_value is None:
        raise ValueError(f"Cache value for key '{key}' is None.")
    if not isinstance(cache_value, (str, bytes)):
        raise TypeError(
            f"Expected cache value of {key} to be a string or bytes, "
            f"found it to be of type: `{type(cache_value)!r}`."
        )
    return cache_value


async def _validate_cache_key(cache: TRedisPlugin, key: str, key_type: str) -> None:
    """Validate if a key exists in cache and is of expected type (str or bytes)."""
    if not await cache.exists(key):
        raise httpexception_404_item_id_does_not_exist(key, key_type)

"""Redis support for FastAPI.

This module is an adaptation of the `fastapi_plugins` package's Redis plugin.
The original developer is @madkote (https://madkote.github.io).

The original code is available at:
https://github.com/madkote/fastapi-plugins/blob/26f31177634ba84ca73c63f84535af205135d781/fastapi_plugins/_redis.py

"""

import warnings
from collections.abc import Awaitable
from enum import Enum, unique
from typing import TYPE_CHECKING, Annotated, Any, Optional, Union

import redis.asyncio as aredis
import redis.asyncio.sentinel as aredis_sentinel
import starlette.requests
import tenacity
from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis import ConnectionError as RedisConnectionError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable

    from mypy_extensions import KwArg


__all__ = [
    "RedisError",
    "RedisType",
    "RedisSettings",
    "RedisPlugin",
    "redis_plugin",
    "depends_redis",
    "TRedisPlugin",
]


class RedisError(Exception):
    """Base Redis exception."""


@unique
class RedisType(str, Enum):
    """Redis type."""

    REDIS = "redis"
    SENTINEL = "sentinel"
    FAKEREDIS = "fakeredis"
    # cluster = 'cluster'


class RedisSettings(BaseSettings):
    """Redis pydantic settings (used by FastAPI)."""

    model_config = SettingsConfigDict(env_prefix="", use_enum_values=True)

    redis_type: RedisType = RedisType.REDIS

    redis_url: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_user: Optional[str] = None
    redis_password: Optional[str] = None
    redis_db: Optional[int] = None
    # redis_connection_timeout: int = 2

    # redis_pool_minsize: int = 1
    # redis_pool_maxsize: int = None
    redis_max_connections: Optional[int] = None
    redis_decode_responses: bool = True

    # redis_sentinels: typing.List = None
    redis_sentinels: Optional[str] = None
    redis_sentinel_master: str = "mymaster"

    redis_prestart_tries: int = 60 * 5  # 5 min
    redis_prestart_wait: int = 1  # 1 second

    def get_redis_address(self) -> str:
        """Get redis address."""
        if self.redis_url:
            return self.redis_url
        if self.redis_db:
            return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}"

    def get_sentinels(self) -> list[tuple[str, int]]:
        """Get redis sentinels."""
        if self.redis_sentinels:
            try:
                return [
                    (_conn.split(":")[0].strip(), int(_conn.split(":")[1].strip()))
                    for _conn in self.redis_sentinels.split(",")
                    if _conn.strip()
                ]
            except Exception as exc:
                raise RuntimeError(
                    f"bad sentinels string :: {type(exc)} :: {exc} :: "
                    f"{self.redis_sentinels}"
                ) from exc
        return []


class RedisPlugin:
    """Redis plugin for FastAPI."""

    DEFAULT_CONFIG_CLASS = RedisSettings

    config: Optional[RedisSettings]

    def __init__(self) -> None:
        self.redis: Optional[Union[aredis.Redis, aredis_sentinel.Sentinel]] = None

    def __call__(self) -> Awaitable[Union[aredis_sentinel.Sentinel, aredis.Redis]]:
        return self._on_call()

    async def _on_call(self) -> Union[aredis_sentinel.Sentinel, aredis.Redis]:
        """Get Redis connection."""
        if self.redis is None:
            raise RedisError("Redis is not initialized")

        if self.config is None:
            raise RedisError("Redis configuration is not initialized")

        if self.config.redis_type == RedisType.SENTINEL:
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(self.redis, aredis_sentinel.Sentinel)  # nosec

            conn: Union[aredis_sentinel.Sentinel, aredis.Redis] = self.redis.master_for(
                self.config.redis_sentinel_master
            )
        elif self.config.redis_type in (RedisType.REDIS, RedisType.FAKEREDIS):
            conn = self.redis
        else:
            raise NotImplementedError(
                f"Redis type {self.config.redis_type.value} is not implemented"
            )

        return conn

    async def init_app(
        self, app: FastAPI, config: Optional[RedisSettings] = None
    ) -> None:
        """Initialize plugin via FastAPI application object."""
        self.config = config or self.DEFAULT_CONFIG_CLASS()
        if self.config is None:
            raise RedisError("Redis configuration is not initialized")
        if not isinstance(self.config, self.DEFAULT_CONFIG_CLASS):
            raise RedisError("Redis configuration is not valid")
        app.state.REDIS = self

    async def init(self) -> None:
        """Initialize plugin."""
        if self.redis is not None:
            raise RedisError("Redis is already initialized")

        if self.config is None:
            raise RedisError("Redis configuration is not initialized")

        opts = {
            "db": self.config.redis_db,
            "username": self.config.redis_user,
            "password": self.config.redis_password,
            # "minsize": self.config.redis_pool_minsize,
            # "maxsize": self.config.redis_pool_maxsize,
            "max_connections": self.config.redis_max_connections,
            "decode_responses": self.config.redis_decode_responses,
        }

        if TYPE_CHECKING:  # pragma: no cover
            address: Union[str, list[tuple[str, int]]]
            method: Union[
                Callable[[str, KwArg(Any)], aredis.Redis],
                type[aredis_sentinel.Sentinel],
            ]

        if self.config.redis_type == RedisType.REDIS:
            address = self.config.get_redis_address()
            method = aredis.from_url  # type: ignore[assignment]
            # opts.update(dict(timeout=self.config.redis_connection_timeout))
        elif self.config.redis_type == RedisType.FAKEREDIS:
            try:
                import fakeredis.aioredis  # pylint: disable=import-outside-toplevel
            except ImportError as exc:
                raise RedisError(
                    f"{self.config.redis_type.value} requires fakeredis to be installed"
                ) from exc

            address = self.config.get_redis_address()
            method = fakeredis.aioredis.FakeRedis.from_url
        elif self.config.redis_type == RedisType.SENTINEL:
            address = self.config.get_sentinels()
            method = aredis_sentinel.Sentinel
        else:
            raise NotImplementedError(
                f"Redis type {self.config.redis_type.value} is not implemented"
            )

        if not address:
            raise ValueError("Redis address is empty")

        @tenacity.retry(
            stop=tenacity.stop_after_attempt(self.config.redis_prestart_tries),
            wait=tenacity.wait_fixed(self.config.redis_prestart_wait),
        )
        async def _inner():
            return method(address, **opts)

        self.redis = await _inner()

        # Check availability - fallback to fakeredis
        try:
            await self.ping()
        except RedisConnectionError as exc:
            # If not using fakeredis, change and use fakeredis
            # Otherwise, re-raise
            if self.config.redis_type == RedisType.FAKEREDIS:
                # Re-raise
                raise exc

            # Emit warning about falling back to fakeredis
            warnings.warn("No live Redis server found - falling back to fakeredis !")

            # Reset redis attribute and set redis type to fakeredis
            self.redis = None
            self.config.redis_type = RedisType.FAKEREDIS

            # Re-run this method (now using fakeredis)
            return await self.init()

    async def terminate(self) -> None:
        """Terminate plugin."""
        self.config = None

        if self.redis is not None:
            # del self.redis
            await self.redis.aclose()  # type: ignore[union-attr]
            self.redis = None

    async def health(self) -> dict[str, "Any"]:
        """Get Redis health status."""
        if self.config is None:
            raise RedisError("Redis configuration is not initialized")

        return {
            "redis_type": self.config.redis_type,
            "redis_address": (
                self.config.get_sentinels()
                if self.config.redis_type == RedisType.SENTINEL
                else self.config.get_redis_address()
            ),
            "redis_pong": (await self.ping()),
        }

    async def ping(self) -> Union[Awaitable, Any]:
        """Ping Redis."""
        if self.config is None:
            raise RedisError("Redis configuration is not initialized")

        if self.config.redis_type in (RedisType.REDIS, RedisType.FAKEREDIS):
            return await self.redis.ping()  # type: ignore[union-attr]

        if self.config.redis_type == RedisType.SENTINEL:
            if TYPE_CHECKING:  # pragma: no cover
                assert isinstance(self.redis, aredis_sentinel.Sentinel)  # nosec

            return await self.redis.master_for(self.config.redis_sentinel_master).ping()

        raise NotImplementedError(
            f"Redis type {self.config.redis_type.value}.ping() is not implemented"
        )


redis_plugin = RedisPlugin()


async def depends_redis(conn: starlette.requests.HTTPConnection) -> aredis.Redis:
    """Get Redis connection."""
    return await conn.app.state.REDIS()


TRedisPlugin = Annotated[aredis.Redis, Depends(depends_redis)]

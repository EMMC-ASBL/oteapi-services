"""OTEAPI Services server settings."""

from __future__ import annotations

import os
import warnings
from functools import lru_cache
from typing import Annotated

from oteapi.settings import OteApiCoreSettings
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from app import __version__
from app.redis_cache import RedisSettings


class AppSettings(RedisSettings, OteApiCoreSettings):
    """OTEAPI Services FastAPI application settings."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="OTEAPI_",
        env_file=".env",
        extra="ignore",
    )

    debug: Annotated[
        bool,
        Field(
            description="Enable debug mode.",
        ),
    ] = False

    include_redisadmin: Annotated[
        bool,
        Field(
            description="""If set to `True`,
            the router for the low-level cache interface will be included into the api.
            WARNING: This might NOT be recommended for specific production cases,
            since sensible data (such as secrets) in the cache might be revealed by
            inspecting other user's session objects. If set to false, the cache can
            only be read from an admin accessing the redis backend.""",
        ),
    ] = False

    authentication_dependencies: Annotated[
        str,
        Field(description="List of FastAPI dependencies for authentication features."),
    ] = ""

    api_name: Annotated[
        str, Field(description="Application-specific name for Redis cache.")
    ] = "oteapi_services"

    prefix: Annotated[
        str,
        Field(
            description="Application route prefix.",
        ),
    ] = f"/api/v{__version__.split('.', maxsplit=1)[0]}"

    @field_validator("debug", mode="after")
    @classmethod
    def _check_dev_env_var(cls, value: bool) -> bool:
        """Check if `DEV_ENV` is set, use to update debug mode."""
        dev_env = os.getenv("DEV_ENV")

        if dev_env:
            try:
                value = bool(int(dev_env))
            except (ValueError, TypeError):
                # Just use current value
                warnings.warn(
                    f"DEV_ENV value '{dev_env}' is not a valid integer.", stacklevel=2
                )

        return value


@lru_cache
def get_settings() -> AppSettings:
    """Get application settings.

    Returns:
        Application settings.

    """
    return AppSettings()

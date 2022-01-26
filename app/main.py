"""OTE-API FastAPI application."""
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_plugins import RedisSettings, redis_plugin
from oteapi.plugins import load_plugins
from pydantic import Field

from app import __version__
from app.routers import (
    datafilter,
    dataresource,
    mapping,
    redisadmin,
    session,
    transformation,
)

if TYPE_CHECKING:
    from typing import Any, Dict


class AppSettings(RedisSettings):
    """Redis settings."""

    api_name: str = Field(
        "oteapi_services", description="Application-specific name for Redis cache."
    )
    prefix: str = Field("/api/v1", description="Application route prefix.")

    class Config:
        """OTE-API Services application configuration."""

        env_prefix = "OTEAPI_"


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    app = FastAPI(
        title="Open Translation Environment API",
        version=__version__,
        description="""OntoTrans Interfaces OpenAPI schema.

The generic interfaces are implemented in dynamic plugins which
are concrete strategy implementations of the following types:

- **Download strategy** (access data via different protocols, such as *https* and *sftp*)
- **Parse strategy** (data type specific interpreters, such as *image/jpeg*, *text/csv*, *application/sql*)
- **Resource strategy** (Information resource, downloadables or services)
- **Mapping strategy** (define relations between business data and conceptual information)
- **Filter operation strategy** (defines specify views/operations)
- **Transformation strategy** (asyncronous operations)

This service is based on:

- **oteapi-core**: v0.0.3

        """,
    )
    for router_module in (
        session,
        dataresource,
        transformation,
        datafilter,
        mapping,
        redisadmin,
    ):
        app.include_router(router_module.router, prefix=CONFIG.prefix)

    return app


def custom_openapi() -> "Dict[str, Any]":
    """Improve the default look & feel when rendering using ReDocs."""
    if _APP.openapi_schema:
        return _APP.openapi_schema

    _APP.openapi_schema = get_openapi(
        title=_APP.title,
        version=_APP.version,
        openapi_version=_APP.openapi_version,
        description=_APP.description,
        routes=_APP.routes,
        tags=_APP.openapi_tags,
        servers=_APP.servers,
    )
    _APP.openapi_schema["info"]["x-logo"] = {
        "url": "https://ontotrans.eu/wp-content/uploads/2020/05/ot_logo_rosa_gro%C3%9F.svg"
    }
    return _APP.openapi_schema


async def init_redis() -> None:
    """Initialize Redis upon app startup."""
    await redis_plugin.init_app(_APP, config=CONFIG)
    await redis_plugin.init()


async def terminate_redis() -> None:
    """Terminate Redis upon shutdown."""
    await redis_plugin.terminate()


CONFIG = AppSettings()
_APP = create_app()
_APP.openapi = custom_openapi

# Events
_APP.add_event_handler("startup", init_redis)
_APP.add_event_handler("shutdown", terminate_redis)
_APP.add_event_handler("startup", load_plugins)

"""OTE-API FastAPI application."""
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_plugins import RedisSettings, redis_plugin
from oteapi.plugins import load_plugins

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


PREFIX = "/api/v1"


class AppSettings(RedisSettings):
    """Redis settings."""

    api_name: str = "oteapi_services"


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
    for router_module in (session, dataresource, transformation, datafilter, mapping, redisadmin):
        app.include_router(router_module.router, prefix=f"{PREFIX}{router_module.router.prefix}")

    print("# Loading plugins")
    load_plugins()

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

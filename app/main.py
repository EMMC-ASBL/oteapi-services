"""OTE-API FastAPI application."""
import logging
from importlib import import_module
from typing import TYPE_CHECKING

from fastapi import Depends, FastAPI, status
from fastapi.openapi.utils import get_openapi
from fastapi_plugins import RedisSettings, redis_plugin
from oteapi.plugins import load_strategies
from pydantic import Field

from app import __version__
from app.models.error import HTTPValidationError
from app.routers import (
    datafilter,
    dataresource,
    function,
    mapping,
    redisadmin,
    session,
    transformation,
    triplestore,
)

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, List


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AppSettings(RedisSettings):
    """Redis settings."""

    AUTH_DEPENDENCIES: str = Field(
        "", description="List of FastAPI dependencies for authentication features."
    )

    api_name: str = Field(
        "oteapi_services", description="Application-specific name for Redis cache."
    )
    prefix: str = Field(
        f"/api/v{__version__.split('.', maxsplit=1)[0]}",
        description="Application route prefix.",
    )

    class Config:
        """OTE-API Services application configuration."""

        env_prefix = "OTEAPI_"


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    app = FastAPI(
        dependencies=get_auth_deps(),
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

This service is based on [**oteapi-core**](https://github.com/EMMC-ASBL/oteapi-core).
""",
    )
    for router_module in (
        session,
        dataresource,
        datafilter,
        function,
        mapping,
        transformation,
        redisadmin,
        triplestore,
    ):
        app.include_router(
            router_module.ROUTER,
            prefix=CONFIG.prefix,
            responses={
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "description": "Validation Error",
                    "model": HTTPValidationError,
                },
            },
        )

    return app


def get_auth_deps() -> "List[Depends]":
    """Get authentication dependencies

    Fetch dependencies for authentication through the
    `OTEAPI_AUTH_DEPS` environment variable.

    Returns:
        List of FastAPI dependencies with authentication functions.

    """
    if CONFIG.authentication_dependencies:
        modules = [
            module.strip().split(":")
            for module in CONFIG.authentication_dependencies.split("|")
        ]
        imports = [
            getattr(import_module(module), classname) for (module, classname) in modules
        ]
        logger.info(
            "Imported the following dependencies for authentication: %s", imports
        )
        dependencies = [Depends(dependency()) for dependency in imports]
    else:
        dependencies = []
        logger.info("No dependencies for authentication assigned.")
    return dependencies


def custom_openapi() -> "Dict[str, Any]":
    """Improve the default look & feel when rendering using ReDocs."""
    if APP.openapi_schema:
        return APP.openapi_schema

    APP.openapi_schema = get_openapi(
        title=APP.title,
        version=APP.version,
        openapi_version=APP.openapi_version,
        description=APP.description,
        routes=APP.routes,
        tags=APP.openapi_tags,
        servers=APP.servers,
    )
    APP.openapi_schema["info"]["x-logo"] = {
        "url": "https://ontotrans.eu/wp-content/uploads/2020/05/ot_logo_rosa_gro%C3%9F.svg"
    }
    return APP.openapi_schema


async def init_redis() -> None:
    """Initialize Redis upon app startup."""
    await redis_plugin.init_app(APP, config=CONFIG)
    await redis_plugin.init()


async def terminate_redis() -> None:
    """Terminate Redis upon shutdown."""
    await redis_plugin.terminate()


CONFIG = AppSettings()
APP = create_app()
APP.openapi = custom_openapi

# Events
APP.add_event_handler("startup", init_redis)
APP.add_event_handler("shutdown", terminate_redis)
APP.add_event_handler("startup", load_strategies)

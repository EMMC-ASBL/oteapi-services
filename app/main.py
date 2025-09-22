"""OTE-API FastAPI application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import Depends, FastAPI, status
from fastapi.openapi.utils import get_openapi
from oteapi.plugins import load_strategies

from app import __version__
from app.models.error import HTTPValidationError
from app.redis_cache import redis_plugin
from app.settings import get_settings

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator
    from typing import Any

    from fastapi import APIRouter


LOGGER = logging.getLogger(__name__)


def get_routers() -> Generator[APIRouter]:
    """Get all routers in the application."""
    routers_dir = (Path(__file__).parent / "routers").resolve()

    for entry in routers_dir.iterdir():
        if (
            entry.is_file() and entry.suffix == ".py" and not entry.stem.startswith("_")
        ) or (entry.is_dir() and (entry / "__init__.py").exists()):
            module = import_module(f"app.routers.{entry.stem}")
            yield module.ROUTER


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Server lifespan events.

    On startup:
    - Initialize the cache
    - Load OTEAPI strategies

    On shutdown:
    - Terminate the cache
    """
    settings = get_settings()

    # Initialize the Redis cache
    await redis_plugin.init_app(app, config=settings)
    await redis_plugin.init()

    # Load OTEAPI strategies
    load_strategies()

    # Run server
    yield

    # Terminate the Redis cache
    await redis_plugin.terminate()


def get_auth_deps() -> list[Depends]:
    """Get authentication dependencies

    Fetch dependencies for authentication through the
    `OTEAPI_AUTH_DEPS` environment variable.

    Returns:
        List of FastAPI dependencies with authentication functions.

    """
    settings = get_settings()

    if settings.authentication_dependencies:
        modules = [
            module.strip().split(":")
            for module in settings.authentication_dependencies.split("|")
        ]
        imports = [
            getattr(import_module(module), classname) for (module, classname) in modules
        ]
        LOGGER.info(
            "Imported the following dependencies for authentication: %s", imports
        )
        dependencies = [Depends(dependency) for dependency in imports]
    else:
        dependencies = []
        LOGGER.info("No dependencies for authentication assigned.")
    return dependencies


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    """Improve the default look & feel when rendering using ReDocs."""
    if app.openapi_schema:
        return app.openapi_schema

    app.openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )
    app.openapi_schema["info"]["x-logo"] = {
        "url": "https://ontotrans.eu/wp-content/uploads/2020/05/ot_logo_rosa_gro%C3%9F.svg"
    }
    return app.openapi_schema


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    auth_dependencies = get_auth_deps()
    settings = get_settings()

    app = FastAPI(
        dependencies=auth_dependencies,
        title="Open Translation Environment API",
        version=__version__,
        lifespan=lifespan,
        debug=settings.debug,
        root_path=settings.prefix,
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

    # Include all routers
    for router in get_routers():
        app.include_router(
            router,
            responses={
                status.HTTP_422_UNPROCESSABLE_CONTENT: {
                    "description": "Validation Error",
                    "model": HTTPValidationError,
                },
            },
        )

    # Customize the OpenAPI specficiation generation
    app.openapi = lambda: custom_openapi(app)

    return app

"""Admin APIs."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter

from app.settings import settings

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator


def get_routers() -> Generator[APIRouter]:
    """Get all routers in the admin directory."""
    admin_dir = Path(__file__).parent.resolve()

    for file_entry in admin_dir.iterdir():
        if (
            file_entry.is_file()
            and file_entry.suffix == ".py"
            and not file_entry.stem.startswith("_")
        ):
            module = import_module(f"app.routers.admin.{file_entry.stem}")
            yield module.ROUTER


ROUTER = APIRouter(
    prefix="/admin",
    tags=["admin"],
    include_in_schema=settings.debug,
)

for admin_router in get_routers():
    ROUTER.include_router(admin_router)

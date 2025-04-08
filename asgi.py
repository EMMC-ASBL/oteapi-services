"""ASGI application.

A server can bind `APP` in this file to their websocket.
"""

from __future__ import annotations

from app.logging import setup_logging
from app.main import create_app

__all__ = ("APP",)

setup_logging()
APP = create_app()

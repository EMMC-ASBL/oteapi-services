"""ASGI application.

A server can bind `app` in this file to their websocket.
"""

from app.main import APP as app

__all__ = ("app",)

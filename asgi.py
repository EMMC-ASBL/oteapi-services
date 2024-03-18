"""ASGI application.

A server can bind `app` in this file to their websocket.
"""

from app.main import create_app

__all__ = ("app",)

app = create_app()

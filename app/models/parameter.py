"""Session Model"""
from typing import Any, Dict

from pydantic import BaseModel


class Session(BaseModel):
    """Session Model."""

    __root__: Dict[str, Any]

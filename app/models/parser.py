"""Parser specific pydantic response models."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, GetResponse, InitializeResponse

IDPREFIX = "parser"


class CreateParserResponse(CreateResponse):
    """Create a response resource

    Router: `POST /parser`
    """

    parser_id: Annotated[
        str,
        Field(
            default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
            description="The parser id.",
            pattern=(
                rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
                r"[0-9a-f]{12}$"
            ),
        ),
    ]


class GetParserResponse(GetResponse):
    """Get a parser resource

    Router: `GET /parser/{parser_id}`
    """


class InitializeParserResponse(InitializeResponse):
    """Initialize a parser resource

    Router: `POST /parser/{parser_id}/initialize`
    """

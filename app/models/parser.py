"""Parser specific pydantic response models."""

from typing import Annotated
from uuid import uuid4

from oteapi.models import AttrDict
from pydantic import Field

from app.models.response import CreateResponse, GetResponse, InitializeResponse, Session

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


class DeleteAllParsersResponse(AttrDict):
    """### Delete all sessions

    Router: `DELETE /parser`
    """

    number_of_deleted_parsers: Annotated[
        int, Field(description="The number of deleted parsers in the Redis cache.")
    ]


class ListParsersResponse(Session):
    """List all parser ids

    Router: `GET /parser`
    """

    keys_: Annotated[
        list[str],
        Field(description="List of all parser ids in the cache.", alias="keys"),
    ]

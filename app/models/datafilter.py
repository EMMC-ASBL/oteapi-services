"""Data filter-specific pydantic response models."""

from typing import Annotated
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, GetResponse, InitializeResponse

IDPREFIX = "filter"


class CreateFilterResponse(CreateResponse):
    """### Create a data filter

    Router: `POST /filter`
    """

    filter_id: Annotated[
        str,
        Field(
            default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
            description="The filter id.",
            pattern=(
                rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
                r"[0-9a-f]{12}$"
            ),
        ),
    ]


class GetFilterResponse(GetResponse):
    """### Get a data filter

    Router: `GET /filter/{filter_id}`
    """


class InitializeFilterResponse(InitializeResponse):
    """### Initialize a data filter

    Router: `POST /filter/{filter_id}/initialize`
    """

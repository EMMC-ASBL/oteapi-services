"""Data resource-specific pydantic response models."""

from typing import Annotated
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, GetResponse, InitializeResponse

IDPREFIX = "dataresource"


class CreateResourceResponse(CreateResponse):
    """### Create a data resource

    Router: `POST /dataresource`
    """

    resource_id: Annotated[
        str,
        Field(
            default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
            description="The resource id.",
            pattern=(
                rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
                r"[0-9a-f]{12}$"
            ),
        ),
    ]


class GetResourceResponse(GetResponse):
    """### Get a data resource

    Router: `GET /dataresource/{resource_id}`
    """


class InitializeResourceResponse(InitializeResponse):
    """### Initialize a data resource

    Router: `POST /dataresource/{resource_id}/initialize`
    """

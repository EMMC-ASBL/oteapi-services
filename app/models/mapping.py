"""Mapping-specific pydantic response models."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, GetResponse, InitializeResponse

IDPREFIX = "mapping"


class CreateMappingResponse(CreateResponse):
    """### Create a mapping

    Router: `POST /mapping`
    """

    mapping_id: Annotated[
        str,
        Field(
            default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
            description="The mapping id.",
            pattern=(
                rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
                r"[0-9a-f]{12}$"
            ),
        ),
    ]


class GetMappingResponse(GetResponse):
    """### Get a mapping

    Router: `GET /mapping/{mapping_id}`
    """


class InitializeMappingResponse(InitializeResponse):
    """### Initialize a mapping

    Router: `POST /mapping/{mapping_id}/initialize`
    """

"""Transformation-specific pydantic response models."""

from typing import Annotated
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, GetResponse, InitializeResponse, Session

IDPREFIX = "transformation"


class CreateTransformationResponse(CreateResponse):
    """### Create a transformation

    Router: `POST /transformation`
    """

    transformation_id: Annotated[
        str,
        Field(
            default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
            description="The transformation id.",
            pattern=(
                rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
                r"[0-9a-f]{12}$"
            ),
        ),
    ]


class GetTransformationResponse(GetResponse):
    """### Get a transformation

    Router: `GET /transformation/{transformation_id}`
    """


class InitializeTransformationResponse(InitializeResponse):
    """### Initialize a transformation

    Router: `POST /transformation/{transformation_id}/initialize`
    """


class ExecuteTransformationResponse(Session):
    """### Execute (run) a transformation

    Router: `POST /transformation/{transformation_ud}/execute`
    """

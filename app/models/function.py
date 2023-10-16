"""Function-specific pydantic response models."""
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, GetResponse, InitializeResponse

IDPREFIX = "function"


class CreateFunctionResponse(CreateResponse):
    """### Create a function

    Router: `POST /function`
    """

    function_id: str = Field(
        default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
        description="The function id.",
        pattern=(
            rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
            r"[0-9a-f]{12}$"
        ),
    )


class GetFunctionResponse(GetResponse):
    """### Get a function

    Router: `GET /function/{function_id}`
    """


class InitializeFunctionResponse(InitializeResponse):
    """### Initialize a function

    Router: `POST /function/{function_id}/initialize`
    """

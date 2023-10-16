"""Session-specific pydantic response models."""
from typing import List
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, InitializeResponse, Session

IDPREFIX = "session"


class CreateSessionResponse(CreateResponse):
    """### Create a session

    Router: `POST /session`
    """

    session_id: str = Field(
        default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
        description="The session id.",
        pattern=(
            rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
            r"[0-9a-f]{12}$"
        ),
    )


class InitializeSessionResponse(InitializeResponse):
    """### Initialize a session

    Router: `POST /session/{session_id}/initialize`
    """


class ListSessionsResponse(Session):
    """### List all sessions

    Router: `GET /session`
    """

    keys_: List[str] = Field(
        ..., description="List of all session ids in the cache.", alias="keys"
    )


class DeleteAllSessionsResponse(Session):
    """### Delete all sessions

    Router: `DELETE /session`
    """

    number_of_deleted_sessions: int = Field(
        ..., description="The number of deleted sessions in the Redis cache."
    )


class DeleteSessionResponse(Session):
    """### Delete a session

    Router: `DELETE /session/{session_id}`
    """

    success: bool = Field(
        ..., description="Whether or not the session was successfully deleted."
    )

"""Session-specific pydantic response models."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from pydantic import Field

from app.models.response import CreateResponse, InitializeResponse, Session

IDPREFIX = "session"


class CreateSessionResponse(CreateResponse):
    """### Create a session

    Router: `POST /session`
    """

    session_id: Annotated[
        str,
        Field(
            default_factory=lambda: f"{IDPREFIX}-{uuid4()}",
            description="The session id.",
            pattern=(
                rf"^{IDPREFIX}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-"
                r"[0-9a-f]{12}$"
            ),
        ),
    ]


class InitializeSessionResponse(InitializeResponse):
    """### Initialize a session

    Router: `POST /session/{session_id}/initialize`
    """


class ListSessionsResponse(Session):
    """### List all sessions

    Router: `GET /session`
    """

    keys_: Annotated[
        list[str],
        Field(description="List of all session ids in the cache.", alias="keys"),
    ]


class DeleteAllSessionsResponse(Session):
    """### Delete all sessions

    Router: `DELETE /session`
    """

    number_of_deleted_sessions: Annotated[
        int, Field(description="The number of deleted sessions in the Redis cache.")
    ]
    message: Annotated[
        str | None,
        Field(
            description="Optional message indicating the result of the operation.",
        ),
    ] = "All session keys deleted."


class DeleteSessionResponse(Session):
    """### Delete a session

    Router: `DELETE /session/{session_id}`
    """

    success: Annotated[
        bool, Field(description="Whether or not the session was successfully deleted.")
    ]

"""Pydantic models for handling errors."""
from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """Validation Error response Model."""

    loc: List[str] = Field(..., title="Location")
    msg: str = Field(..., title="Message")
    type: str = Field(..., title="Error Type")


class HTTPValidationError(BaseModel):
    """HTTPValidation Error Response model."""

    detail: Optional[List[ValidationError]]


class HTTPNotFoundError(HTTPValidationError):
    """HTTPNotFound Error Response model."""


def httpexception_404_item_id_does_not_exist(
    item_id: str, item_name: str
) -> HTTPException:
    """return 404 Exception with session_id."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "loc": f"[{item_name}]",
                "msg": f"{item_name}={item_id} not found in server cache.",
                "type": "Error",
            }
        ],
    )


def httpexception_422_resource_id_is_unprocessable(resource_id: str) -> HTTPException:
    """return 422 Exception with resource_id."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=[
            {
                "loc": ["resource_id"],
                "msg": "Missing downloadUrl/mediaType or "
                f"accessUrl/accessService identifier in {resource_id=}",
                "type": "Error",
            }
        ],
    )

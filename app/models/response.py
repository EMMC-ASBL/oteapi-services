"""Pydantic response models."""
import re
from typing import TYPE_CHECKING

from oteapi.models import AttrDict
from pydantic import root_validator

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict


class Session(AttrDict):
    """Base session response model."""


class CreateResponse(Session):
    """Base `POST /` (create) response model.

    The subclasses of this model should _always_ contain a `*_id` attribute.
    """

    @root_validator(allow_reuse=True)
    def ensure_id_attribute(cls, values: "Dict[str, Any]") -> "Dict[str, Any]":
        """Ensure a `*_id` attribute exists."""
        if issubclass(cls, CreateResponse) and cls != CreateResponse:
            # `cls` is a subclass of `CreateResponse`
            if not any(re.match(r"^.+_id$", field) for field in values):
                raise AttributeError(
                    "A '*_id' attribute MUST be defined for a subclass of "
                    "`CreateResponse`."
                )
        return values


class GetResponse(Session):
    """Base `GET /{id}` response model."""


class InitializeResponse(Session):
    """Base `POST /{id}/initialize` response model."""

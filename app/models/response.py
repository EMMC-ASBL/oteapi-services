"""Pydantic response models."""
import re

from oteapi.models import AttrDict
from pydantic import model_validator


class Session(AttrDict):
    """Base session response model."""


class CreateResponse(Session):
    """Base `POST /` (create) response model.

    The subclasses of this model should _always_ contain a `*_id` attribute.
    """

    @model_validator(mode="after")
    def ensure_id_attribute(self) -> "CreateResponse":
        """Ensure a `*_id` attribute exists."""
        if (
            issubclass(self.__class__, CreateResponse)
            and self.__class__ != CreateResponse
        ):
            # Validating on a subclassed instance of `CreateResponse`
            if not any(re.match(r"^.+_id$", field) for field, _ in self):
                raise AttributeError(
                    "A '*_id' attribute MUST be defined for a subclass of "
                    "`CreateResponse`."
                )

        return self


class GetResponse(Session):
    """Base `GET /{id}` response model."""


class InitializeResponse(Session):
    """Base `POST /{id}/initialize` response model."""

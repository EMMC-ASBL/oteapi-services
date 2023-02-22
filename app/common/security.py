"""Utility functions and more to do with security and authentication.

This is based on the FastAPI documentation found at
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#hash-and-verify-the-passwords
"""
from typing import TYPE_CHECKING

from passlib.context import CryptContext
from pydantic import SecretBytes, SecretStr

if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional, Union

    from oteapi.models import FunctionConfig, ResourceConfig, TransformationConfig

    SecretStrategyConfig = Union[FunctionConfig, ResourceConfig, TransformationConfig]


CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_secret(
    secret: "Union[str, bytes]", hashed_secret: "Optional[Union[str, bytes]]" = None
) -> bool:
    """Verify a secret.

    Parameters:
        secret: Plain secret as bytes or string.
        hashed_secret: The hashed secret.

    Returns:
        Whether or not the secret is/can be verified.

    """
    return CRYPT_CONTEXT.verify(secret, hashed_secret)


def get_hash_value(secret: "Union[str, bytes]") -> str:
    """Hash secret.

    Parameters:
        secret: Plain secret as bytes or string to be hashed.

    Returns:
        The hashed secret.

    """
    return CRYPT_CONTEXT.hash(secret)


def hash_model_secrets(model: "SecretStrategyConfig") -> SecretStrategyConfig:
    """Hash any `pydantic.SecretStr` or `pydantic.SecretBytes` values in `model`.

    !!! note
        This does not hash nested `SecretStr` or `SecretBytes` values.

    !!! note
        If the field is of type `SecretBytes`, the hashed value will be stored with
        UTF-8 encoding.

    Parameters:
        model: Pydantic model to hash `SecretStr` or `SecretBytes` values within.

    Returns:
        The "treated" model.

    """
    for field, value in model:
        if value is not None:
            if isinstance(value, SecretStr):
                setattr(model, field, get_hash_value(value.get_secret_value()))
            elif isinstance(value, SecretBytes):
                setattr(
                    model,
                    field,
                    get_hash_value(value.get_secret_value()).encode("utf-8"),
                )
    return model

"""Demo function strategy class."""

from __future__ import annotations

from oteapi.models import AttrDict, FunctionConfig
from pydantic.dataclasses import dataclass


@dataclass
class DemoFunctionStrategy:
    """Function Strategy."""

    function_config: FunctionConfig

    def initialize(self) -> AttrDict:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTEAPI
        Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        return AttrDict()

    def get(self) -> AttrDict:
        """Execute the strategy.

        This method will be called through the strategy-specific endpoint of the
        OTEAPI Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        return AttrDict()

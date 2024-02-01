"""Demo function strategy class."""
from typing import TYPE_CHECKING

from oteapi.models import AttrDict, FunctionConfig
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Optional


@dataclass
class DemoFunctionStrategy:
    """Function Strategy.

    **Registers strategies**:

    - `("functionType", "function/DEMO")`

    """

    function_config: FunctionConfig

    def initialize(self, session: "Optional[dict[str, Any]]" = None) -> AttrDict:
        """Initialize strategy.

        This method will be called through the `/initialize` endpoint of the OTEAPI
        Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        del session  # unused
        del self.function_config  # unused

        return AttrDict()

    def get(self, session: "Optional[dict[str, Any]]" = None) -> AttrDict:
        """Execute the strategy.

        This method will be called through the strategy-specific endpoint of the
        OTEAPI Services.

        Parameters:
            session: A session-specific dictionary context.

        Returns:
            An update model of key/value-pairs to be stored in the
            session-specific context from services.

        """
        del session  # unused
        del self.function_config  # unused
        return AttrDict()

"""Demo mapping strategy class."""

from typing import TYPE_CHECKING

from oteapi.models.mappingconfig import MappingConfig
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Optional


@dataclass
class DemoMappingStrategy:
    """Mapping Strategy."""

    mapping_config: MappingConfig

    def initialize(
        self, session: "Optional[dict[str, Any]]" = None
    ) -> "dict[str, Any]":
        """Initialize mapping"""

        del session  # unused
        del self.mapping_config  # unused
        return {}

    def get(self, session: "Optional[dict[str, Any]]" = None) -> "dict[str, Any]":
        """Manage mapping and return shared map"""

        del session  # unused
        del self.mapping_config  # unused

        return {}

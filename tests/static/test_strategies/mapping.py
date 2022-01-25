"""Demo mapping strategy class."""
# pylint: disable=no-self-use,unused-argument
from dataclasses import dataclass
from typing import TYPE_CHECKING

from oteapi.plugins.factories import StrategyFactory

if TYPE_CHECKING:
    from typing import Any, Dict, Optional

    from oteapi.models.mappingconfig import MappingConfig


@dataclass
@StrategyFactory.register(("mappingType", "mapping/demo"))
class DemoMappingStrategy:
    """Mapping Strategy."""

    mapping_config: "MappingConfig"

    def initialize(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> "Dict[str, Any]":
        """Initialize mapping"""
        return {}

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> "Dict[str, Any]":
        """Manage mapping and return shared map"""
        return {}

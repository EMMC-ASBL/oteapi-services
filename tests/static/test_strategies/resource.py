"""Demo resource strategy class."""
# pylint: disable=no-self-use,unused-argument
from dataclasses import dataclass
from typing import TYPE_CHECKING

from oteapi.plugins.factories import StrategyFactory, create_download_strategy

if TYPE_CHECKING:
    from typing import Any, Dict, Optional

    from oteapi.models.resourceconfig import ResourceConfig


@dataclass
@StrategyFactory.register(("accessService", "demo-access-service"))
class DemoResourceStrategy:
    """Resource Strategy."""

    resource_config: "ResourceConfig"

    def initialize(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> "Dict[str, Any]":
        """Initialize"""
        return {}

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> "Dict[str, Any]":
        """Manage mapping and return shared map"""
        # Example of the plugin using the download strategy to fetch the data
        download_strategy = create_download_strategy(self.resource_config)
        read_output = download_strategy.get(session)
        return {"output": read_output}

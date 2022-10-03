"""Demo resource strategy class."""
from typing import TYPE_CHECKING

from oteapi.models.resourceconfig import ResourceConfig
from oteapi.plugins.factories import create_strategy
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


@dataclass
class DemoResourceStrategy:
    """Resource Strategy."""

    resource_config: ResourceConfig

    def initialize(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> "Dict[str, Any]":
        """Initialize"""
        del session  # fix ignore-unused-argument
        return self.resource_config

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> "Dict[str, Any]":
        """Manage mapping and return shared map"""
        # Example of the plugin using the download strategy to fetch the data
        download_strategy = create_strategy("download", self.resource_config)
        read_output = download_strategy.get(session)
        return {"output": read_output}

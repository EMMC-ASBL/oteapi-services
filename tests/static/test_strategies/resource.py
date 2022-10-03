"""Demo resource strategy class."""
from typing import TYPE_CHECKING

from oteapi.models.resourceconfig import ResourceConfig
from oteapi.models.sessionupdate import SessionUpdate
from oteapi.plugins.factories import create_strategy
from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


class ResourceResult(SessionUpdate):
    """Update session with the FilterResult model"""

    output: "Optional[str]" = Field(None, description="Optional result")


@dataclass
class DemoResourceStrategy:
    """Resource Strategy."""

    resource_config: ResourceConfig

    def initialize(self, session: "Optional[Dict[str, Any]]" = None) -> ResourceResult:
        """Initialize"""

        dummy = self.resource_config.deepcopy()
        del dummy
        del session
        return ResourceResult()

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> ResourceResult:
        """Manage mapping and return shared map"""
        # Example of the plugin using the download strategy to fetch the data
        download_strategy = create_strategy("download", self.resource_config)
        read_output = download_strategy.get(session)
        return ResourceResult(output=read_output)

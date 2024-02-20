"""Demo resource strategy class."""

from typing import TYPE_CHECKING, Annotated, Optional

from oteapi.models import AttrDict
from oteapi.models.resourceconfig import ResourceConfig
from oteapi.plugins.factories import create_strategy
from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any


class ResourceResult(AttrDict):
    """Update session with the FilterResult model"""

    output: Annotated[Optional[str], Field(description="Optional result")] = None


@dataclass
class DemoResourceStrategy:
    """Resource Strategy."""

    resource_config: ResourceConfig

    def initialize(self, session: "Optional[dict[str, Any]]" = None) -> ResourceResult:
        """Initialize"""

        del self.resource_config
        del session  # unused
        return ResourceResult()

    def get(self, session: "Optional[dict[str, Any]]" = None) -> ResourceResult:
        """Manage mapping and return shared map"""
        # Example of the plugin using the download strategy to fetch the data
        download_strategy = create_strategy("download", self.resource_config)
        read_output = download_strategy.get(session)
        return ResourceResult(output=read_output)

"""Demo strategy class for text/json."""
# pylint: disable=unused-argument
import json
from typing import TYPE_CHECKING

from oteapi.datacache.datacache import DataCache
from oteapi.models.resourceconfig import ResourceConfig
from oteapi.plugins.factories import create_strategy
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


@dataclass
class DemoJSONDataParseStrategy:
    """Parse Strategy."""

    resource_config: ResourceConfig

    def initialize(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> "Dict[str, Any]":
        """Initialize"""

        del session  # unused
        del self.resource_config  # unused
        return {}

    def parse(self, session: "Optional[Dict[str, Any]]" = None) -> "Dict[str, Any]":
        """Parse json."""
        downloader = create_strategy("download", self.resource_config)
        output = downloader.get()
        cache = DataCache(self.resource_config.configuration)
        content = cache.get(output["key"])

        if isinstance(content, dict):
            return content
        return json.loads(content)

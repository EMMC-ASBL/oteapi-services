"""Demo resource strategy class."""

from __future__ import annotations

from oteapi.models.resourceconfig import ResourceConfig
from pydantic.dataclasses import dataclass


@dataclass
class DemoResourceStrategy:
    """Resource Strategy."""

    resource_config: ResourceConfig

    def initialize(self) -> dict:
        """Initialize."""
        return {}

    def get(self) -> dict:
        """resource distribution."""
        return self.resource_config.model_dump()

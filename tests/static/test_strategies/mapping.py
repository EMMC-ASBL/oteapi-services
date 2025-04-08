"""Demo mapping strategy class."""

from __future__ import annotations

from oteapi.models import AttrDict
from oteapi.models.mappingconfig import MappingConfig
from pydantic.dataclasses import dataclass


@dataclass
class DemoMappingStrategy:
    """Mapping Strategy."""

    mapping_config: MappingConfig

    def initialize(self) -> AttrDict:
        """Initialize mapping"""
        return AttrDict()

    def get(self) -> AttrDict:
        """Manage mapping and return shared map"""
        return AttrDict()

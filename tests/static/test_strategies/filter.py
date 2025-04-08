"""Demo filter strategy."""

from __future__ import annotations

from typing import Annotated

from oteapi.models import AttrDict
from oteapi.models.filterconfig import FilterConfig
from pydantic import Field
from pydantic.dataclasses import dataclass


class DemoDataConfiguration(AttrDict):
    """Demo filter data model."""

    demo_data: Annotated[list[int], Field(description="List of demo data.")] = []


class DemoFilterConfig(FilterConfig):
    """Demo filter configuration."""

    configuration: DemoDataConfiguration = Field(
        ..., description=FilterConfig.model_fields["configuration"].description
    )


@dataclass
class DemoFilter:
    """Filter Strategy."""

    filter_config: DemoFilterConfig

    def initialize(self) -> AttrDict:
        """Initialize strategy and return a dictionary"""
        return AttrDict(result="collectionid")

    def get(self) -> AttrDict:
        """Execute strategy and return a dictionary"""
        return AttrDict(key=self.filter_config.configuration.demo_data)

"""Demo filter strategy."""
# pylint: disable=unused-argument
from typing import TYPE_CHECKING, List

from oteapi.models.filterconfig import FilterConfig
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


class DemoDataModel(BaseModel):
    """Demo filter data model."""

    demo_data: List[int] = Field([], description="List of demo data.")


@dataclass
class DemoFilter:
    """Filter Strategy."""

    filter_config: FilterConfig

    def initialize(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> "Dict[str, Any]":
        """Initialize strategy and return a dictionary"""
        return {"result": "collectionid"}

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> "Dict[str, List[int]]":
        """Execute strategy and return a dictionary"""
        model = DemoDataModel(**self.filter_config.configuration)
        return {"key": model.demo_data}

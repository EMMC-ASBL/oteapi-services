"""Demo filter strategy."""
from typing import TYPE_CHECKING, Annotated

from oteapi.models.filterconfig import FilterConfig
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Optional


class DemoDataModel(BaseModel):
    """Demo filter data model."""

    demo_data: Annotated[list[int], Field(description="List of demo data.")] = []


@dataclass
class DemoFilter:
    """Filter Strategy."""

    filter_config: FilterConfig

    def initialize(
        self, session: "Optional[dict[str, Any]]" = None
    ) -> "dict[str, Any]":
        """Initialize strategy and return a dictionary"""
        del session  # unused
        del self.filter_config  # unused

        return {"result": "collectionid"}

    def get(self, session: "Optional[dict[str, Any]]" = None) -> "dict[str, Any]":
        """Execute strategy and return a dictionary"""
        del session  # unused
        model = DemoDataModel(
            **self.filter_config.configuration  # pylint: disable=not-a-mapping
        )

        return {"key": model.demo_data}

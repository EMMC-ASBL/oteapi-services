
# pylint: disable=W0511, W0613
"""
Demo filter strategy
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from oteapi.models.filterconfig import FilterConfig
from oteapi.plugins.factories import StrategyFactory
from pydantic import BaseModel


class DemoDataModel(BaseModel):
    demoData: List[int]


@dataclass
@StrategyFactory.register(("filterType", "filter/demo"))
class DemoFilter:

    filter_config: FilterConfig

    def initialize(self, session: Optional[Dict[str, Any]] = None) -> Dict:
        """Initialize strategy and return a dictionary"""

        # TODO: Add logic
        return {"result": "collectionid"}

    def get(self, session: Optional[Dict[str, Any]] = None) -> Dict:
        """Execute strategy and return a dictionary"""

        model = DemoDataModel(**self.filter_config.configuration)
        return {"key": model.demoData}

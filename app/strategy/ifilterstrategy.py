"""
Resource Strategy Interface
"""

from typing import Protocol, Dict, Optional, Any
from dataclasses import dataclass
from app.models.filterconfig import FilterConfig
from app.strategy.factory import StrategyFactory


@dataclass
class IFilterStrategy(Protocol):
    """ Resource Interface """

    filter_config: FilterConfig

    def get(self, session: Optional[Dict[str, Any]] = None) -> Dict:
        """ Execute strategy and return a dictionary """

    def initialize(self, session: Optional[Dict[str, Any]] = None) -> Dict:
        """ Initialize strategy and return a dictionary """


def create_filter_strategy(filter_config: FilterConfig) -> IFilterStrategy:
    """ Helper function to simplify creating a filter strategy """
    return StrategyFactory.make_strategy(filter_config)

"""Demo transformation strategy class."""
# pylint: disable=no-self-use,unused-argument
from datetime import datetime
from typing import TYPE_CHECKING

from oteapi.models.transformationconfig import (
    TransformationConfig,
    TransformationStatus,
)
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


@dataclass
class DummyTransformationStrategy:
    """Transformation Strategy."""

    transformation_config: TransformationConfig

    def run(self, session: "Optional[Dict[str, Any]]" = None) -> "Dict[str, Any]":
        """Run a job, return a jobid"""
        return {"result": "a01d"}

    def initialize(
        self, session: "Optional[Dict[str, Any]]" = None
    ) -> "Dict[str, Any]":
        """Initialize a job"""
        return {"result": "collection id"}

    def status(self, task_id: str) -> TransformationStatus:
        """Get job status"""
        return TransformationStatus(
            id=task_id,
            status="wip",
            messages=[],
            created=datetime.utcnow(),
            startTime=datetime.utcnow(),
            finishTime=datetime.utcnow(),
        )

    def get(self, session: "Optional[Dict[str, Any]]" = None) -> "Dict[str, Any]":
        """get transformation"""
        return {}

"""Demo transformation strategy class."""

from datetime import datetime
from typing import TYPE_CHECKING

from oteapi.models.transformationconfig import (
    TransformationConfig,
    TransformationStatus,
)
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Optional


@dataclass
class DummyTransformationStrategy:
    """Transformation Strategy."""

    transformation_config: TransformationConfig

    def run(self, session: "Optional[dict[str, Any]]" = None) -> "dict[str, Any]":
        """Run a job, return a jobid"""
        del session
        del self.transformation_config
        return {"result": "a01d"}

    def initialize(
        self, session: "Optional[dict[str, Any]]" = None
    ) -> "dict[str, Any]":
        """Initialize a job"""
        del session
        del self.transformation_config

        return {"result": "collection id"}

    def status(self, task_id: str) -> TransformationStatus:
        """Get job status"""
        del self.transformation_config  # unused

        return TransformationStatus(
            id=task_id,
            status="wip",
            messages=[],
            created=datetime.utcnow(),
            startTime=datetime.utcnow(),
            finishTime=datetime.utcnow(),
        )

    def get(self, session: "Optional[dict[str, Any]]" = None) -> "dict[str, Any]":
        """get transformation"""
        del session  # unused
        del self.transformation_config  # unused
        return {}

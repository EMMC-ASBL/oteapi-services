"""Demo transformation strategy class."""

from datetime import datetime
from typing import TYPE_CHECKING

from oteapi.models import AttrDict
from oteapi.models.transformationconfig import (
    TransformationConfig,
    TransformationStatus,
)
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any


@dataclass
class DummyTransformationStrategy:
    """Transformation Strategy."""

    transformation_config: TransformationConfig

    def run(self) -> "dict[str, Any]":
        """Run a job, return a jobid"""
        return {"result": "a01d"}

    def initialize(self) -> "AttrDict":
        """Initialize a job"""
        return AttrDict(result="collection id")

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

    def get(self) -> "AttrDict":
        """get transformation"""
        return AttrDict()

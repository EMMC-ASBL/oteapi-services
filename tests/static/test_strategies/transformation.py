"""Demo transformation strategy class."""

from __future__ import annotations

import datetime
import sys
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

    def run(self) -> dict[str, Any]:
        """Run a job, return a jobid"""
        return {"result": "a01d"}

    def initialize(self) -> AttrDict:
        """Initialize a job"""
        return AttrDict(result="collection id")

    def status(self, task_id: str) -> TransformationStatus:
        """Get job status"""
        if sys.version_info < (3, 11):
            time_now = datetime.datetime.utcnow()
        else:
            time_now = datetime.datetime.now(datetime.UTC)

        return TransformationStatus(
            id=task_id,
            status="wip",
            messages=[],
            created=time_now,
            startTime=time_now,
            finishTime=time_now,
        )

    def get(self) -> AttrDict:
        """get transformation"""
        return AttrDict()

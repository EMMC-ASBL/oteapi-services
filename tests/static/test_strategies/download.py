"""Demo download strategy class for file."""

from typing import TYPE_CHECKING, Annotated, Optional

from oteapi.datacache.datacache import DataCache
from oteapi.models.resourceconfig import ResourceConfig
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any


class FileConfig(BaseModel):
    """File Specific Configuration"""

    text: Annotated[
        bool, Field(description="Whether the file should be opened in text mode.")
    ] = False

    encoding: Annotated[
        Optional[str],
        Field(
            description="Encoding used when opening the file.  "
            "Default is platform dependent.",
        ),
    ] = None


@dataclass
class FileStrategy:
    """Strategy for retrieving data via local file."""

    resource_config: ResourceConfig

    def initialize(
        self, session: "Optional[dict[str, Any]]" = None
    ) -> "dict[str, Any]":
        """Initialize"""
        del session
        del self.resource_config
        return {}

    def get(self, session: "Optional[dict[str, Any]]" = None) -> "dict[str, Any]":
        """Read local file."""
        del session  # fix ignore-unused-argument
        assert self.resource_config.downloadUrl
        assert (
            self.resource_config.downloadUrl.scheme  # pylint: disable=no-member
            == "file"
        )
        filename = self.resource_config.downloadUrl.host  # pylint: disable=no-member

        cache = DataCache(self.resource_config.configuration)
        if cache.config.accessKey and cache.config.accessKey in cache:
            key = cache.config.accessKey
        else:
            config = FileConfig(
                **self.resource_config.configuration,  # pylint: disable=not-a-mapping
                extra="ignore"
            )
            mode = "rt" if config.text else "rb"
            with open(filename, mode, encoding=config.encoding) as handle:
                key = cache.add(handle.read())

        return {"key": key}

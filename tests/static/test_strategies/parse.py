"""Demo strategy class for text/json."""

# pylint: disable=unused-argument
import json
from typing import TYPE_CHECKING, Literal, Optional

from oteapi.datacache import DataCache
from oteapi.datacache.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, HostlessAnyUrl, ParserConfig
from oteapi.plugins import create_strategy
from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any, Optional


class DEMOConfig(AttrDict):
    """JSON parse-specific Configuration Data Model."""

    downloadUrl: Optional[HostlessAnyUrl] = Field(
        None, description="The HTTP(S) URL, which will be downloaded."
    )
    mediaType: Optional[str] = Field(
        "application/json",
        description=("The media type"),
    )
    datacache_config: Optional[DataCacheConfig] = Field(
        None,
        description=(
            "Configurations for the data cache for storing the downloaded file "
            "content."
        ),
    )


class DEMOParserConfig(ParserConfig):
    """JSON parse strategy filter config."""

    parserType: Literal["parser/demo"] = Field(
        "parser/demo",
        description=ParserConfig.model_fields["parserType"].description,
    )
    configuration: DEMOConfig = Field(
        ..., description="JSON parse strategy-specific configuration."
    )


@dataclass
class DemoJSONDataParseStrategy:
    """Parse Strategy."""

    parse_config: DEMOParserConfig

    def initialize(self) -> "dict[str, Any]":
        """Initialize"""
        return {}

    def get(self) -> "dict[str, Any]":
        """Parse json."""
        downloader = create_strategy(
            "download", self.parse_config.configuration.model_dump()
        )
        output = downloader.get()
        cache = DataCache(self.parse_config.configuration.datacache_config)
        content = cache.get(output["key"])

        if isinstance(content, dict):
            return content
        return json.loads(content)

"""Demo strategy class for text/json."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from oteapi.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, HostlessAnyUrl, ParserConfig
from oteapi.plugins import create_strategy
from pydantic import Field
from pydantic.dataclasses import dataclass


class DEMOConfig(AttrDict):
    """JSON parse-specific Configuration Data Model."""

    downloadUrl: Annotated[
        HostlessAnyUrl | None,
        Field(description="The HTTP(S) URL, which will be downloaded."),
    ] = None
    mediaType: Annotated[
        Literal["application/json"] | None,
        Field(
            description=("The media type"),
        ),
    ] = "application/json"
    datacache_config: Annotated[
        DataCacheConfig | None,
        Field(
            description=(
                "Configurations for the data cache for storing the downloaded file "
                "content."
            ),
        ),
    ] = None


class DEMOParserConfig(ParserConfig):
    """JSON parse strategy filter config."""

    parserType: Annotated[
        Literal["parser/demo"],
        Field(
            description=ParserConfig.model_fields["parserType"].description,
        ),
    ] = "parser/demo"
    configuration: Annotated[
        DEMOConfig, Field(description="JSON parse strategy-specific configuration.")
    ]


@dataclass
class DemoJSONDataParseStrategy:
    """Parse Strategy."""

    parse_config: DEMOParserConfig

    def initialize(self) -> AttrDict:
        """Initialize"""
        return AttrDict()

    def get(self) -> AttrDict:
        """Parse json."""
        downloader = create_strategy(
            "download", self.parse_config.configuration.model_dump()
        )
        output = downloader.get()
        cache = DataCache(self.parse_config.configuration.datacache_config)
        content = cache.get(output["key"])

        if isinstance(content, dict):
            return AttrDict(**content)
        return AttrDict(**json.loads(content))

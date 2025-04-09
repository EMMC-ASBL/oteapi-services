"""Demo download strategy class for file."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from oteapi.datacache.datacache import DataCache
from oteapi.models import AttrDict, DataCacheConfig, ResourceConfig
from pydantic import AnyHttpUrl, BaseModel, Field
from pydantic.dataclasses import dataclass


class FileConfig(BaseModel):
    """File Specific Configuration"""

    text: Annotated[
        bool, Field(description="Whether the file should be opened in text mode.")
    ] = False

    encoding: Annotated[
        str | None,
        Field(
            description="Encoding used when opening the file.  "
            "Default is platform dependent.",
        ),
    ] = None


@dataclass
class FileStrategy:
    """Strategy for retrieving data via local file."""

    resource_config: ResourceConfig

    def initialize(self) -> AttrDict:
        """Initialize"""
        return AttrDict()

    def get(self) -> AttrDict:
        """Read local file."""
        assert self.resource_config.downloadUrl
        assert self.resource_config.downloadUrl.scheme == "file"
        filename = self.resource_config.downloadUrl.host

        cache = DataCache(self.resource_config.configuration)
        if cache.config.accessKey and cache.config.accessKey in cache:
            key = cache.config.accessKey
        else:
            config = FileConfig(
                **self.resource_config.configuration,
                extra="ignore",
            )
            mode = "rt" if config.text else "rb"
            with Path(filename).open(mode, encoding=config.encoding) as handle:
                key = cache.add(handle.read())

        return AttrDict(key=key)


class HTTPSConfig(AttrDict):
    """HTTP(S)-specific Configuration Data Model."""

    datacache_config: Annotated[
        DataCacheConfig | None,
        Field(
            description=(
                "Configurations for the data cache for storing the downloaded file "
                "content."
            ),
        ),
    ] = None


class HTTPSDemoConfig(ResourceConfig):
    """HTTP(S) download strategy filter config."""

    downloadUrl: Annotated[
        AnyHttpUrl, Field(description="The HTTP(S) URL, which will be downloaded.")
    ]
    configuration: Annotated[
        HTTPSConfig,
        Field(description="HTTP(S) download strategy-specific configuration."),
    ] = HTTPSConfig()


class HTTPDownloadContent(AttrDict):
    """Class for returning values from Download HTTPS strategy."""

    key: Annotated[str, Field(description="Key to access the data in the cache.")]


@dataclass
class HTTPSStrategy:
    """Strategy for retrieving data via http."""

    download_config: HTTPSDemoConfig

    def initialize(self) -> AttrDict:
        """Initialize."""
        return AttrDict()

    def get(self) -> HTTPDownloadContent:
        """Download via http/https and store on local cache."""
        cache = DataCache(self.download_config.configuration.datacache_config)
        if cache.config.accessKey and cache.config.accessKey in cache:
            key = cache.config.accessKey
        else:
            key = cache.add({"dummy_content": "dummycontent"})

        return HTTPDownloadContent(key=key)

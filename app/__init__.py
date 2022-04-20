"""OTE-API Services.

This repository contains the OTE-API server application.
The server should be deployed via the `Dockerfile`.
"""
import datetime as dt
from pathlib import Path
from typing import TYPE_CHECKING

from dulwich.repo import Repo

if TYPE_CHECKING:  # pragma: no cover
    from dulwich.objects import Commit


_CACHED_VERSION = None


def _get_version(api_version: str = "1", default_branch: str = "origin/master") -> str:
    """Compile OTEAPI Services version.

    The version syntax and semantics are laid out in the GitHub issue #71:
    https://github.com/EMMC-ASBL/oteapi-services/issues/71.

    Returns:
        The compiled version for the OTEAPI Services.

    """
    global _CACHED_VERSION  # pylint: disable=global-statement
    if not _CACHED_VERSION:
        repo_path = Path(__file__).resolve().parent.parent.resolve()
        repo = Repo(repo_path)
        default_branch_sha = repo.get_refs()[
            f"refs/remotes/{default_branch}".encode("utf-8")
        ]

        head_master: "Commit" = repo.get_object(default_branch_sha)
        head_master_time = dt.datetime.fromtimestamp(
            head_master.commit_time,
            dt.timezone(dt.timedelta(seconds=head_master.commit_timezone)),
        )
        calver = head_master_time.astimezone(dt.timezone.utc).strftime("%Y%m%d")

        build_number = len(list(repo.get_walker(default_branch_sha)))

        _CACHED_VERSION = f"{api_version}.{calver}.{build_number}"
    return _CACHED_VERSION


__version__ = _get_version()
__author__ = "SINTEF"
__author_email__ = "Team4.0@SINTEF.no"

"""Repository management tasks powered by `invoke`.

More information on `invoke` can be found at http://www.pyinvoke.org/.
"""
# pylint: disable=import-outside-toplevel
import datetime as dt
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from invoke import task

if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional, Tuple

    from dulwich.objects import Commit


TOP_DIR = Path(__file__).parent.resolve()


def update_file(
    filename: Path, sub_line: "Tuple[str, str]", strip: "Optional[str]" = None
) -> None:
    """Utility function for tasks to read, update, and write files.

    Parameters:
        filename: The file to read, update, and write to.
        sub_line: A tuple of first, what to look for and secondly, what to replace with.
        strip: What to strip from the right end of the line in the file.

    """
    lines = [
        re.sub(sub_line[0], sub_line[1], line.rstrip(strip))
        for line in filename.read_text(encoding="utf8").splitlines()
    ]
    filename.write_text("\n".join(lines) + "\n", encoding="utf8")


def compile_version(
    api_version: str = "1", default_branch: str = "origin/master"
) -> str:
    """Compile OTEAPI Services version.

    The version syntax and semantics are laid out in the GitHub issue #71:
    https://github.com/EMMC-ASBL/oteapi-services/issues/71.

    Parameters:
        api_version: The API version.
        default_branch: The default branch to determine the build number from.
            This is to be given as `<REMOTE>/<BRANCH NAME>`, e.g., `origin/main`.

    Returns:
        The compiled version for the OTEAPI Services.

    """
    from dulwich.repo import Repo

    repo = Repo(TOP_DIR)
    for ref in [
        f"refs/remotes/{default_branch}".encode("utf-8"),
        b"refs/remotes/origin/master",
        b"refs/remotes/origin/main",
    ]:
        if ref in repo.get_refs():
            default_branch_sha = repo.get_refs()[ref]
            break
    else:
        sys.exit(
            "Error: Expected a valid ref in the git repo ! Did this run via "
            "`invoke setver`?"
        )

    head_master: "Commit" = repo.get_object(default_branch_sha)
    head_master_time = dt.datetime.fromtimestamp(
        head_master.commit_time,
        dt.timezone(dt.timedelta(seconds=head_master.commit_timezone)),
    )
    calver = head_master_time.astimezone(dt.timezone.utc).strftime("%Y%m%d")

    build_number = len(list(repo.get_walker(default_branch_sha)))

    return f"{api_version}.{calver}.{build_number}"


def dir_is_git(default_branch: str = "origin/master") -> bool:
    """Validate the repository with regards to using `git` and compiling the
    version.

    Parameters:
        default_branch: The default branch to determine the build number from.
            This is to be given as `<REMOTE>/<BRANCH NAME>`, e.g., `origin/main`.

    Returns:
        Whether or not the repository is a valid `git` repository and the OTEAPI
        Services version is expected to be compiled properly.

    """
    from dulwich import porcelain
    from dulwich.errors import NotGitRepository
    from dulwich.repo import Repo

    try:
        repo = Repo(TOP_DIR)
    except NotGitRepository:
        return False

    with open(os.devnull, "wb") as handle:
        porcelain.fetch(repo, outstream=handle, errstream=handle)

    return any(
        ref in repo.get_refs()
        for ref in [
            f"refs/remotes/{default_branch}".encode("utf-8"),
            b"refs/remotes/origin/master",
            b"refs/remotes/origin/main",
        ]
    )


@task(help={"ver": "OTEAPI Services version to set."})
def setver(_, ver=""):
    """Sets the OTEAPI Services version."""
    if os.getenv("CI", "false") != "true":
        sys.exit("This invoke task should only be run as part of a CI/CD workflow.")

    if ver:
        match = re.fullmatch(
            (
                r"v?(?P<version>[1-9]+[0-9]*"  # API version
                r"\.20[0-9]{2}[0-1][0-9][0-3][0-9]"  # CalVer (YYYY0M0D)
                r"\.[0-9]+)"  # Build number
            ),
            ver,
        )
        if not match:
            sys.exit(
                "Error: Please specify version as "
                "'<API version>.<CalVer (YYYY0M0D)>.<Build number>' or "
                "'v<API version>.<CalVer (YYYY0M0D)>.<Build number>'."
            )
        ver = match.group("version")
    else:
        if dir_is_git(default_branch="origin/master"):
            ver = compile_version(
                api_version="1",
                default_branch="origin/master",
            )
        else:
            sys.exit(
                "Could not set version. No version is provided using the `--ver` "
                "option. Nor can the `master` remote branch be properly accessed in "
                "the repository folder. Is this a git repository?"
            )

    update_file(
        TOP_DIR / "app" / "__init__.py",
        (r'__version__ = (\'|").*(\'|")', f'__version__ = "{ver}"'),
    )

    print(f"Bumped version to {ver}.")

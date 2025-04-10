"""Repository management tasks powered by `invoke`.

More information on `invoke` can be found at http://www.pyinvoke.org/.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from invoke import UnexpectedExit, task

if TYPE_CHECKING:
    from invoke import Context


TOP_DIR = Path(__file__).parent.resolve()
DEFAULT_BRANCH = "origin/master"


def update_file(
    filename: Path, sub_line: tuple[str, str], strip: str | None = None
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
    context: Context,
    api_version: str | None = None,
    remote_branch: str | None = None,
    debug: bool = False,
) -> str:
    """Compile OTEAPI Services version.

    The version syntax and semantics are laid out in the GitHub issue #71:
    https://github.com/EMMC-ASBL/oteapi-services/issues/71.

    Parameters:
        context: The `invoke` context.
        api_version: The API version.
        remote_branch: The remote branch to determine the build number from.
            This is to be given as `<REMOTE>/<BRANCH NAME>`, e.g., `origin/main`.
        debug: Whether to run in debug mode.

    Returns:
        The compiled version for the OTEAPI Services.

    """
    api_version = api_version or "1"
    remote_branch = remote_branch or DEFAULT_BRANCH

    general_error_msg = (
        "Error: Expected a valid ref in the git repo !\n"
        "Did this run via `invoke setver`?"
    )

    # Create a refname to sha mapping for all remote refs
    try:
        result = context.run(
            'git for-each-ref --format="%(refname) %(objectname) %(creatordate:short)" '
            "refs/remotes/",
            hide=True,
        )
    except UnexpectedExit as err:
        if debug:
            print(
                f"Error: Could not list remote refs.\n{err}",
                file=sys.stderr,
                flush=True,
            )
        sys.exit(general_error_msg)
    if debug:
        print(f"GET REMOTE REFS ... stdout:\n{result.stdout}", flush=True)

    ref_to_sha_mapping: dict[str, str] = {}
    ref_to_date_mapping: dict[str, dt.datetime] = {}
    for remote_ref in result.stdout.splitlines():
        ref, sha, date = remote_ref.split()
        ref_to_sha_mapping[ref] = sha
        ref_to_date_mapping[ref] = dt.datetime.strptime(date, "%Y-%m-%d")
    if debug:
        print(f"ref_to_sha_mapping: {ref_to_sha_mapping}", flush=True)
        print(f"ref_to_date_mapping: {ref_to_date_mapping}", flush=True)

    # Determine the ref to use
    chosen_ref = f"refs/remotes/{remote_branch}"
    if chosen_ref not in ref_to_sha_mapping:
        if debug:
            print(
                "Error: Could not find a valid ref in the git repo.\n"
                f"ref_to_sha_mapping: {ref_to_sha_mapping}\nref_to_date_mapping: "
                f"{ref_to_date_mapping}",
                file=sys.stderr,
                flush=True,
            )
        sys.exit(general_error_msg)

    # Get the calender version
    calver = ref_to_date_mapping[chosen_ref].strftime("%Y%m%d")

    # Get the build number (number of commits up to the chosen ref from the initial
    # commit)
    try:
        result = context.run(
            f"git rev-list --count {ref_to_sha_mapping[chosen_ref]}", hide=True
        )
    except UnexpectedExit as err:
        if debug:
            print(
                f"Error: Could not determine the build number.\n{err}",
                file=sys.stderr,
                flush=True,
            )
        sys.exit(general_error_msg)
    if debug:
        print(f"GET BUILD NUMBER ... stdout:\n{result.stdout}", flush=True)

    build_number = result.stdout.strip()

    return f"{api_version}.{calver}.{build_number}"


def dir_is_git(
    context: Context, remote_branch: str | None = None, debug: bool = False
) -> bool:
    """Validate the repository with regards to using `git` and compiling the
    version.

    Parameters:
        context: The `invoke` context.
        remote_branch: The remote branch to determine the build number from.
            This is to be given as `<REMOTE>/<BRANCH NAME>`, e.g., `origin/main`.
        debug: Whether to run in debug mode.

    Returns:
        Whether or not the repository is a valid `git` repository and the OTEAPI
        Services version is expected to be compiled properly.

    """
    remote_branch = remote_branch or DEFAULT_BRANCH

    # Ensure we are running from the root of or within the repository
    if Path(context.cwd).resolve() != TOP_DIR or not Path(
        context.cwd
    ).resolve().is_relative_to(TOP_DIR):
        if debug:
            print(
                "Error: Please run this task from the root of or within the "
                "repository.",
                file=sys.stderr,
                flush=True,
            )
        return False
    if debug:
        print(
            "Determined current working directory to be the root of or within the "
            f"repository: {Path(context.cwd).resolve()}",
            flush=True,
        )

    # Possibly update the remote URL
    custom_remote_url = os.getenv("REMOTE_URL")
    if custom_remote_url:
        remote_name = remote_branch.split("/", maxsplit=1)[0]
        try:
            context.run(
                f"git remote set-url {remote_name} {custom_remote_url}", hide=True
            )
        except UnexpectedExit as err:
            if debug:
                print(
                    f"Error: Could not set the remote URL to REMOTE_URL value.\n{err}",
                    file=sys.stderr,
                    flush=True,
                )
            return False
        if debug:
            print("Set the remote URL to REMOTE_URL value.", flush=True)

    # Fetch from all remotes
    try:
        context.run("git fetch --all", hide=True)
    except UnexpectedExit as err:
        if debug:
            print(
                f"Error: Could not fetch from all remotes.\n{err}",
                file=sys.stderr,
                flush=True,
            )
        return False
    if debug:
        print("Fetched from all remotes.", flush=True)

    # Check and return bool for whether the remote branch is available or not
    try:
        result = context.run(
            "git for-each-ref --format='%(refname)' refs/remotes/", hide=True
        )
    except UnexpectedExit as err:
        if debug:
            print(
                f"Error: Could not list remote branches.\n{err}",
                file=sys.stderr,
                flush=True,
            )
        return False
    if debug:
        print(f"GET REMOTE BRANCHES ... stdout:\n{result.stdout}", flush=True)

    return f"refs/remotes/{remote_branch}" in result.stdout.splitlines()


def git_available(context: Context) -> bool:
    """Check if `git` is available on the system.

    Returns:
        Whether or not `git` is available on the system.

    """
    try:
        context.run("git --version", hide=True)
    except UnexpectedExit:
        return False
    return True


@task(
    help={
        "ver": "OTEAPI Services version to set.",
        "remote_branch": (
            "Remote branch to set version from. Should be of the form "
            "'<remote>/<branch_name>', e.g., 'origin/main'."
        ),
        "debug": "Whether to run in debug mode.",
    }
)
def setver(c, ver="", remote_branch=DEFAULT_BRANCH, debug=False):
    """Sets the OTEAPI Services version.

    The URL of the remote can be updated by setting the environment variable
    `REMOTE_URL` to the desired URL. This is useful if extra credentials are needed.
    """
    if TYPE_CHECKING:
        c: Context  # type: ignore[no-redef]
        ver: str  # type: ignore[no-redef]
        remote_branch: str  # type: ignore[no-redef]

    CI = os.getenv("CI")
    if CI is None or CI.lower() in ("0", "false"):
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
        if not git_available(context=c):
            sys.exit(
                "Could not set version. No version is provided using the '--ver' "
                "option. Git is not available on the system."
            )

        if dir_is_git(context=c, remote_branch=remote_branch, debug=debug):
            ver = compile_version(
                context=c,
                api_version="1",
                remote_branch=remote_branch,
                debug=debug,
            )
        else:
            sys.exit(
                "Could not set version. No version is provided using the '--ver' "
                f"option. Nor can the {remote_branch!r} remote branch be properly "
                "accessed in the repository folder. Is this a git repository?"
            )

    update_file(
        TOP_DIR / "app" / "__init__.py",
        (r'__version__ = (\'|").*(\'|")', f'__version__ = "{ver}"'),
    )

    print(f"Bumped version to {ver}.")

"""
Reader of the declaration of a project, `hodegos.yml`, which lists the folders searched besides the
accepted places.

Constants
---------
FORMAT
    Format identifier read by this release.
DECLARATION_PLACES
    Places of the declaration below a folder.

Functions
---------
read_declared_folders(folder)
    Return the folders declared by the declaration of a folder, or none.
"""

from __future__ import annotations

from pathlib import PurePosixPath, Path
from typing import Any

import yaml

from hodegos.errors import DiscoveryError, ErrorCode

FORMAT_KEY = "_schema"
"""Key holding the format identifier of the declaration."""

FORMAT = "hodegos:configuration@1"
"""Format identifier of `hodegos.yml` read by this release."""

FOLDERS_KEY = "folders"
"""Key listing the declared folders."""

DECLARATION_PLACES = (PurePosixPath("hodegos.yml"), PurePosixPath(".config/hodegos.yml"))
"""Places of the declaration below a folder. At most one of them may hold a file."""


def read_declared_folders(folder: Path) -> tuple[PurePosixPath, ...]:
    """
    Return the folders declared below `folder` by its declaration.

    Parameters
    ----------
    folder : Path
        Folder whose declaration is read.

    Returns
    -------
    tuple[PurePosixPath, ...]
        Declared folders, relative to `folder`, in their declared order; empty without a
        declaration.

    Raises
    ------
    DiscoveryError
        With the code `competing-declarations` when both places hold a file, and
        `invalid-declaration` when the file does not parse or departs from its format.
    """
    found = [folder / place for place in DECLARATION_PLACES if (folder / place).is_file()]
    if len(found) > 1:
        raise DiscoveryError(
            ErrorCode.COMPETING_DECLARATIONS,
            "two declarations compete: " + " and ".join(map(str, found)) + "; keep one",
        )
    if not found:
        return ()
    return _parse(found[0])


def _parse(path: Path) -> tuple[PurePosixPath, ...]:
    """Parse one declaration and return its folders, or raise naming the departure."""
    try:
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, ValueError) as error:
        raise _invalid(path, f"cannot be read: {error}") from error
    if not isinstance(raw, dict):
        raise _invalid(path, "must hold a mapping")
    unknown = sorted(str(key) for key in raw if key not in (FORMAT_KEY, FOLDERS_KEY))
    if unknown:
        raise _invalid(
            path,
            "declares unknown keys: " + ", ".join(unknown) + "; "
            f"admitted keys: {FORMAT_KEY}, {FOLDERS_KEY}",
        )
    if raw.get(FORMAT_KEY) != FORMAT:
        raise _invalid(path, f"must declare {FORMAT_KEY}: {FORMAT}")
    folders = raw.get(FOLDERS_KEY)
    if folders is None:
        return ()
    if not isinstance(folders, list):
        raise _invalid(path, f"{FOLDERS_KEY} must be a list of folders")
    return tuple(_folder(path, item) for item in folders)


def _folder(path: Path, item: Any) -> PurePosixPath:
    """Return one declared folder, or raise unless it is a relative path below the declaration."""
    if not isinstance(item, str):
        raise _invalid(path, f"declared folder {item!r} must be a string")
    text = item.rstrip("/")
    segments = text.split("/")
    if (
        not text
        or item.startswith("/")
        or "\\" in text
        or any(segment in ("", ".", "..") for segment in segments)
    ):
        raise _invalid(
            path,
            f"declared folder {item!r} must be a non-empty path below the folder of the "
            "declaration, with no segment '.' or '..'",
        )
    return PurePosixPath(text)


def _invalid(path: Path, reason: str) -> DiscoveryError:
    """Build the error of an invalid declaration."""
    return DiscoveryError(ErrorCode.INVALID_DECLARATION, f"{path}: {reason}")

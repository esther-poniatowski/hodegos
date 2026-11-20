"""
Discovery of the root of a project and of the configuration of a tool.

Classes
-------
Location
    Configuration found for a tool: its file, and its table when the file is `pyproject.toml`.
Discovery
    Root of a command and the configuration that it reads.

Functions
---------
discover(tool, *, root, config, start, cwd, environ, files)
    Resolve the root of a command and locate the configuration of the tool.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from hodegos.errors import DiscoveryError, ErrorCode
from hodegos.file_system import FileSystem, LocalFileSystem
from hodegos.tool import Tool

PYPROJECT = "pyproject.toml"
"""Name of the file of a Python project, whose table `[tool.<name>]` may hold a configuration."""

CONFIG_FOLDERS = (".config", "config")
"""Subfolders holding the file of a tool, searched after the folder itself and in this order."""


@dataclass(frozen=True)
class Location:
    """
    Configuration found for a tool.

    Attributes
    ----------
    path : Path
        File holding the configuration.
    table : Mapping[str, Any] | None
        Content of the table `[tool.<name>]` when `path` is a `pyproject.toml`, else None: the tool
        parses any other file itself.
    """

    path: Path
    table: Mapping[str, Any] | None = field(default=None)


@dataclass(frozen=True)
class Discovery:
    """
    Root of a command and the configuration that it reads.

    Attributes
    ----------
    root : Path
        Absolute root of the command.
    configuration : Location | None
        Configuration of the tool, or None when no place holds one; the tool then decides whether
        to run on its defaults or to stop.
    """

    root: Path
    configuration: Location | None


# The keyword arguments mirror the options of a command, so their count follows the command.
def discover(  # pylint: disable=too-many-arguments
    tool: Tool,
    *,
    root: Path | None = None,
    config: Path | None = None,
    start: Path | None = None,
    cwd: Path | None = None,
    environ: Mapping[str, str] | None = None,
    files: FileSystem | None = None,
) -> Discovery:
    """
    Resolve the root of a command and locate the configuration of the tool.

    The root is the first answer of:

    1. `root`, the value of the root option;
    2. the variable `<NAME>_ROOT`, when set and not empty;
    3. the nearest folder, from `start` upward, holding a configuration of the tool in one of its
       places; the outermost such folder for a stacked tool;
    4. the current folder.

    The configuration is the file named by `config`, else the single place of the root holding
    one. The places of a folder are the file `<name>.<extension>`, the same file in `.config/`, the
    same file in `config/`, and the table `[tool.<name>]` of `pyproject.toml` for a tool that reads
    it.

    Parameters
    ----------
    tool : Tool
        Convention of the tool.
    root : Path, optional
        Value of the root option, relative to the current folder.
    config : Path, optional
        Value of the configuration option, relative to the current folder.
    start : Path, optional
        Folder where the search of the root begins, relative to the current folder, such as the
        folder of a source file. Default: the current folder. The start changes the search only:
        `root`, `config` and the variable keep resolving against the current folder. The current
        folder also stays the root when the search finds none.
    cwd : Path, optional
        Current folder. Default: the working folder of the process.
    environ : Mapping[str, str], optional
        Environment variables. Default: `os.environ`.
    files : FileSystem, optional
        Port through which every file is read. Default: `LocalFileSystem()`, the local file
        system.

    Returns
    -------
    Discovery
        Root and configuration. Every path is absolute and normalized lexically, without
        resolving symbolic links.

    Raises
    ------
    DiscoveryError
        With the code `missing-config` when `config` names no file, `competing-places` when two
        places of the root hold a configuration, and `invalid-pyproject` for a `pyproject.toml`
        that does not parse.
    """
    current = _normalize(cwd if cwd is not None else Path.cwd())
    variables = os.environ if environ is None else environ
    reader = LocalFileSystem() if files is None else files
    resolved_root = _given_root(tool, root, current, variables)
    if resolved_root is None:
        begin = current if start is None else _normalize(current / start)
        resolved_root = _searched_root(tool, begin, reader) or current
    if config is not None:
        given = _normalize(current / config)
        if not reader.is_file(given):
            raise DiscoveryError(
                ErrorCode.MISSING_CONFIG, f"no configuration file at {given}, named by option"
            )
        return Discovery(resolved_root, Location(given))
    found = _locations(tool, resolved_root, reader)
    if len(found) > 1:
        raise DiscoveryError(
            ErrorCode.COMPETING_PLACES,
            f"two places hold a configuration of {tool.name}: "
            + " and ".join(str(location.path) for location in found)
            + "; keep one",
        )
    return Discovery(resolved_root, found[0] if found else None)


def _given_root(
    tool: Tool, root: Path | None, current: Path, variables: Mapping[str, str]
) -> Path | None:
    """Return the root named by the option or by the variable, resolved against `current`."""
    if root is not None:
        return _normalize(current / root)
    variable = variables.get(tool.variable, "")
    return _normalize(current / variable) if variable else None


def _searched_root(tool: Tool, begin: Path, files: FileSystem) -> Path | None:
    """Return the folder holding a configuration found from `begin` upward, or None."""
    outermost: Path | None = None
    for folder in (begin, *begin.parents):
        if _locations(tool, folder, files):
            if not tool.stacked:
                return folder
            outermost = folder
    return outermost


def _locations(tool: Tool, folder: Path, files: FileSystem) -> list[Location]:
    """Return every place of `folder` holding a configuration of the tool, in search order."""
    bases = [folder, *(folder / subfolder for subfolder in CONFIG_FOLDERS)]
    found = [
        Location(base / name)
        for base in bases
        for name in tool.file_names
        if files.is_file(base / name)
    ]
    if tool.pyproject:
        table = _pyproject_table(tool, folder / PYPROJECT, files)
        if table is not None:
            found.append(Location(folder / PYPROJECT, table))
    return found


def _pyproject_table(tool: Tool, path: Path, files: FileSystem) -> Mapping[str, Any] | None:
    """Return the table `[tool.<name>]` of a `pyproject.toml`, or None when either is absent."""
    if not files.is_file(path):
        return None
    try:
        document = tomllib.loads(files.read_text(path))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise DiscoveryError(ErrorCode.INVALID_PYPROJECT, f"{path}: {error}") from error
    section = document.get("tool")
    if not isinstance(section, dict):
        return None
    table = section.get(tool.name)
    return table if isinstance(table, dict) else None


def _normalize(path: Path) -> Path:
    """Return `path` made absolute and normalized lexically, as both implementations do."""
    return Path(os.path.normpath(path.absolute()))

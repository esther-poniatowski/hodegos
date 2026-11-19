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
discover(tool, *, root, config, cwd, environ)
    Resolve the root of a command and locate the configuration of the tool.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from hodegos.declaration import read_declared_folders
from hodegos.errors import DiscoveryError, ErrorCode
from hodegos.tool import Tool

PYPROJECT = "pyproject.toml"
"""Name of the file of a Python project, whose table `[tool.<name>]` may hold a configuration."""

DOT_CONFIG = ".config"
"""Folder of the configuration files of a project, an accepted place besides its root."""


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


def discover(
    tool: Tool,
    *,
    root: Path | None = None,
    config: Path | None = None,
    cwd: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Discovery:
    """
    Resolve the root of a command and locate the configuration of the tool.

    The root is the first answer of:

    1. `root`, the value of the root option;
    2. the variable `<NAME>_ROOT`, when set and not empty;
    3. the nearest folder, from the current folder upward, holding a configuration of the tool in
       one of its places; the outermost such folder for a stacked tool;
    4. the current folder.

    The configuration is the file named by `config`, else the single place of the root holding
    one. The places of a folder are the file `<name>.<extension>`, the same file in `.config/`, the
    same file in each folder listed by the declaration `hodegos.yml` of the folder, and the table
    `[tool.<name>]` of `pyproject.toml` for a tool that reads it.

    Parameters
    ----------
    tool : Tool
        Convention of the tool.
    root : Path, optional
        Value of the root option, relative to the current folder.
    config : Path, optional
        Value of the configuration option, relative to the current folder.
    cwd : Path, optional
        Current folder. Default: the working folder of the process.
    environ : Mapping[str, str], optional
        Environment variables. Default: `os.environ`.

    Returns
    -------
    Discovery
        Root and configuration. Every path is absolute and normalized lexically, without
        resolving symbolic links.

    Raises
    ------
    DiscoveryError
        With the code `missing-config` when `config` names no file, `competing-places` when two
        places of the root hold a configuration, `competing-declarations` or
        `invalid-declaration` for a declaration met by the search, and `invalid-pyproject` for a
        `pyproject.toml` that does not parse.
    """
    current = _normalize(cwd if cwd is not None else Path.cwd())
    variables = os.environ if environ is None else environ
    resolved_root = _resolve_root(tool, root, current, variables)
    if config is not None:
        given = _normalize(current / config)
        if not given.is_file():
            raise DiscoveryError(
                ErrorCode.MISSING_CONFIG, f"no configuration file at {given}, named by option"
            )
        return Discovery(resolved_root, Location(given))
    found = _locations(tool, resolved_root)
    if len(found) > 1:
        raise DiscoveryError(
            ErrorCode.COMPETING_PLACES,
            f"two places hold a configuration of {tool.name}: "
            + " and ".join(str(location.path) for location in found)
            + "; keep one",
        )
    return Discovery(resolved_root, found[0] if found else None)


def _resolve_root(
    tool: Tool, root: Path | None, current: Path, variables: Mapping[str, str]
) -> Path:
    """Return the root from the option, the variable, the search, or the current folder."""
    if root is not None:
        return _normalize(current / root)
    variable = variables.get(tool.variable, "")
    if variable:
        return _normalize(current / variable)
    outermost: Path | None = None
    for folder in (current, *current.parents):
        if _locations(tool, folder):
            if not tool.stacked:
                return folder
            outermost = folder
    return outermost if outermost is not None else current


def _locations(tool: Tool, folder: Path) -> list[Location]:
    """Return every place of `folder` holding a configuration of the tool, in search order."""
    bases = [folder, folder / DOT_CONFIG]
    bases += [folder / declared for declared in read_declared_folders(folder)]
    found = [
        Location(base / name)
        for base in bases
        for name in tool.file_names
        if (base / name).is_file()
    ]
    if tool.pyproject:
        table = _pyproject_table(tool, folder / PYPROJECT)
        if table is not None:
            found.append(Location(folder / PYPROJECT, table))
    return found


def _pyproject_table(tool: Tool, path: Path) -> Mapping[str, Any] | None:
    """Return the table `[tool.<name>]` of a `pyproject.toml`, or None when either is absent."""
    if not path.is_file():
        return None
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise DiscoveryError(ErrorCode.INVALID_PYPROJECT, f"{path}: {error}") from error
    section = document.get("tool")
    if not isinstance(section, dict):
        return None
    table = section.get(tool.name)
    return table if isinstance(table, dict) else None


def _normalize(path: Path) -> Path:
    """Return `path` made absolute and normalized lexically, as both implementations do."""
    return Path(os.path.normpath(path.absolute()))

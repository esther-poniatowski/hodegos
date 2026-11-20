"""
Port to the files read by a discovery, and its adapter of the local file system.

A tool can read a configuration inside a state served from memory or from Git. That tool supplies
its own adapter of the port, so that the state needs no copy on disk.

Classes
-------
FileSystem
    Read access to the files of a host, addressed by absolute paths.
LocalFileSystem
    Adapter of the port to the local file system, the default of a discovery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class FileSystem(Protocol):
    """
    Read access to the files of a host, addressed by absolute paths.

    The port has the shape of the port `FileSystem` of the TypeScript package.
    """

    def is_file(self, path: Path) -> bool:
        """
        Return whether `path` names a regular file.

        Parameters
        ----------
        path : Path
            Absolute path, normalized lexically.

        Returns
        -------
        bool
            True for a regular file; False for a folder, an absent or an unreachable path.
        """

    def read_text(self, path: Path) -> str:
        """
        Return the content of the file at `path`, decoded as UTF-8.

        Parameters
        ----------
        path : Path
            Absolute path of a regular file, normalized lexically.

        Returns
        -------
        str
            Content of the file.

        Raises
        ------
        OSError
            When the file cannot be read.
        UnicodeDecodeError
            When the content is not UTF-8.
        """


class LocalFileSystem:
    """
    Adapter of the port `FileSystem` to the local file system.

    Examples
    --------
    >>> LocalFileSystem().is_file(Path("/"))
    False
    """

    def is_file(self, path: Path) -> bool:
        """Return whether `path` names a regular file of the local file system, False when the path
        cannot be reached, as the adapter of Node answers."""
        try:
            return path.is_file()
        except OSError:
            return False

    def read_text(self, path: Path) -> str:
        """Return the content of the local file at `path`, decoded as UTF-8."""
        return path.read_text(encoding="utf-8")

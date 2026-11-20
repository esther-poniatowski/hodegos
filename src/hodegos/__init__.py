"""
Initialization logic and public interface for the `hodegos` package.

Hodegos resolves the root of a command and locates the configuration file of a tool, in the places
that the specification of Hodegos accepts for the convention of the tool. Each tool parses its own
file.

Variables
---------
__version__ : str, default "0.0.0+unknown"
    Version of the package. If the package metadata is unavailable (e.g. in editable or source-only
    environments), a fallback value is provided (PEP 440 compliant).
__all__ : list
    Public objects exposed by this package.

Classes
-------
Tool
    Convention of one tool: name, extensions, and the places that it reads.
Discovery
    Root of a command and the configuration that it reads.
Location
    Configuration found for a tool.
DiscoveryError
    Failure of a discovery, with its kind.
ErrorCode
    Kinds of failure of a discovery.
FileSystem
    Port to the files read by a discovery.
LocalFileSystem
    Adapter of the port to the local file system, the default of a discovery.

Functions
---------
discover(tool, *, root, config, start, cwd, environ, files) -> Discovery
    Resolve the root of a command and locate the configuration of the tool.
info() -> str
    Format diagnostic information about the package and platform.

Examples
--------
To programmatically retrieve the package version, a string:

    >>> import hodegos
    >>> isinstance(hodegos.__version__, str)
    True

See Also
--------
importlib.metadata.version
    Function to retrieve the version of a package.
PackageNotFoundError
    Exception raised when the package is not found in the environment.
"""

from importlib.metadata import version, PackageNotFoundError
import platform

from hodegos.discovery import Discovery, Location, discover
from hodegos.errors import DiscoveryError, ErrorCode
from hodegos.file_system import FileSystem, LocalFileSystem
from hodegos.tool import Tool

try:
    if __package__ is None:  # erroneous script execution
        raise PackageNotFoundError
    __version__ = version(__package__)
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "Discovery",
    "DiscoveryError",
    "ErrorCode",
    "FileSystem",
    "LocalFileSystem",
    "Location",
    "Tool",
    "discover",
    "info",
    "__version__",
]


def info() -> str:
    """Format diagnostic information on package and platform."""
    platform_name = f"{platform.system()} Python {platform.python_version()}"
    return f"{__package__} {__version__} | Platform: {platform_name}"

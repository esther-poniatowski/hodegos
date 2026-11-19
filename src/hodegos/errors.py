"""
Errors of the discovery, each carrying the code that the conformance cases name.

Classes
-------
ErrorCode
    Kinds of failure of a discovery.
DiscoveryError
    Failure of a discovery, with its kind and an actionable message.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """Kinds of failure of a discovery, shared with the TypeScript implementation."""

    INVALID_REQUEST = "invalid-request"
    """The tool name or an extension does not follow the convention."""
    MISSING_CONFIG = "missing-config"
    """The configuration option names no file."""
    COMPETING_PLACES = "competing-places"
    """Two places of the root hold a configuration of the tool."""
    COMPETING_DECLARATIONS = "competing-declarations"
    """A folder holds both `hodegos.yml` and `.config/hodegos.yml`."""
    INVALID_DECLARATION = "invalid-declaration"
    """A file `hodegos.yml` does not parse or departs from its format."""
    INVALID_PYPROJECT = "invalid-pyproject"
    """A file `pyproject.toml` read for the table of the tool does not parse."""


class DiscoveryError(ValueError):
    """
    Failure of a discovery.

    Attributes
    ----------
    code : ErrorCode
        Kind of the failure.
    """

    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code

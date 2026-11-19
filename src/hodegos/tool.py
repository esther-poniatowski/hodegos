"""
Convention of one tool: its name, the extensions of its file, and the places that it reads.

Classes
-------
Tool
    Convention of one tool, fixed by the tool and passed to every discovery.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from hodegos.errors import DiscoveryError, ErrorCode

TOOL_NAME = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
"""Form of a tool name: lowercase letters and digits, words joined by single hyphens."""

EXTENSION = re.compile(r"^[a-z0-9]+$")
"""Form of an extension, written without its dot."""


@dataclass(frozen=True)
class Tool:
    """
    Convention of one tool.

    Attributes
    ----------
    name : str
        Name of the tool, which names its file `<name>.<extension>` and its variable
        `<NAME>_ROOT`.
    extensions : tuple[str, ...]
        Extensions admitted for the file, without their dot, such as `("yml",)`.
    pyproject : bool
        Whether the table `[tool.<name>]` of `pyproject.toml` is a place of the configuration.
    stacked : bool
        Whether the tool stacks one file per folder, so that the search of the root takes the
        outermost folder holding a configuration instead of the nearest.

    Raises
    ------
    DiscoveryError
        With the code `invalid-request`, when the name or an extension departs from its form.

    Examples
    --------
    >>> Tool("anagraphe", ("yml",)).variable
    'ANAGRAPHE_ROOT'
    >>> Tool("probe-tool", ("toml",)).variable
    'PROBE_TOOL_ROOT'
    """

    name: str
    extensions: tuple[str, ...]
    pyproject: bool = False
    stacked: bool = False

    def __post_init__(self) -> None:
        if not TOOL_NAME.match(self.name):
            raise DiscoveryError(
                ErrorCode.INVALID_REQUEST,
                f"tool name {self.name!r}: write lowercase letters and digits, "
                "words joined by single hyphens",
            )
        if not self.extensions:
            raise DiscoveryError(
                ErrorCode.INVALID_REQUEST, f"tool {self.name}: admit at least one extension"
            )
        for extension in self.extensions:
            if not EXTENSION.match(extension):
                raise DiscoveryError(
                    ErrorCode.INVALID_REQUEST,
                    f"extension {extension!r} of tool {self.name}: write lowercase letters and "
                    "digits, without the dot",
                )

    @property
    def variable(self) -> str:
        """Name of the environment variable that names the root."""
        return self.name.upper().replace("-", "_") + "_ROOT"

    @property
    def file_names(self) -> tuple[str, ...]:
        """Names of the configuration file, one per extension, in the order of the extensions."""
        return tuple(f"{self.name}.{extension}" for extension in self.extensions)

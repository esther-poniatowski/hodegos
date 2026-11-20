"""
Run the conformance cases of `specs/cases/discovery.yml` against the Python implementation.

Each case runs twice. The first run reads a temporary folder through the default local file
system. The second run serves the tree from memory through the port `FileSystem`, below a top absent
from the disk.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from hodegos import Discovery, DiscoveryError, ErrorCode, FileSystem, Tool, discover

CASES_FILE = Path(__file__).resolve().parents[1] / "specs" / "cases" / "discovery.yml"
DOCUMENT: dict[str, Any] = yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))
DEFAULT_REQUEST: dict[str, Any] = DOCUMENT["defaults"]["request"]
CASES: list[dict[str, Any]] = DOCUMENT["cases"]

MEMORY_TOP = Path("/hodegos-memory-top")
"""Top of the trees served from memory, a folder absent from the disk."""


class MemoryFileSystem:
    """Adapter of the port `FileSystem` serving the files of a tree held in memory."""

    def __init__(self, files: dict[Path, str]) -> None:
        self.files = files

    def is_file(self, path: Path) -> bool:
        """Return whether the tree holds a file at `path`."""
        return path in self.files

    def read_text(self, path: Path) -> str:
        """Return the content of the file at `path`, or raise as a missing file does."""
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]


def _build(top: Path, tree: dict[str, str]) -> None:
    """Write each file of the tree below the top."""
    for relative, content in tree.items():
        path = top / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _relative(top: Path, path: Path) -> str:
    """Return a path of the outcome relative to the top, as the cases write it."""
    return path.relative_to(top).as_posix()


def _optional_path(value: str | None) -> Path | None:
    """Return the path of an optional value of the request."""
    return None if value is None else Path(value)


@pytest.mark.parametrize("reader", ["local", "memory"])
@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_case(case: dict[str, Any], reader: str, tmp_path: Path) -> None:
    """The outcome of the request equals the expected outcome of the case, for each reader."""
    request = {**DEFAULT_REQUEST, **case.get("request", {})}
    expect = case["expect"]
    files: FileSystem | None
    if reader == "local":
        top = tmp_path.resolve()
        _build(top, case["tree"])
        (top / request["cwd"]).mkdir(parents=True, exist_ok=True)
        files = None
    else:
        top = MEMORY_TOP
        assert not top.exists()
        files = MemoryFileSystem(
            {top / relative: content for relative, content in case["tree"].items()}
        )

    def run() -> Discovery:
        tool = Tool(
            request["tool"],
            tuple(request["extensions"]),
            pyproject=request["pyproject"],
            stacked=request["stacked"],
        )
        return discover(
            tool,
            root=_optional_path(request["root"]),
            config=_optional_path(request["config"]),
            start=_optional_path(request["start"]),
            cwd=top / request["cwd"],
            environ=request["environ"],
            files=files,
        )

    if "error" in expect:
        with pytest.raises(DiscoveryError) as caught:
            run()
        assert caught.value.code.value == expect["error"]
        return
    outcome = run()
    configuration = outcome.configuration
    assert {
        "root": _relative(top, outcome.root),
        "configuration": None if configuration is None else _relative(top, configuration.path),
        "table": None if configuration is None else configuration.table,
    } == expect


def test_every_error_code_has_a_case() -> None:
    """Each kind of failure is exercised by at least one case, so that no code goes untested."""
    expected = {case["expect"]["error"] for case in CASES if "error" in case["expect"]}
    assert expected == {code.value for code in ErrorCode}

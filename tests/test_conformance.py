"""Run the conformance cases of `specs/cases/discovery.yml` against the Python implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from hodegos import DiscoveryError, Tool, discover

CASES_FILE = Path(__file__).resolve().parents[1] / "specs" / "cases" / "discovery.yml"
DOCUMENT: dict[str, Any] = yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))
DEFAULT_REQUEST: dict[str, Any] = DOCUMENT["defaults"]["request"]
CASES: list[dict[str, Any]] = DOCUMENT["cases"]


def _build(top: Path, tree: dict[str, str]) -> None:
    """Write each file of the tree below the top."""
    for relative, content in tree.items():
        path = top / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _relative(top: Path, path: Path) -> str:
    """Return a path of the outcome relative to the top, as the cases write it."""
    return path.relative_to(top).as_posix()


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_case(case: dict[str, Any], tmp_path: Path) -> None:
    """The outcome of the request equals the expected outcome of the case."""
    top = tmp_path.resolve()
    _build(top, case["tree"])
    request = {**DEFAULT_REQUEST, **case.get("request", {})}
    expect = case["expect"]
    cwd = top / request["cwd"]
    cwd.mkdir(parents=True, exist_ok=True)

    def run() -> Any:
        tool = Tool(
            request["tool"],
            tuple(request["extensions"]),
            pyproject=request["pyproject"],
            stacked=request["stacked"],
        )
        return discover(
            tool,
            root=None if request["root"] is None else Path(request["root"]),
            config=None if request["config"] is None else Path(request["config"]),
            cwd=cwd,
            environ=request["environ"],
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
    from hodegos import ErrorCode  # pylint: disable=import-outside-toplevel

    expected = {case["expect"]["error"] for case in CASES if "error" in case["expect"]}
    assert expected == {code.value for code in ErrorCode}

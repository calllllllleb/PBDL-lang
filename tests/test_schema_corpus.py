from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pytest

from pbdl import validate_document


def _format_violations(violations: object) -> str:
    return repr(violations)


def test_valid_schema_corpus(
    repository_root: Path,
    load_json_fixture: Callable[[Path], Any],
) -> None:
    paths = sorted((repository_root / "spec" / "examples" / "valid").glob("*.json"))
    assert paths

    failures: list[str] = []
    for path in paths:
        result = validate_document(load_json_fixture(path))
        if not result.valid:
            failures.append(f"{path.name}: {_format_violations(result.violations)}")

    assert not failures, "\n".join(failures)


def test_invalid_schema_corpus(
    repository_root: Path,
    load_json_fixture: Callable[[Path], Any],
) -> None:
    paths = sorted((repository_root / "spec" / "examples" / "invalid").glob("*.json"))
    assert paths

    unexpected: list[str] = []
    for path in paths:
        result = validate_document(load_json_fixture(path))
        if result.valid:
            unexpected.append(path.name)

    assert not unexpected, f"unexpected Schema-valid fixtures: {unexpected!r}"


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_fixture_loader_rejects_nonstandard_json_constants(
    tmp_path: Path,
    load_json_fixture: Callable[[Path], Any],
    constant: str,
) -> None:
    path = tmp_path / "nonstandard.json"
    path.write_text(f"{{\"value\": {constant}}}", encoding="utf-8")

    with pytest.raises(ValueError, match="non-standard JSON constant"):
        load_json_fixture(path)

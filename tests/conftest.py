from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pytest


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def load_json_fixture() -> Callable[[Path], Any]:
    def _reject_nonstandard_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant: {value}")

    def _load(path: Path) -> Any:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle, parse_constant=_reject_nonstandard_constant)

    return _load

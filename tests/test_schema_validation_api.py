from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

import pbdl.schema_validation as schema_validation
from pbdl import (
    SchemaValidationResult,
    SchemaViolation,
    is_schema_valid,
    validate_document,
)
from tests.helpers import minimal_document


def test_public_api_valid_document_has_no_schema_violations() -> None:
    result = validate_document(minimal_document())

    assert result == SchemaValidationResult(valid=True, violations=())
    assert is_schema_valid(minimal_document()) is True


def test_public_api_invalid_document_returns_structured_violations() -> None:
    result = validate_document({})

    assert result.valid is False
    assert result.violations
    for violation in result.violations:
        assert isinstance(violation, SchemaViolation)
        assert isinstance(violation.instance_path, tuple)
        assert isinstance(violation.schema_path, tuple)
        assert violation.keyword is None or isinstance(violation.keyword, str)
        assert isinstance(violation.message, str)


def test_result_rejects_inconsistent_validity_flag() -> None:
    violation = SchemaViolation((), (), "required", "missing field")

    with pytest.raises(ValueError):
        SchemaValidationResult(valid=True, violations=(violation,))


def test_canonical_schema_path_points_to_specification_artifact(repository_root: Path) -> None:
    assert schema_validation._canonical_schema_path() == (
        repository_root / "spec" / "schema" / "pbdl-v1.schema.json"
    )


def test_production_validator_is_explicit_draft_2020_12() -> None:
    validator = schema_validation._get_validator()

    assert isinstance(validator, Draft202012Validator)


def test_schema_self_check_exposes_schema_artifact_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    schema_validation._get_validator.cache_clear()
    monkeypatch.setattr(schema_validation, "_load_schema", lambda: {"type": 42})

    with pytest.raises(SchemaError):
        schema_validation._get_validator()

    schema_validation._get_validator.cache_clear()


def test_diagnostics_are_deterministic_with_mixed_path_segments() -> None:
    document = {
        "pbdl_version": "1.0.0",
        "subjects": [{"id": "ok"}, {"id": "bad id", "extra": True}],
        "behaviors": None,
        "preferences": [],
        "relations": [],
        "extra": 1,
    }

    first = validate_document(document)
    second = validate_document(document)

    assert first == second
    assert first.violations == second.violations
    assert len(first.violations) >= 4


@pytest.mark.parametrize("document", [minimal_document(), {}])
def test_validation_never_mutates_input(document: object) -> None:
    before = deepcopy(document)

    validate_document(document)

    assert document == before


def test_missing_schema_artifact_is_not_converted_to_document_invalidity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    missing = tmp_path / "missing-schema.json"
    schema_validation._load_schema.cache_clear()
    schema_validation._get_validator.cache_clear()
    monkeypatch.setattr(schema_validation, "_canonical_schema_path", lambda: missing)

    with pytest.raises(FileNotFoundError):
        validate_document(minimal_document())

    schema_validation._load_schema.cache_clear()
    schema_validation._get_validator.cache_clear()

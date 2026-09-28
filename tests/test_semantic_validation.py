from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from pbdl import (
    SemanticInputError,
    SemanticValidationResult,
    SemanticViolation,
    are_semantics_valid,
    validate_semantics,
)
from tests.helpers import (
    base_behavior,
    base_preference,
    base_relation,
    direct_provenance,
    generator_descriptor,
    minimal_document,
)


def _document_with_all_core_entities() -> dict[str, Any]:
    document = minimal_document()
    document["behaviors"] = [base_behavior()]
    document["preferences"] = [base_preference()]
    document["relations"] = [base_relation()]
    return document


def _document_with_behavior_temporal(temporal: dict[str, Any]) -> dict[str, Any]:
    document = minimal_document()
    behavior = base_behavior()
    behavior["temporal"] = temporal
    document["behaviors"] = [behavior]
    return document


def _instant(value: str) -> dict[str, Any]:
    return {"kind": "instant", "at": value}


def _interval(start: str, end: str) -> dict[str, Any]:
    return {"kind": "interval", "start": start, "end": end}


def test_public_api_accepts_semantically_valid_document() -> None:
    result = validate_semantics(_document_with_all_core_entities())

    assert result == SemanticValidationResult(valid=True, violations=())
    assert are_semantics_valid(_document_with_all_core_entities()) is True


def test_result_rejects_inconsistent_validity_flag() -> None:
    violation = SemanticViolation(
        instance_path=("behaviors", 0, "temporal", "at"),
        kind="invalid_temporal_date",
        message="invalid date",
    )

    with pytest.raises(ValueError):
        SemanticValidationResult(valid=True, violations=(violation,))


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2024-02-29", True),
        ("2023-02-29", False),
        ("1900-02-29", False),
        ("2000-02-29", True),
        ("2026-02-30", False),
    ],
)
def test_gregorian_calendar_boundaries(value: str, expected: bool) -> None:
    result = validate_semantics(_document_with_behavior_temporal(_instant(value)))

    assert result.valid is expected
    if not expected:
        assert result.violations[0].kind == "invalid_temporal_date"
        assert result.violations[0].instance_path == (
            "behaviors",
            0,
            "temporal",
            "at",
        )


@pytest.mark.parametrize(
    "value",
    [
        "2023-02-29T10:00",
        "1900-02-29T10:00:00Z",
        "2026-02-30T10:00:00.123456789+08:00",
    ],
)
def test_datetime_calendar_date_must_exist(value: str) -> None:
    result = validate_semantics(_document_with_behavior_temporal(_instant(value)))

    assert result.valid is False
    assert result.violations[0].kind == "invalid_temporal_date"


def _document_for_temporal_surface(surface: str, value: str) -> dict[str, Any]:
    if surface == "behavior_temporal":
        return _document_with_behavior_temporal(_instant(value))

    if surface == "preference_temporal":
        document = minimal_document()
        preference = base_preference()
        preference["temporal"] = _instant(value)
        document["preferences"] = [preference]
        return document

    if surface == "relation_temporal":
        document = _document_with_all_core_entities()
        document["relations"][0]["temporal"] = _instant(value)
        return document

    document = minimal_document()
    behavior = base_behavior()
    if surface == "observed_window":
        behavior["frequencies"] = [
            {
                "kind": "observed_count",
                "count": 1,
                "precision": "exact",
                "window": {"kind": "interval", "start": value},
            }
        ]
    elif surface == "source_time":
        behavior["provenance"][0]["source"]["times"] = [
            {"role": "reported", "at": value}
        ]
    elif surface == "generator_time":
        generator = generator_descriptor()
        generator["times"] = [{"role": "generated", "at": value}]
        behavior["provenance"][0]["generator"] = generator
    elif surface == "evidence_time":
        behavior["provenance"][0]["evidence"] = [
            {
                "kind": "text_excerpt",
                "content": "source text",
                "times": [{"role": "recorded", "at": value}],
            }
        ]
    else:
        raise AssertionError(surface)
    document["behaviors"] = [behavior]
    return document


@pytest.mark.parametrize(
    ("surface", "expected_path"),
    [
        ("behavior_temporal", ("behaviors", 0, "temporal", "at")),
        ("preference_temporal", ("preferences", 0, "temporal", "at")),
        ("relation_temporal", ("relations", 0, "temporal", "at")),
        (
            "observed_window",
            ("behaviors", 0, "frequencies", 0, "window", "start"),
        ),
        (
            "source_time",
            ("behaviors", 0, "provenance", 0, "source", "times", 0, "at"),
        ),
        (
            "generator_time",
            ("behaviors", 0, "provenance", 0, "generator", "times", 0, "at"),
        ),
        (
            "evidence_time",
            (
                "behaviors",
                0,
                "provenance",
                0,
                "evidence",
                0,
                "times",
                0,
                "at",
            ),
        ),
    ],
)
def test_all_temporal_owner_surfaces_are_traversed(
    surface: str, expected_path: tuple[str | int, ...]
) -> None:
    result = validate_semantics(_document_for_temporal_surface(surface, "2026-02-30"))

    assert result.valid is False
    assert result.violations[0].kind == "invalid_temporal_date"
    assert result.violations[0].instance_path == expected_path


def test_nested_local_provenance_time_is_traversed() -> None:
    document = minimal_document()
    behavior = base_behavior()
    local = direct_provenance()
    local["source"]["times"] = [{"role": "observed", "at": "2026-02-30"}]
    behavior["contexts"] = [
        {
            "value": {"kind": "text", "value": "at home"},
            "provenance": [local],
        }
    ]
    document["behaviors"] = [behavior]

    result = validate_semantics(document)

    assert result.valid is False
    assert result.violations[0].instance_path == (
        "behaviors",
        0,
        "contexts",
        0,
        "provenance",
        0,
        "source",
        "times",
        0,
        "at",
    )


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("2026-10", "2026-09-15", False),
        ("2026-09", "2026-09-15", True),
        ("2026", "2026-09-15", True),
        ("2027", "2026-12", False),
    ],
)
def test_date_family_interval_uses_conservative_possible_ranges(
    start: str, end: str, expected: bool
) -> None:
    result = validate_semantics(
        _document_with_behavior_temporal(_interval(start, end))
    )

    assert result.valid is expected
    if not expected:
        assert result.violations[0].kind == "interval_order"


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("2026-09-28T10:01", "2026-09-28T10:00:59", False),
        ("2026-09-28T10:00", "2026-09-28T10:00:30", True),
        ("2026-09-28T10:00:30", "2026-09-28T10:00", True),
    ],
)
def test_local_datetime_interval_comparison(
    start: str, end: str, expected: bool
) -> None:
    result = validate_semantics(
        _document_with_behavior_temporal(_interval(start, end))
    )

    assert result.valid is expected


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("2026-09-28T10:00+00:00", "2026-09-28T10:30+01:00", False),
        ("2026-09-28T10:00+02:00", "2026-09-28T08:30+00:00", True),
        ("2026-09-28T10:00Z[UTC]", "2026-09-28T09:30+00:00", False),
    ],
)
def test_explicit_offset_datetime_uses_physical_instant_ranges(
    start: str, end: str, expected: bool
) -> None:
    result = validate_semantics(
        _document_with_behavior_temporal(_interval(start, end))
    )

    assert result.valid is expected


def test_mixed_offset_datetime_is_not_forced_comparable() -> None:
    result = validate_semantics(
        _document_with_behavior_temporal(
            _interval("2026-09-28T10:00Z", "2026-09-28T09:00")
        )
    )

    assert result.valid is True


def test_zone_token_only_datetime_is_not_forced_comparable() -> None:
    result = validate_semantics(
        _document_with_behavior_temporal(
            _interval(
                "2026-09-28T10:00[America/Los_Angeles]",
                "2026-09-28T09:00[America/Los_Angeles]",
            )
        )
    )

    assert result.valid is True


def test_date_and_datetime_families_are_not_forced_comparable() -> None:
    result = validate_semantics(
        _document_with_behavior_temporal(
            _interval("2026-10-02", "2026-10-01T23:59")
        )
    )

    assert result.valid is True


@pytest.mark.parametrize(
    "fraction",
    ["1", "10", "100", "1234567", "12345678", "123456789"],
)
def test_fractional_second_precision_from_one_to_nine_digits_is_supported(
    fraction: str,
) -> None:
    value = f"2026-09-28T10:00:00.{fraction}"
    result = validate_semantics(
        _document_with_behavior_temporal(_interval(value, value))
    )

    assert result.valid is True


def test_nanosecond_ordering_is_not_truncated_to_microseconds() -> None:
    result = validate_semantics(
        _document_with_behavior_temporal(
            _interval(
                "2026-09-28T10:00:00.100000001",
                "2026-09-28T10:00:00.100000000",
            )
        )
    )

    assert result.valid is False
    assert result.violations[0].kind == "interval_order"


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_rate_frequency_requires_finite_value(value: float) -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["frequencies"] = [
        {
            "kind": "rate",
            "value": value,
            "period": {"value": 1, "unit": "day"},
            "precision": "exact",
        }
    ]
    document["behaviors"] = [behavior]

    result = validate_semantics(document)

    assert result.valid is False
    assert result.violations[0].kind == "non_finite_number"
    assert result.violations[0].instance_path == (
        "behaviors",
        0,
        "frequencies",
        0,
        "value",
    )


@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), float("-inf")]
)
def test_numeric_preference_requires_finite_value(value: float) -> None:
    document = minimal_document()
    preference = base_preference()
    preference["value"] = {"kind": "number", "operator": "eq", "value": value}
    document["preferences"] = [preference]

    result = validate_semantics(document)

    assert result.valid is False
    assert result.violations[0].kind == "non_finite_number"
    assert result.violations[0].instance_path == (
        "preferences",
        0,
        "value",
        "value",
    )


@pytest.mark.parametrize(
    ("field", "expected_suffix"),
    [
        ("value", ("value",)),
        ("min", ("scale", "min")),
        ("max", ("scale", "max")),
    ],
)
def test_confidence_requires_finite_numeric_fields(
    field: str, expected_suffix: tuple[str, ...]
) -> None:
    document = minimal_document()
    behavior = base_behavior()
    confidence = {
        "value": 0.5,
        "metric": "score",
        "scale": {"min": 0.0, "max": 1.0},
    }
    if field == "value":
        confidence["value"] = float("inf")
    else:
        confidence["scale"][field] = float("nan")
    behavior["provenance"][0]["confidence"] = confidence
    document["behaviors"] = [behavior]

    result = validate_semantics(document)

    assert result.valid is False
    matching = [item for item in result.violations if item.kind == "non_finite_number"]
    assert len(matching) == 1
    assert matching[0].instance_path[-len(expected_suffix) :] == expected_suffix


@pytest.mark.parametrize(
    ("value", "minimum", "maximum", "expected", "expected_kind"),
    [
        (0.0, 0.0, 1.0, True, None),
        (1.0, 0.0, 1.0, True, None),
        (-0.1, 0.0, 1.0, False, "confidence_value_out_of_range"),
        (1.1, 0.0, 1.0, False, "confidence_value_out_of_range"),
        (0.5, 1.0, 1.0, False, "invalid_confidence_scale"),
        (20.0, 100.0, 0.0, False, "invalid_confidence_scale"),
    ],
)
def test_confidence_scale_consistency(
    value: float,
    minimum: float,
    maximum: float,
    expected: bool,
    expected_kind: str | None,
) -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["provenance"][0]["confidence"] = {
        "value": value,
        "metric": "score",
        "scale": {"min": minimum, "max": maximum},
    }
    document["behaviors"] = [behavior]

    result = validate_semantics(document)

    assert result.valid is expected
    if expected_kind is not None:
        assert result.violations[0].kind == expected_kind


def test_confidence_without_scale_has_no_universal_range() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["provenance"][0]["confidence"] = {
        "value": 250.0,
        "metric": "producer_defined_score",
    }
    document["behaviors"] = [behavior]

    assert validate_semantics(document).valid is True


def test_nested_local_provenance_confidence_is_traversed() -> None:
    document = minimal_document()
    behavior = base_behavior()
    local = direct_provenance()
    local["confidence"] = {
        "value": 2.0,
        "metric": "score",
        "scale": {"min": 0.0, "max": 1.0},
    }
    behavior["factors"] = [
        {
            "role": "observed_association",
            "factor": {"kind": "text", "value": "factor"},
            "direction": "unspecified",
            "provenance": [local],
        }
    ]
    document["behaviors"] = [behavior]

    result = validate_semantics(document)

    assert result.valid is False
    assert result.violations[0].instance_path == (
        "behaviors",
        0,
        "factors",
        0,
        "provenance",
        0,
        "confidence",
        "value",
    )


def test_schema_invalid_input_is_semantic_precondition_failure() -> None:
    with pytest.raises(SemanticInputError) as captured:
        validate_semantics({})

    error = captured.value
    assert error.schema_result is not None
    assert error.schema_result.valid is False
    assert error.resolution_result is None
    assert error.lower_layer_result is error.schema_result


def test_reference_invalid_input_is_semantic_precondition_failure() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["subject"] = {"ref": "missing"}
    document["behaviors"] = [behavior]

    with pytest.raises(SemanticInputError) as captured:
        validate_semantics(document)

    error = captured.value
    assert error.schema_result is None
    assert error.resolution_result is not None
    assert error.resolution_result.valid is False
    assert error.lower_layer_result is error.resolution_result


def test_boolean_helper_preserves_lower_layer_preconditions() -> None:
    with pytest.raises(SemanticInputError):
        are_semantics_valid({})


def test_diagnostics_are_deterministic() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["temporal"] = _instant("2026-02-30")
    behavior["frequencies"] = [
        {
            "kind": "rate",
            "value": float("inf"),
            "period": {"value": 1, "unit": "day"},
            "precision": "exact",
        }
    ]
    behavior["provenance"][0]["confidence"] = {
        "value": 2.0,
        "metric": "score",
        "scale": {"min": 0.0, "max": 1.0},
    }
    document["behaviors"] = [behavior]

    first = validate_semantics(document)
    second = validate_semantics(document)

    assert first == second
    assert first.violations == second.violations


def test_semantic_validation_never_mutates_input() -> None:
    document = _document_with_all_core_entities()
    document["behaviors"][0]["temporal"] = _interval("2026-09", "2026-09-15")
    before = deepcopy(document)

    validate_semantics(document)

    assert document == before


def test_optional_empty_collections_remain_semantically_valid() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior.update(
        {
            "frequencies": [],
            "contexts": [],
            "factors": [],
            "annotations": [],
        }
    )
    document["behaviors"] = [behavior]

    assert validate_semantics(document).valid is True


def test_full_equal_embedded_duplicate_is_not_semantic_invalidity() -> None:
    document = minimal_document()
    behavior = base_behavior()
    annotation = {
        "text": "same",
        "provenance": [direct_provenance()],
    }
    behavior["annotations"] = [annotation, deepcopy(annotation)]
    document["behaviors"] = [behavior]

    assert validate_semantics(document).valid is True


def test_semantic_equivalent_explicit_child_provenance_is_not_rejected() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = [
        {
            "value": {"kind": "text", "value": "at home"},
            "provenance": deepcopy(behavior["provenance"]),
        }
    ]
    document["behaviors"] = [behavior]

    assert validate_semantics(document).valid is True


@pytest.mark.parametrize("endpoint_kind", ["behavior", "preference"])
def test_relation_endpoint_kind_combinations_are_not_over_constrained(
    endpoint_kind: str,
) -> None:
    document = _document_with_all_core_entities()
    entity_id = "behavior_1" if endpoint_kind == "behavior" else "preference_1"
    document["relations"][0]["source"] = {"ref": entity_id}
    document["relations"][0]["target"] = {"ref": entity_id}
    document["relations"][0]["type"] = {
        "system": "urn:example:relation",
        "code": "arbitrary_structurally_valid_type",
    }

    assert validate_semantics(document).valid is True


def test_numeric_preference_without_unit_remains_semantically_valid() -> None:
    document = minimal_document()
    preference = base_preference()
    preference["value"] = {"kind": "number", "operator": "lte", "value": 30}
    document["preferences"] = [preference]

    assert validate_semantics(document).valid is True


def test_text_preference_fallback_remains_semantically_valid() -> None:
    document = minimal_document()
    preference = base_preference()
    preference["value"] = {"kind": "text", "value": "source-supported wording"}
    document["preferences"] = [preference]

    assert validate_semantics(document).valid is True

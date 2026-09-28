from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

import pbdl.canonicalization as canonicalization
from pbdl import (
    CanonicalizationInputError,
    canonicalize_document,
    is_canonical_normal_form,
)
from tests.helpers import (
    base_behavior,
    base_preference,
    base_relation,
    direct_provenance,
    generator_descriptor,
    minimal_document,
)


def _p1() -> dict[str, Any]:
    return direct_provenance("patient_self_report")


def _p2() -> dict[str, Any]:
    return direct_provenance("clinician_documentation")


def _document_with_all_core_entities() -> dict[str, Any]:
    document = minimal_document()
    document["behaviors"] = [base_behavior()]
    document["preferences"] = [base_preference()]
    document["relations"] = [base_relation()]
    return document


def _context(
    value: str,
    provenance: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "value": {"kind": "text", "value": value}
    }
    if provenance is not None:
        result["provenance"] = deepcopy(provenance)
    return result


def _factor(
    *,
    direction: str = "unspecified",
    provenance: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "role": "observed_association",
        "factor": {"kind": "text", "value": "factor"},
        "direction": direction,
    }
    if provenance is not None:
        result["provenance"] = deepcopy(provenance)
    return result


def _recurrence(
    days: list[str],
    provenance: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "kind": "recurrence",
        "period": {"value": 1, "unit": "week"},
        "precision": "exact",
        "days_of_week": days,
    }
    if provenance is not None:
        result["provenance"] = deepcopy(provenance)
    return result


def test_public_api_keeps_already_canonical_document_unchanged() -> None:
    document = minimal_document()

    assert canonicalize_document(document) == document
    assert is_canonical_normal_form(document) is True


def test_optional_empty_collections_are_omitted_but_required_roots_are_preserved() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior.update(
        frequencies=[],
        contexts=[],
        factors=[],
        annotations=[],
    )
    behavior["provenance"][0]["evidence"] = []
    behavior["provenance"][0]["source"]["times"] = []
    generator = generator_descriptor()
    generator["times"] = []
    behavior["provenance"][0]["generator"] = generator
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)
    canonical_behavior = canonical["behaviors"][0]

    for field in ("frequencies", "contexts", "factors", "annotations"):
        assert field not in canonical_behavior
    provenance = canonical_behavior["provenance"][0]
    assert "evidence" not in provenance
    assert "times" not in provenance["source"]
    assert "times" not in provenance["generator"]
    assert canonical["preferences"] == []
    assert canonical["relations"] == []


def test_empty_evidence_times_are_omitted() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["provenance"][0]["evidence"] = [
        {"kind": "text_excerpt", "content": "text", "times": []}
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    evidence = canonical["behaviors"][0]["provenance"][0]["evidence"][0]
    assert "times" not in evidence


def test_provenance_duplicates_use_nested_order_insensitive_equality() -> None:
    document = minimal_document()
    behavior = base_behavior()
    first = _p1()
    first["source"]["times"] = [
        {"role": "reported", "at": "2026-09"},
        {"role": "recorded", "at": "2026-10"},
    ]
    first["evidence"] = [
        {"kind": "text_excerpt", "content": "a"},
        {"kind": "text_excerpt", "content": "b"},
    ]
    second = deepcopy(first)
    second["source"]["times"].reverse()
    second["evidence"].reverse()
    behavior["provenance"] = [first, second]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["provenance"]) == 1


@pytest.mark.parametrize("surface", ["source", "generator", "evidence"])
def test_time_event_duplicates_are_removed_stably(surface: str) -> None:
    document = minimal_document()
    behavior = base_behavior()
    earlier = {"role": "reported", "at": "2026-09"}
    later = {"role": "recorded", "at": "2026-10"}

    if surface == "source":
        behavior["provenance"][0]["source"]["times"] = [
            deepcopy(later),
            deepcopy(earlier),
            deepcopy(later),
        ]
        role_times = behavior["provenance"][0]["source"]["times"]
    elif surface == "generator":
        generator = generator_descriptor()
        generator["times"] = [
            {"role": "generated", "at": "2026-10"},
            {"role": "migrated", "at": "2026-09"},
            {"role": "generated", "at": "2026-10"},
        ]
        behavior["provenance"][0]["generator"] = generator
        role_times = generator["times"]
    else:
        behavior["provenance"][0]["evidence"] = [
            {
                "kind": "text_excerpt",
                "content": "text",
                "times": [
                    deepcopy(later),
                    deepcopy(earlier),
                    deepcopy(later),
                ],
            }
        ]
        role_times = behavior["provenance"][0]["evidence"][0]["times"]

    expected = deepcopy(role_times[:2])
    document["behaviors"] = [behavior]
    canonical = canonicalize_document(document)

    provenance = canonical["behaviors"][0]["provenance"][0]
    if surface == "source":
        actual = provenance["source"]["times"]
    elif surface == "generator":
        actual = provenance["generator"]["times"]
    else:
        actual = provenance["evidence"][0]["times"]
    assert actual == expected


def test_evidence_duplicates_are_removed_after_child_normalization() -> None:
    document = minimal_document()
    behavior = base_behavior()
    evidence = {
        "kind": "text_excerpt",
        "content": "text",
        "times": [
            {"role": "reported", "at": "2026-09"},
            {"role": "reported", "at": "2026-09"},
        ],
    }
    behavior["provenance"][0]["evidence"] = [
        deepcopy(evidence),
        deepcopy(evidence),
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)
    items = canonical["behaviors"][0]["provenance"][0]["evidence"]

    assert len(items) == 1
    assert len(items[0]["times"]) == 1


def test_annotation_duplicates_use_full_equality_and_order_insensitive_provenance() -> None:
    document = minimal_document()
    behavior = base_behavior()
    first = {"text": "note", "provenance": [_p1(), _p2()]}
    second = {"text": "note", "provenance": [_p2(), _p1()]}
    behavior["annotations"] = [first, second]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["annotations"]) == 1
    assert "provenance" in canonical["behaviors"][0]["annotations"][0]


def test_annotation_provenance_is_never_removed_by_owner_inheritance() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["annotations"] = [
        {
            "text": "note",
            "provenance": deepcopy(behavior["provenance"]),
        }
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    annotation = canonical["behaviors"][0]["annotations"][0]
    assert annotation["provenance"] == [_p1()]


def test_context_duplicates_require_same_content_and_effective_provenance() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = [
        _context("home"),
        _context("home", [_p1()]),
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["contexts"]) == 1


def test_context_same_content_but_different_effective_provenance_is_preserved() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = [
        _context("home"),
        _context("home", [_p2()]),
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["contexts"]) == 2


def test_coded_context_canonical_information_difference_prevents_dedup() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = [
        {
            "value": {
                "kind": "coded",
                "value": {
                    "system": "s",
                    "code": "c",
                    "display": "A",
                },
            }
        },
        {
            "value": {
                "kind": "coded",
                "value": {
                    "system": "s",
                    "code": "c",
                    "display": "B",
                },
            }
        },
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["contexts"]) == 2


def test_text_context_equality_is_exact_and_does_not_case_fold() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = [
        _context("Home"),
        _context("home"),
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["contexts"]) == 2


def test_behavior_factor_role_direction_or_provenance_difference_is_preserved() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["factors"] = [
        _factor(direction="unspecified"),
        _factor(direction="factor_to_behavior"),
        _factor(direction="unspecified", provenance=[_p2()]),
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["factors"]) == 3


def test_recurrence_days_of_week_order_is_ignored_for_duplicate_equality() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["frequencies"] = [
        _recurrence(["mon", "wed"]),
        _recurrence(["wed", "mon"]),
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["frequencies"]) == 1
    days = canonical["behaviors"][0]["frequencies"][0]["days_of_week"]
    assert days == ["mon", "wed"]


def test_frequency_same_content_but_different_effective_provenance_is_preserved() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["frequencies"] = [
        _recurrence(["mon", "wed"]),
        _recurrence(["wed", "mon"], [_p2()]),
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["frequencies"]) == 2


@pytest.mark.parametrize(
    "surface",
    ["temporal", "frequency", "context", "factor"],
)
def test_redundant_explicit_local_provenance_is_omitted(
    surface: str,
) -> None:
    document = minimal_document()
    behavior = base_behavior()
    if surface == "temporal":
        behavior["temporal"] = {
            "kind": "instant",
            "at": "2026-09",
            "provenance": [_p1()],
        }
    elif surface == "frequency":
        behavior["frequencies"] = [
            _recurrence(["mon"], [_p1()])
        ]
    elif surface == "context":
        behavior["contexts"] = [
            _context("home", [_p1()])
        ]
    else:
        behavior["factors"] = [
            _factor(provenance=[_p1()])
        ]
    document["behaviors"] = [behavior]

    canonical_behavior = canonicalize_document(document)["behaviors"][0]
    if surface == "temporal":
        qualifier = canonical_behavior["temporal"]
    elif surface == "frequency":
        qualifier = canonical_behavior["frequencies"][0]
    elif surface == "context":
        qualifier = canonical_behavior["contexts"][0]
    else:
        qualifier = canonical_behavior["factors"][0]
    assert "provenance" not in qualifier


def test_different_or_subset_local_provenance_is_preserved() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["provenance"] = [_p1(), _p2()]
    behavior["contexts"] = [
        _context("home", [_p1()])
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    local = canonical["behaviors"][0]["contexts"][0]["provenance"]
    assert local == [_p1()]


def test_window_inherits_frequency_effective_provenance_not_behavior_owner() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["frequencies"] = [
        {
            "kind": "observed_count",
            "count": 1,
            "precision": "exact",
            "provenance": [_p2()],
            "window": {
                "kind": "interval",
                "start": "2026-09",
                "provenance": [_p2()],
            },
        }
    ]
    document["behaviors"] = [behavior]

    canonical_frequency = canonicalize_document(document)["behaviors"][0][
        "frequencies"
    ][0]

    assert canonical_frequency["provenance"] == [_p2()]
    assert "provenance" not in canonical_frequency["window"]


def test_window_explicit_behavior_provenance_remains_when_frequency_overrides() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["frequencies"] = [
        {
            "kind": "observed_count",
            "count": 1,
            "precision": "exact",
            "provenance": [_p2()],
            "window": {
                "kind": "interval",
                "start": "2026-09",
                "provenance": [_p1()],
            },
        }
    ]
    document["behaviors"] = [behavior]

    canonical_frequency = canonicalize_document(document)["behaviors"][0][
        "frequencies"
    ][0]

    assert canonical_frequency["provenance"] == [_p2()]
    assert canonical_frequency["window"]["provenance"] == [_p1()]


def test_observed_count_duplicate_checks_window_full_temporal_equality() -> None:
    document = minimal_document()
    behavior = base_behavior()
    common = {
        "kind": "observed_count",
        "count": 1,
        "precision": "exact",
        "window": {
            "kind": "interval",
            "start": "2026-09",
        },
    }
    different = deepcopy(common)
    different["window"]["provenance"] = [_p2()]
    behavior["frequencies"] = [common, different]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["frequencies"]) == 2


def test_temporal_exact_string_equality_does_not_rewrite_precision() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["frequencies"] = [
        {
            "kind": "observed_count",
            "count": 1,
            "precision": "exact",
            "window": {
                "kind": "interval",
                "start": "2026-09-28T10:00:00.1",
            },
        },
        {
            "kind": "observed_count",
            "count": 1,
            "precision": "exact",
            "window": {
                "kind": "interval",
                "start": "2026-09-28T10:00:00.10",
            },
        },
    ]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["frequencies"]) == 2
    value = canonical["behaviors"][0]["frequencies"][0]["window"]["start"]
    assert value.endswith(".1")


def test_confidence_numeric_equality_is_exact_mathematical_number_equality() -> None:
    document = minimal_document()
    behavior = base_behavior()
    first = _p1()
    second = _p1()
    first["confidence"] = {"value": 1, "metric": "score"}
    second["confidence"] = {"value": 1.0, "metric": "score"}
    behavior["provenance"] = [first, second]
    document["behaviors"] = [behavior]

    canonical = canonicalize_document(document)

    assert len(canonical["behaviors"][0]["provenance"]) == 1


def test_private_preference_value_equality_preserves_operator_unit_and_coding_information() -> None:
    base = {"kind": "number", "operator": "lte", "value": 1}
    same_number = {"kind": "number", "operator": "lte", "value": 1.0}
    other_operator = {"kind": "number", "operator": "lt", "value": 1}
    with_unit = {
        "kind": "number",
        "operator": "lte",
        "value": 1,
        "unit": {
            "system": "u",
            "code": "min",
            "display": "minutes",
        },
    }
    other_display = deepcopy(with_unit)
    other_display["unit"]["display"] = "minute"

    assert canonicalization._preference_value_equal(
        base, same_number
    ) is True
    assert canonicalization._preference_value_equal(
        base, other_operator
    ) is False
    assert canonicalization._preference_value_equal(
        with_unit, other_display
    ) is False


def test_same_oriented_full_equal_relation_is_deduplicated() -> None:
    document = _document_with_all_core_entities()
    document["relations"] = [
        deepcopy(document["relations"][0]),
        deepcopy(document["relations"][0]),
    ]

    canonical = canonicalize_document(document)

    assert len(canonical["relations"]) == 1


def test_relation_temporal_redundant_local_provenance_normalizes_before_dedup() -> None:
    document = _document_with_all_core_entities()
    first = deepcopy(document["relations"][0])
    first["temporal"] = {
        "kind": "instant",
        "at": "2026-09",
    }
    second = deepcopy(first)
    second["temporal"]["provenance"] = deepcopy(second["provenance"])
    document["relations"] = [first, second]

    canonical = canonicalize_document(document)

    assert len(canonical["relations"]) == 1
    assert "provenance" not in canonical["relations"][0]["temporal"]


def test_swapped_relation_endpoints_are_preserved_without_vocabulary_contract() -> None:
    document = minimal_document()
    first = base_behavior()
    second = base_behavior()
    second["id"] = "behavior_2"
    document["behaviors"] = [first, second]
    relation = base_relation()
    relation["source"] = {"ref": "behavior_1"}
    relation["target"] = {"ref": "behavior_2"}
    swapped = deepcopy(relation)
    swapped["source"], swapped["target"] = (
        swapped["target"],
        swapped["source"],
    )
    document["relations"] = [relation, swapped]

    canonical = canonicalize_document(document)

    assert len(canonical["relations"]) == 2
    assert canonical["relations"][0]["source"]["ref"] == "behavior_1"
    assert canonical["relations"][1]["source"]["ref"] == "behavior_2"


@pytest.mark.parametrize(
    "difference",
    ["type", "temporal", "provenance", "annotation"],
)
def test_relation_full_information_differences_prevent_dedup(
    difference: str,
) -> None:
    document = _document_with_all_core_entities()
    first = deepcopy(document["relations"][0])
    second = deepcopy(first)
    if difference == "type":
        second["type"]["display"] = "different"
    elif difference == "temporal":
        first["temporal"] = {
            "kind": "instant",
            "at": "2026-09",
        }
        second["temporal"] = {
            "kind": "instant",
            "at": "2026-10",
        }
    elif difference == "provenance":
        second["provenance"] = [_p1()]
    else:
        first["annotations"] = [
            {"text": "one", "provenance": [_p1()]}
        ]
        second["annotations"] = [
            {"text": "two", "provenance": [_p1()]}
        ]
    document["relations"] = [first, second]

    canonical = canonicalize_document(document)

    assert len(canonical["relations"]) == 2


def test_root_entity_order_and_collection_survivor_order_are_preserved() -> None:
    document = minimal_document()
    document["subjects"] = [
        {"id": "subject_2"},
        {"id": "subject_1"},
    ]
    first = base_behavior()
    first["id"] = "behavior_2"
    first["subject"] = {"ref": "subject_2"}
    first["contexts"] = [
        _context("second"),
        _context("first"),
        _context("second"),
    ]
    second = base_behavior()
    document["behaviors"] = [first, second]

    canonical = canonicalize_document(document)

    assert [item["id"] for item in canonical["subjects"]] == [
        "subject_2",
        "subject_1",
    ]
    assert [item["id"] for item in canonical["behaviors"]] == [
        "behavior_2",
        "behavior_1",
    ]
    contexts = canonical["behaviors"][0]["contexts"]
    assert [item["value"]["value"] for item in contexts] == [
        "second",
        "first",
    ]


def test_input_is_immutable_and_canonicalization_is_idempotent() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = [
        _context("home"),
        _context("home"),
    ]
    behavior["annotations"] = []
    document["behaviors"] = [behavior]
    before = deepcopy(document)

    canonical = canonicalize_document(document)

    assert document == before
    assert canonicalize_document(canonical) == canonical


def test_post_normalization_document_remains_valid_at_all_existing_layers() -> None:
    from pbdl import (
        resolve_references,
        validate_document,
        validate_semantics,
    )

    document = _document_with_all_core_entities()
    document["behaviors"][0]["contexts"] = [
        _context("home"),
        _context("home"),
    ]
    document["relations"].append(
        deepcopy(document["relations"][0])
    )

    canonical = canonicalize_document(document)

    assert validate_document(canonical).valid is True
    assert resolve_references(canonical).valid is True
    assert validate_semantics(canonical).valid is True


def test_is_canonical_normal_form_distinguishes_normalization_needed_from_normal() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = []
    document["behaviors"] = [behavior]

    assert is_canonical_normal_form(document) is False
    canonical = canonicalize_document(document)
    assert is_canonical_normal_form(canonical) is True


def test_schema_invalid_input_is_not_repaired_by_canonicalizer() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["frequencies"] = [
        {
            "kind": "recurrence",
            "period": {"value": 1, "unit": "week"},
            "precision": "exact",
            "days_of_week": [],
        }
    ]
    document["behaviors"] = [behavior]

    with pytest.raises(CanonicalizationInputError) as captured:
        canonicalize_document(document)

    assert captured.value.schema_result is not None
    assert captured.value.resolution_result is None
    assert captured.value.semantic_result is None


def test_reference_invalid_input_preserves_resolution_result() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["subject"] = {"ref": "missing"}
    document["behaviors"] = [behavior]

    with pytest.raises(CanonicalizationInputError) as captured:
        canonicalize_document(document)

    assert captured.value.schema_result is None
    assert captured.value.resolution_result is not None
    assert captured.value.resolution_result.valid is False


def test_semantic_invalid_input_preserves_semantic_result() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["temporal"] = {
        "kind": "instant",
        "at": "2026-02-30",
    }
    document["behaviors"] = [behavior]

    with pytest.raises(CanonicalizationInputError) as captured:
        canonicalize_document(document)

    assert captured.value.schema_result is None
    assert captured.value.resolution_result is None
    assert captured.value.semantic_result is not None
    assert captured.value.semantic_result.valid is False


def test_local_provenance_empty_is_invalid_not_normalized_to_inheritance() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = [
        {
            "value": {"kind": "text", "value": "home"},
            "provenance": [],
        }
    ]
    document["behaviors"] = [behavior]

    with pytest.raises(CanonicalizationInputError):
        canonicalize_document(document)


def test_is_canonical_normal_form_raises_for_invalid_input_instead_of_returning_false() -> None:
    with pytest.raises(CanonicalizationInputError):
        is_canonical_normal_form({})

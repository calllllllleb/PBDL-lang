from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from pbdl import (
    ResolutionInputError,
    ResolutionResult,
    ResolutionViolation,
    are_references_valid,
    resolve_references,
)
from tests.helpers import (
    base_behavior,
    base_preference,
    base_relation,
    direct_provenance,
    minimal_document,
)


def _document_with_all_core_entities() -> dict[str, Any]:
    document = minimal_document()
    document["behaviors"] = [base_behavior()]
    document["preferences"] = [base_preference()]
    document["relations"] = [base_relation()]
    return document


def test_public_api_resolves_valid_document() -> None:
    result = resolve_references(_document_with_all_core_entities())

    assert result == ResolutionResult(valid=True, violations=())
    assert are_references_valid(_document_with_all_core_entities()) is True


def test_result_rejects_inconsistent_validity_flag() -> None:
    violation = ResolutionViolation(
        instance_path=("behaviors", 0, "subject", "ref"),
        kind="unresolved_reference",
        entity_id="missing",
        message="missing",
    )

    with pytest.raises(ValueError):
        ResolutionResult(valid=True, violations=(violation,))


@pytest.mark.parametrize(
    ("collection_name", "entity_factory"),
    [
        ("subjects", lambda: {"id": "duplicate"}),
        (
            "behaviors",
            lambda: {
                **base_behavior(),
                "id": "duplicate",
            },
        ),
        (
            "preferences",
            lambda: {
                **base_preference(),
                "id": "duplicate",
            },
        ),
    ],
)
def test_same_kind_duplicate_entity_ids_are_rejected(
    collection_name: str, entity_factory: Any
) -> None:
    document = minimal_document()

    if collection_name == "subjects":
        document["subjects"] = [{"id": "duplicate"}, entity_factory()]
    else:
        first = entity_factory()
        second = entity_factory()
        document[collection_name] = [first, second]

    result = resolve_references(document)
    duplicate_violations = [
        violation
        for violation in result.violations
        if violation.kind == "duplicate_entity_id"
    ]

    assert result.valid is False
    assert len(duplicate_violations) == 1
    assert duplicate_violations[0].entity_id == "duplicate"


@pytest.mark.parametrize(
    "pair",
    [
        "subject_behavior",
        "subject_preference",
        "behavior_preference",
    ],
)
def test_cross_kind_entity_id_collisions_are_rejected(pair: str) -> None:
    document = minimal_document()

    if pair == "subject_behavior":
        document["subjects"].append({"id": "shared"})
        behavior = base_behavior()
        behavior["id"] = "shared"
        document["behaviors"] = [behavior]
    elif pair == "subject_preference":
        document["subjects"].append({"id": "shared"})
        preference = base_preference()
        preference["id"] = "shared"
        document["preferences"] = [preference]
    else:
        behavior = base_behavior()
        behavior["id"] = "shared"
        preference = base_preference()
        preference["id"] = "shared"
        document["behaviors"] = [behavior]
        document["preferences"] = [preference]

    duplicate_violations = [
        violation
        for violation in resolve_references(document).violations
        if violation.kind == "duplicate_entity_id"
    ]

    assert len(duplicate_violations) == 1
    assert duplicate_violations[0].entity_id == "shared"


def test_duplicate_diagnostic_points_to_each_later_occurrence() -> None:
    document = minimal_document()
    document["subjects"] = [
        {"id": "shared"},
        {"id": "shared"},
        {"id": "shared"},
    ]

    duplicate_violations = [
        violation
        for violation in resolve_references(document).violations
        if violation.kind == "duplicate_entity_id"
    ]

    assert [violation.instance_path for violation in duplicate_violations] == [
        ("subjects", 1, "id"),
        ("subjects", 2, "id"),
    ]


@pytest.mark.parametrize("surface", ["behavior_subject", "preference_subject"])
def test_subject_reference_resolves_existing_subject(surface: str) -> None:
    document = minimal_document()

    if surface == "behavior_subject":
        document["behaviors"] = [base_behavior()]
    else:
        document["preferences"] = [base_preference()]

    assert are_references_valid(document) is True


@pytest.mark.parametrize("surface", ["behavior_subject", "preference_subject"])
def test_subject_reference_reports_missing_target(surface: str) -> None:
    document = minimal_document()

    if surface == "behavior_subject":
        entity = base_behavior()
        entity["subject"] = {"ref": "missing"}
        document["behaviors"] = [entity]
        expected_path = ("behaviors", 0, "subject", "ref")
    else:
        entity = base_preference()
        entity["subject"] = {"ref": "missing"}
        document["preferences"] = [entity]
        expected_path = ("preferences", 0, "subject", "ref")

    result = resolve_references(document)

    assert result.violations == (
        ResolutionViolation(
            instance_path=expected_path,
            kind="unresolved_reference",
            entity_id="missing",
            message="EntityId 'missing' does not exist in the document",
        ),
    )


@pytest.mark.parametrize(
    ("surface", "target_kind"),
    [
        ("behavior_subject", "behavior"),
        ("behavior_subject", "preference"),
        ("preference_subject", "behavior"),
        ("preference_subject", "preference"),
    ],
)
def test_subject_reference_reports_wrong_target_kind(
    surface: str, target_kind: str
) -> None:
    document = minimal_document()
    behavior = base_behavior()
    preference = base_preference()
    document["behaviors"] = [behavior]
    document["preferences"] = [preference]

    target_id = "behavior_1" if target_kind == "behavior" else "preference_1"
    if surface == "behavior_subject":
        behavior["subject"] = {"ref": target_id}
        expected_path = ("behaviors", 0, "subject", "ref")
    else:
        preference["subject"] = {"ref": target_id}
        expected_path = ("preferences", 0, "subject", "ref")

    violations = resolve_references(document).violations
    matching = [
        violation
        for violation in violations
        if violation.instance_path == expected_path
    ]

    assert len(matching) == 1
    assert matching[0].kind == "wrong_target_kind"
    assert matching[0].entity_id == target_id


def test_behavior_executor_subject_reference_resolves_subject() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["executor"] = {"ref": "subject_1"}
    document["behaviors"] = [behavior]

    assert are_references_valid(document) is True


@pytest.mark.parametrize(
    ("target_id", "expected_kind"),
    [
        ("missing", "unresolved_reference"),
        ("behavior_1", "wrong_target_kind"),
        ("preference_1", "wrong_target_kind"),
    ],
)
def test_behavior_executor_subject_reference_enforces_subject_target(
    target_id: str, expected_kind: str
) -> None:
    document = _document_with_all_core_entities()
    document["behaviors"][0]["executor"] = {"ref": target_id}

    matching = [
        violation
        for violation in resolve_references(document).violations
        if violation.instance_path == ("behaviors", 0, "executor", "ref")
    ]

    assert len(matching) == 1
    assert matching[0].kind == expected_kind


def test_external_actor_ref_does_not_enter_core_identity_namespace() -> None:
    document = minimal_document()
    first = base_behavior()
    second = base_behavior()
    second["id"] = "behavior_2"
    external_actor = {
        "kind": "person",
        "external_id": {"system": "example", "value": "doctor-1"},
    }
    first["executor"] = deepcopy(external_actor)
    second["executor"] = deepcopy(external_actor)
    document["behaviors"] = [first, second]

    assert resolve_references(document).valid is True


@pytest.mark.parametrize(
    ("source_id", "target_id"),
    [
        ("behavior_1", "behavior_1"),
        ("behavior_1", "preference_1"),
        ("preference_1", "behavior_1"),
        ("preference_1", "preference_1"),
    ],
)
def test_relation_core_entity_endpoint_combinations_are_not_over_constrained(
    source_id: str, target_id: str
) -> None:
    document = _document_with_all_core_entities()
    relation = base_relation()
    relation["source"] = {"ref": source_id}
    relation["target"] = {"ref": target_id}
    relation["type"] = {
        "system": "urn:example:unregistered-relation-system",
        "code": "arbitrary_relation_code",
    }
    document["relations"] = [relation]

    assert resolve_references(document).valid is True


@pytest.mark.parametrize("field_name", ["source", "target"])
def test_relation_endpoint_rejects_subject_target(field_name: str) -> None:
    document = _document_with_all_core_entities()
    document["relations"][0][field_name] = {"ref": "subject_1"}

    matching = [
        violation
        for violation in resolve_references(document).violations
        if violation.instance_path == ("relations", 0, field_name, "ref")
    ]

    assert len(matching) == 1
    assert matching[0].kind == "wrong_target_kind"


@pytest.mark.parametrize("field_name", ["source", "target"])
def test_relation_endpoint_reports_missing_target(field_name: str) -> None:
    document = _document_with_all_core_entities()
    document["relations"][0][field_name] = {"ref": "missing"}

    matching = [
        violation
        for violation in resolve_references(document).violations
        if violation.instance_path == ("relations", 0, field_name, "ref")
    ]

    assert len(matching) == 1
    assert matching[0].kind == "unresolved_reference"


def test_duplicate_identity_makes_subject_reference_ambiguous() -> None:
    document = minimal_document()
    document["subjects"].append({"id": "shared"})
    behavior = base_behavior()
    behavior["id"] = "shared"
    document["behaviors"] = [behavior]
    preference = base_preference()
    preference["subject"] = {"ref": "shared"}
    document["preferences"] = [preference]

    result = resolve_references(document)

    assert "duplicate_entity_id" in [item.kind for item in result.violations]
    ambiguous = [
        item
        for item in result.violations
        if item.instance_path == ("preferences", 0, "subject", "ref")
    ]
    assert len(ambiguous) == 1
    assert ambiguous[0].kind == "ambiguous_reference"


def test_duplicate_identity_makes_core_entity_reference_ambiguous() -> None:
    document = _document_with_all_core_entities()
    document["preferences"][0]["id"] = "behavior_1"
    document["relations"][0]["source"] = {"ref": "behavior_1"}
    document["relations"][0]["target"] = {"ref": "behavior_1"}

    result = resolve_references(document)

    assert "duplicate_entity_id" in [item.kind for item in result.violations]
    relation_violations = [
        item
        for item in result.violations
        if item.instance_path[:2] == ("relations", 0)
    ]
    assert len(relation_violations) == 2
    assert all(item.kind == "ambiguous_reference" for item in relation_violations)


def test_schema_invalid_input_stops_before_resolution() -> None:
    with pytest.raises(ResolutionInputError) as captured:
        resolve_references({})

    error = captured.value
    assert error.schema_result.valid is False
    assert error.schema_violations == error.schema_result.violations
    assert error.schema_violations


def test_boolean_helper_preserves_schema_precondition_failure() -> None:
    with pytest.raises(ResolutionInputError):
        are_references_valid({})


def test_resolution_diagnostics_are_deterministic() -> None:
    document = _document_with_all_core_entities()
    document["subjects"].append({"id": "behavior_1"})
    document["behaviors"][0]["subject"] = {"ref": "missing"}
    document["preferences"][0]["subject"] = {"ref": "behavior_1"}
    document["relations"][0]["source"] = {"ref": "subject_1"}
    document["relations"][0]["target"] = {"ref": "behavior_1"}

    first = resolve_references(document)
    second = resolve_references(document)

    assert first == second
    assert first.violations == second.violations


@pytest.mark.parametrize("valid_references", [True, False])
def test_resolution_never_mutates_input(valid_references: bool) -> None:
    document = _document_with_all_core_entities()
    if not valid_references:
        document["behaviors"][0]["subject"] = {"ref": "missing"}
    before = deepcopy(document)

    resolve_references(document)

    assert document == before


def test_temporal_calendar_semantics_are_not_implemented_by_resolver() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["temporal"] = {"kind": "instant", "at": "2026-02-30"}
    document["behaviors"] = [behavior]

    assert resolve_references(document).valid is True


def test_confidence_scale_semantics_are_not_implemented_by_resolver() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["provenance"][0]["confidence"] = {
        "value": 20,
        "metric": "example",
        "scale": {"min": 100, "max": 0},
    }
    document["behaviors"] = [behavior]

    assert resolve_references(document).valid is True


def test_resolver_does_not_canonicalize_duplicate_entities() -> None:
    document = minimal_document()
    duplicate = {"id": "subject_1"}
    document["subjects"].append(duplicate)
    before = deepcopy(document)

    result = resolve_references(document)

    assert result.valid is False
    assert document == before
    assert len(document["subjects"]) == 2


def test_external_actor_and_provenance_semantics_do_not_create_extra_resolution() -> None:
    document = minimal_document()
    behavior = base_behavior()
    behavior["executor"] = {
        "kind": "device",
        "external_id": {"system": "urn:example:device", "value": "device_1"},
        "display": "Reminder device",
    }
    behavior["provenance"] = [
        direct_provenance(),
        direct_provenance("clinician_documentation"),
    ]
    document["behaviors"] = [behavior]

    assert resolve_references(document).valid is True

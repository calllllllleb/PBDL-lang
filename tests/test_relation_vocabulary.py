from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from pbdl import (
    CanonicalizationInputError,
    RelationVocabulary,
    RelationVocabularyDefinitionError,
    VocabularyInputError,
    canonicalize_document,
    is_canonical_normal_form,
    is_relation_vocabulary_valid,
    validate_relation_vocabulary,
)
from tests.helpers import (
    base_behavior,
    base_preference,
    base_relation,
    minimal_document,
)


def _endpoint(kind: str, role: str) -> dict[str, str]:
    return {"kind": kind, "role": role}


def _entry(
    *,
    code: str = "example",
    directionality: str = "directional",
    version: str | None = None,
    inverse: dict[str, str] | None = None,
) -> dict[str, Any]:
    if directionality == "directional":
        signatures = [
            {
                "source": _endpoint("behavior", "behavior"),
                "target": _endpoint("preference", "preference"),
            }
        ]
    else:
        signatures = [
            {
                "endpoints": [
                    _endpoint("behavior", "behavior"),
                    _endpoint("preference", "preference"),
                ]
            }
        ]

    result: dict[str, Any] = {
        "system": "urn:example:relation",
        "code": code,
        "directionality": directionality,
        "endpoint_signatures": signatures,
        "causal_status": "non_causal",
    }
    if version is not None:
        result["version"] = version
    if inverse is not None:
        result["inverse"] = inverse
    return result


def _vocabulary(*entries: dict[str, Any]) -> RelationVocabulary:
    return RelationVocabulary.from_mapping({"entries": list(entries)})


def _behavior_preference_document(*, swapped: bool = False) -> dict[str, Any]:
    document = minimal_document()
    document["behaviors"] = [base_behavior()]
    document["preferences"] = [base_preference()]
    relation = base_relation()
    if swapped:
        relation["source"], relation["target"] = (
            relation["target"],
            relation["source"],
        )
    document["relations"] = [relation]
    return document


def _two_behavior_relation_document() -> dict[str, Any]:
    document = minimal_document()
    first = base_behavior()
    second = base_behavior()
    second["id"] = "behavior_2"
    document["behaviors"] = [first, second]

    relation = base_relation()
    relation["source"] = {"ref": "behavior_2"}
    relation["target"] = {"ref": "behavior_1"}
    swapped = deepcopy(relation)
    swapped["source"], swapped["target"] = (
        swapped["target"],
        swapped["source"],
    )
    document["relations"] = [relation, swapped]
    return document


def _malformed_registries() -> list[tuple[str, dict[str, Any]]]:
    directional = _entry()
    duplicate = deepcopy(directional)
    duplicate["version"] = "v2"

    bad_directionality = deepcopy(directional)
    bad_directionality["directionality"] = "unknown"

    bad_causal = deepcopy(directional)
    bad_causal["causal_status"] = "maybe_causal"

    empty_signatures = deepcopy(directional)
    empty_signatures["endpoint_signatures"] = []

    wrong_directional_shape = deepcopy(directional)
    wrong_directional_shape["endpoint_signatures"] = [
        {
            "endpoints": [
                _endpoint("behavior", "behavior"),
                _endpoint("preference", "preference"),
            ]
        }
    ]

    bad_kind = deepcopy(directional)
    bad_kind["endpoint_signatures"][0]["source"]["kind"] = "subject"

    blank_role = deepcopy(directional)
    blank_role["endpoint_signatures"][0]["source"]["role"] = "   "

    symmetric_roles = _entry(directionality="symmetric")
    symmetric_roles["endpoint_signatures"] = [
        {
            "endpoints": [
                _endpoint("behavior", "left"),
                _endpoint("behavior", "right"),
            ]
        }
    ]

    inverse_on_symmetric = _entry(directionality="symmetric")
    inverse_on_symmetric["inverse"] = {
        "system": "urn:example:relation",
        "code": "other",
    }

    self_inverse = _entry()
    self_inverse["inverse"] = {
        "system": "urn:example:relation",
        "code": "example",
    }

    unresolved_inverse = _entry(
        inverse={
            "system": "urn:example:relation",
            "code": "missing",
        }
    )

    inverse_version_mismatch = _entry(
        code="forward",
        inverse={
            "system": "urn:example:relation",
            "code": "reverse",
            "version": "v2",
        },
    )
    reverse = _entry(code="reverse", version="v1")

    return [
        ("duplicate_identity", {"entries": [directional, duplicate]}),
        ("directionality", {"entries": [bad_directionality]}),
        ("causal_status", {"entries": [bad_causal]}),
        ("empty_signatures", {"entries": [empty_signatures]}),
        ("directional_shape", {"entries": [wrong_directional_shape]}),
        ("endpoint_kind", {"entries": [bad_kind]}),
        ("blank_role", {"entries": [blank_role]}),
        ("same_kind_roles", {"entries": [symmetric_roles]}),
        ("inverse_non_directional", {"entries": [inverse_on_symmetric]}),
        ("inverse_self_reference", {"entries": [self_inverse]}),
        ("inverse_unresolved", {"entries": [unresolved_inverse]}),
        (
            "inverse_version_mismatch",
            {"entries": [inverse_version_mismatch, reverse]},
        ),
    ]


def test_malformed_relation_vocabulary_definitions_fail_closed() -> None:
    for _case, mapping in _malformed_registries():
        with pytest.raises(RelationVocabularyDefinitionError):
            RelationVocabulary.from_mapping(mapping)


def test_type_lookup_and_version_compatibility_are_vocabulary_conformance() -> None:
    unknown_document = _behavior_preference_document()
    unknown_vocabulary = _vocabulary()
    unknown = validate_relation_vocabulary(
        unknown_document,
        unknown_vocabulary,
    )

    assert unknown.valid is False
    assert [violation.kind for violation in unknown.violations] == [
        "unknown_relation_type"
    ]
    assert (
        is_relation_vocabulary_valid(
            unknown_document,
            unknown_vocabulary,
        )
        is False
    )

    version_document = _behavior_preference_document()
    version_document["relations"][0]["type"]["version"] = "v2"
    version_vocabulary = _vocabulary(_entry(version="v1"))
    mismatch = validate_relation_vocabulary(
        version_document,
        version_vocabulary,
    )

    assert mismatch.valid is False
    assert [violation.kind for violation in mismatch.violations] == [
        "relation_type_version_mismatch"
    ]


def test_directional_endpoint_signature_uses_source_target_order() -> None:
    vocabulary = _vocabulary(_entry(directionality="directional"))

    valid = validate_relation_vocabulary(
        _behavior_preference_document(swapped=False),
        vocabulary,
    )
    invalid = validate_relation_vocabulary(
        _behavior_preference_document(swapped=True),
        vocabulary,
    )

    assert valid.valid is True
    assert invalid.valid is False
    assert [violation.kind for violation in invalid.violations] == [
        "endpoint_signature_mismatch"
    ]


def test_unordered_endpoint_signature_accepts_both_document_orientations() -> None:
    for directionality in ("symmetric", "non_directional"):
        vocabulary = _vocabulary(_entry(directionality=directionality))

        forward = validate_relation_vocabulary(
            _behavior_preference_document(swapped=False),
            vocabulary,
        )
        swapped = validate_relation_vocabulary(
            _behavior_preference_document(swapped=True),
            vocabulary,
        )

        assert forward.valid is True
        assert swapped.valid is True


def test_vocabulary_validation_preserves_lower_layer_failures() -> None:
    vocabulary = _vocabulary()

    with pytest.raises(VocabularyInputError) as schema_error:
        validate_relation_vocabulary({}, vocabulary)
    assert schema_error.value.schema_result is not None
    assert schema_error.value.resolution_result is None
    assert schema_error.value.semantic_result is None

    semantic_invalid = minimal_document()
    behavior = base_behavior()
    behavior["temporal"] = {"kind": "instant", "at": "2023-02-29"}
    semantic_invalid["behaviors"] = [behavior]

    with pytest.raises(VocabularyInputError) as semantic_error:
        validate_relation_vocabulary(semantic_invalid, vocabulary)
    assert semantic_error.value.schema_result is None
    assert semantic_error.value.resolution_result is None
    assert semantic_error.value.semantic_result is not None


def test_canonicalizer_rejects_vocabulary_invalid_input_without_repair() -> None:
    document = _behavior_preference_document()
    vocabulary = _vocabulary()

    with pytest.raises(CanonicalizationInputError) as error:
        canonicalize_document(document, relation_vocabulary=vocabulary)

    assert error.value.vocabulary_result is not None
    assert error.value.vocabulary_result.valid is False
    assert error.value.schema_result is None
    assert error.value.resolution_result is None
    assert error.value.semantic_result is None


def test_symmetric_vocabulary_deduplicates_swapped_relations_stably() -> None:
    document = _two_behavior_relation_document()
    entry = _entry(directionality="symmetric")
    entry["endpoint_signatures"] = [
        {
            "endpoints": [
                _endpoint("behavior", "peer"),
                _endpoint("behavior", "peer"),
            ]
        }
    ]
    vocabulary = _vocabulary(entry)

    assert canonicalize_document(document) == document
    assert is_canonical_normal_form(
        document,
        relation_vocabulary=vocabulary,
    ) is False

    canonical = canonicalize_document(
        document,
        relation_vocabulary=vocabulary,
    )

    assert len(canonical["relations"]) == 1
    assert canonical["relations"][0]["source"]["ref"] == "behavior_2"
    assert canonical["relations"][0]["target"]["ref"] == "behavior_1"
    assert is_canonical_normal_form(
        canonical,
        relation_vocabulary=vocabulary,
    ) is True

    different_display = _two_behavior_relation_document()
    different_display["relations"][1]["type"]["display"] = "different"
    preserved = canonicalize_document(
        different_display,
        relation_vocabulary=vocabulary,
    )
    assert len(preserved["relations"]) == 2


def test_inverse_metadata_never_collapses_distinct_relation_types() -> None:
    document = minimal_document()
    first = base_behavior()
    second = base_behavior()
    second["id"] = "behavior_2"
    document["behaviors"] = [first, second]

    forward = base_relation()
    forward["source"] = {"ref": "behavior_1"}
    forward["target"] = {"ref": "behavior_2"}
    forward["type"] = {
        "system": "urn:example:relation",
        "code": "forward",
    }

    reverse = deepcopy(forward)
    reverse["source"], reverse["target"] = reverse["target"], reverse["source"]
    reverse["type"] = {
        "system": "urn:example:relation",
        "code": "reverse",
    }
    document["relations"] = [forward, reverse]

    forward_entry = _entry(
        code="forward",
        inverse={
            "system": "urn:example:relation",
            "code": "reverse",
        },
    )
    reverse_entry = _entry(
        code="reverse",
        inverse={
            "system": "urn:example:relation",
            "code": "forward",
        },
    )
    for entry in (forward_entry, reverse_entry):
        entry["endpoint_signatures"] = [
            {
                "source": _endpoint("behavior", "from"),
                "target": _endpoint("behavior", "to"),
            }
        ]
    vocabulary = _vocabulary(forward_entry, reverse_entry)

    canonical = canonicalize_document(
        document,
        relation_vocabulary=vocabulary,
    )

    assert len(canonical["relations"]) == 2
    assert [item["type"]["code"] for item in canonical["relations"]] == [
        "forward",
        "reverse",
    ]

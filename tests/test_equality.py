from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from pbdl import (
    DocumentEqualityInputError,
    RelationVocabulary,
    documents_canonically_equal,
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
    code: str,
    directionality: str,
    inverse: dict[str, str] | None = None,
) -> dict[str, Any]:
    if directionality == "directional":
        signatures = [
            {
                "source": _endpoint("behavior", "source"),
                "target": _endpoint("behavior", "target"),
            }
        ]
    else:
        signatures = [
            {
                "endpoints": [
                    _endpoint("behavior", "member"),
                    _endpoint("behavior", "member"),
                ]
            }
        ]

    entry: dict[str, Any] = {
        "system": "urn:example:relation",
        "code": code,
        "directionality": directionality,
        "endpoint_signatures": signatures,
        "causal_status": "non_causal",
    }
    if inverse is not None:
        entry["inverse"] = inverse
    return entry


def _vocabulary(*entries: dict[str, Any]) -> RelationVocabulary:
    return RelationVocabulary.from_mapping({"entries": list(entries)})


def _two_behavior_document(
    *, code: str = "peer", swapped: bool = False
) -> dict[str, Any]:
    document = minimal_document()
    first = base_behavior()
    second = deepcopy(first)
    second["id"] = "behavior_2"
    document["behaviors"] = [first, second]

    relation = base_relation()
    relation["source"] = {"ref": "behavior_1"}
    relation["target"] = {"ref": "behavior_2"}
    relation["type"] = {
        "system": "urn:example:relation",
        "code": code,
    }
    if swapped:
        relation["source"], relation["target"] = (
            relation["target"],
            relation["source"],
        )
    document["relations"] = [relation]
    return document


def _populated_document() -> dict[str, Any]:
    document = minimal_document()
    document["subjects"] = [{"id": "subject_1"}, {"id": "subject_2"}]

    first_behavior = base_behavior()
    second_behavior = deepcopy(first_behavior)
    second_behavior["id"] = "behavior_2"
    second_behavior["subject"] = {"ref": "subject_2"}
    document["behaviors"] = [first_behavior, second_behavior]

    first_preference = base_preference()
    second_preference = deepcopy(first_preference)
    second_preference["id"] = "preference_2"
    second_preference["subject"] = {"ref": "subject_2"}
    document["preferences"] = [first_preference, second_preference]

    first_relation = base_relation()
    second_relation = deepcopy(first_relation)
    second_relation["source"] = {"ref": "behavior_2"}
    second_relation["target"] = {"ref": "preference_2"}
    document["relations"] = [first_relation, second_relation]
    return document


def test_root_collection_order_is_ignored() -> None:
    left = _populated_document()
    right = deepcopy(left)
    for field in ("subjects", "behaviors", "preferences", "relations"):
        right[field].reverse()

    assert documents_canonically_equal(left, right) is True


def test_same_entity_identity_does_not_replace_full_information_equality() -> None:
    left = minimal_document()
    left["behaviors"] = [base_behavior()]
    right = deepcopy(left)
    right["behaviors"][0]["type"]["display"] = "different display"

    assert documents_canonically_equal(left, right) is False


def test_normalization_required_representation_equals_canonical_form() -> None:
    left = minimal_document()
    behavior = base_behavior()
    behavior["contexts"] = []
    left["behaviors"] = [behavior]

    right = minimal_document()
    right["behaviors"] = [base_behavior()]

    assert documents_canonically_equal(left, right) is True


def test_swapped_relation_is_not_assumed_equal_without_vocabulary() -> None:
    left = _two_behavior_document()
    right = _two_behavior_document(swapped=True)

    assert documents_canonically_equal(left, right) is False


@pytest.mark.parametrize("directionality", ["symmetric", "non_directional"])
def test_unordered_relation_types_allow_swapped_endpoints(
    directionality: str,
) -> None:
    vocabulary = _vocabulary(
        _entry(code="peer", directionality=directionality)
    )
    left = _two_behavior_document()
    right = _two_behavior_document(swapped=True)

    assert (
        documents_canonically_equal(
            left,
            right,
            relation_vocabulary=vocabulary,
        )
        is True
    )


@pytest.mark.parametrize("case", ["directional", "inverse"])
def test_directional_endpoint_order_and_inverse_type_remain_distinct(
    case: str,
) -> None:
    if case == "directional":
        vocabulary = _vocabulary(
            _entry(code="peer", directionality="directional")
        )
        left = _two_behavior_document()
        right = _two_behavior_document(swapped=True)
    else:
        vocabulary = _vocabulary(
            _entry(
                code="forward",
                directionality="directional",
                inverse={
                    "system": "urn:example:relation",
                    "code": "reverse",
                },
            ),
            _entry(
                code="reverse",
                directionality="directional",
                inverse={
                    "system": "urn:example:relation",
                    "code": "forward",
                },
            ),
        )
        left = _two_behavior_document(code="forward")
        right = _two_behavior_document(code="reverse", swapped=True)

    assert (
        documents_canonically_equal(
            left,
            right,
            relation_vocabulary=vocabulary,
        )
        is False
    )


@pytest.mark.parametrize("difference", ["version", "display"])
def test_vocabulary_lookup_does_not_weaken_relation_type_full_coding_equality(
    difference: str,
) -> None:
    vocabulary = _vocabulary(
        _entry(code="peer", directionality="symmetric")
    )
    left = _two_behavior_document()
    right = _two_behavior_document(swapped=True)
    if difference == "version":
        left["relations"][0]["type"]["version"] = "v1"
        right["relations"][0]["type"]["version"] = "v2"
    else:
        left["relations"][0]["type"]["display"] = "Peer A"
        right["relations"][0]["type"]["display"] = "Peer B"

    assert (
        documents_canonically_equal(
            left,
            right,
            relation_vocabulary=vocabulary,
        )
        is False
    )


@pytest.mark.parametrize("side", ["left", "right"])
def test_invalid_lower_layer_input_raises_with_side_and_original_result(
    side: str,
) -> None:
    valid = minimal_document()
    invalid = minimal_document()
    invalid_behavior = base_behavior()
    invalid_behavior["subject"] = {"ref": "missing_subject"}
    invalid["behaviors"] = [invalid_behavior]
    left, right = (invalid, valid) if side == "left" else (valid, invalid)

    with pytest.raises(DocumentEqualityInputError) as captured:
        documents_canonically_equal(left, right)

    error = captured.value
    assert error.side == side
    assert error.schema_result is None
    assert error.resolution_result is not None
    assert error.semantic_result is None
    assert error.vocabulary_result is None
    assert error.lower_layer_result is error.resolution_result


def test_vocabulary_invalid_input_is_not_converted_to_equality_false() -> None:
    vocabulary = _vocabulary(
        _entry(code="peer", directionality="symmetric")
    )
    valid = _two_behavior_document()
    invalid = deepcopy(valid)
    invalid["relations"][0]["type"]["code"] = "unknown"

    with pytest.raises(DocumentEqualityInputError) as captured:
        documents_canonically_equal(
            valid,
            invalid,
            relation_vocabulary=vocabulary,
        )

    error = captured.value
    assert error.side == "right"
    assert error.schema_result is None
    assert error.resolution_result is None
    assert error.semantic_result is None
    assert error.vocabulary_result is not None
    assert error.lower_layer_result is error.vocabulary_result

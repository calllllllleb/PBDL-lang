from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from pbdl import is_schema_valid, validate_document
from tests.helpers import (
    base_behavior,
    base_preference,
    base_relation,
    direct_provenance,
    document_with_behavior,
    document_with_preference,
    document_with_relation,
    generator_descriptor,
    minimal_document,
)


def _behavior_with_provenance(provenance: dict[str, Any]) -> dict[str, Any]:
    behavior = base_behavior()
    behavior["provenance"] = [provenance]
    return behavior


@pytest.mark.parametrize(
    ("executor", "expected"),
    [
        ({"kind": "person"}, True),
        ({"ref": "subject_1"}, True),
        ({"ref": "subject_1", "kind": "person"}, False),
    ],
)
def test_actor_reference_variants_are_structurally_exclusive(
    executor: dict[str, Any], expected: bool
) -> None:
    behavior = base_behavior()
    behavior["executor"] = executor

    assert is_schema_valid(document_with_behavior(behavior)) is expected


@pytest.mark.parametrize(
    ("evidence", "expected"),
    [
        ({"kind": "text_excerpt", "content": "evidence"}, True),
        ({"kind": "document_reference", "locator": "doc:1"}, True),
        (
            {
                "kind": "document_reference",
                "content": "evidence",
                "locator": "doc:1",
            },
            True,
        ),
        ({"kind": "other"}, False),
    ],
)
def test_evidence_allows_content_or_locator_or_both(
    evidence: dict[str, Any], expected: bool
) -> None:
    provenance = direct_provenance()
    provenance["evidence"] = [evidence]

    assert is_schema_valid(document_with_behavior(_behavior_with_provenance(provenance))) is expected


@pytest.mark.parametrize(
    ("provenance", "expected"),
    [
        (direct_provenance(), True),
        (
            {
                **direct_provenance(),
                "generator": generator_descriptor(),
            },
            True,
        ),
        ({"derivation": "direct"}, False),
        ({"derivation": "inferred", "generator": generator_descriptor()}, True),
        (
            {
                "derivation": "inferred",
                "source": {"kind": "patient_self_report"},
                "generator": generator_descriptor(),
            },
            True,
        ),
        (
            {
                "derivation": "inferred",
                "source": {"kind": "patient_self_report"},
            },
            False,
        ),
        (
            {
                "derivation": "undetermined",
                "source": {"kind": "other", "locator": "source:1"},
            },
            True,
        ),
        (
            {
                "derivation": "undetermined",
                "source": {"kind": "other"},
                "evidence": [{"kind": "text_excerpt", "content": "evidence"}],
            },
            True,
        ),
        (
            {
                "derivation": "undetermined",
                "source": {"kind": "other", "locator": "source:1"},
                "evidence": [{"kind": "text_excerpt", "content": "evidence"}],
            },
            True,
        ),
        (
            {
                "derivation": "undetermined",
                "source": {"kind": "other"},
            },
            False,
        ),
        (
            {
                "derivation": "undetermined",
                "source": {"kind": "other"},
                "evidence": [],
            },
            False,
        ),
    ],
)
def test_provenance_structural_conditions(
    provenance: dict[str, Any], expected: bool
) -> None:
    assert is_schema_valid(document_with_behavior(_behavior_with_provenance(provenance))) is expected


@pytest.mark.parametrize(
    ("temporal", "expected"),
    [
        ({"kind": "interval", "start": "2026-09"}, True),
        ({"kind": "interval", "end": "2026-10"}, True),
        ({"kind": "interval", "start": "2026-09", "end": "2026-10"}, True),
        ({"kind": "interval"}, False),
        ({"kind": "interval", "start": "2026-10", "end": "2026-09"}, True),
    ],
)
def test_interval_requires_at_least_one_endpoint_without_ordering_semantics(
    temporal: dict[str, Any], expected: bool
) -> None:
    behavior = base_behavior()
    behavior["temporal"] = temporal

    assert is_schema_valid(document_with_behavior(behavior)) is expected


@pytest.mark.parametrize(
    ("temporal", "expected"),
    [
        ({"kind": "instant", "at": "2026-09"}, True),
        ({"kind": "interval", "start": "2026-09"}, True),
        ({"kind": "unknown", "at": "2026-09"}, False),
        ({"kind": "instant", "at": "2026-09", "start": "2026-09"}, False),
    ],
)
def test_temporal_extent_union(temporal: dict[str, Any], expected: bool) -> None:
    behavior = base_behavior()
    behavior["temporal"] = temporal

    assert is_schema_valid(document_with_behavior(behavior)) is expected


@pytest.mark.parametrize(
    ("frequency", "expected"),
    [
        ({"kind": "observed_count", "count": 0, "precision": "exact"}, True),
        (
            {
                "kind": "rate",
                "value": 0,
                "period": {"value": 1, "unit": "day"},
                "precision": "approximate",
            },
            True,
        ),
        (
            {
                "kind": "recurrence",
                "period": {"value": 1, "unit": "week"},
                "precision": "exact",
            },
            True,
        ),
        ({"kind": "qualitative", "value": "often"}, True),
        ({"kind": "unknown", "value": "often"}, False),
        (
            {
                "kind": "observed_count",
                "count": 1,
                "precision": "exact",
                "value": 2,
                "period": {"value": 1, "unit": "day"},
            },
            False,
        ),
    ],
)
def test_behavior_frequency_union(frequency: dict[str, Any], expected: bool) -> None:
    behavior = base_behavior()
    behavior["frequencies"] = [frequency]

    assert is_schema_valid(document_with_behavior(behavior)) is expected


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        ({"days_of_week": ["mon", "wed"]}, True),
        ({"days_of_week": []}, False),
        ({"days_of_week": ["mon", "mon"]}, False),
        ({"days_of_week": ["mon"], "period": {"value": 1, "unit": "day"}}, False),
        ({"days_of_week": ["mon"], "period": {"value": 2, "unit": "week"}}, False),
        ({"days_of_week": ["mon"], "times_per_period": 1}, False),
        (
            {
                "period": {"value": 2, "unit": "day"},
                "times_per_period": 3,
            },
            True,
        ),
    ],
)
def test_recurrence_weekday_condition(updates: dict[str, Any], expected: bool) -> None:
    frequency: dict[str, Any] = {
        "kind": "recurrence",
        "period": {"value": 1, "unit": "week"},
        "precision": "exact",
    }
    frequency.update(updates)
    behavior = base_behavior()
    behavior["frequencies"] = [frequency]

    assert is_schema_valid(document_with_behavior(behavior)) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"kind": "coded", "value": {"system": "s", "code": "c"}}, True),
        ({"kind": "text", "value": "text"}, True),
        ({"kind": "boolean", "value": False}, True),
        ({"kind": "number", "operator": "eq", "value": 1}, True),
        ({"kind": "unknown", "value": "text"}, False),
        ({"kind": "coded", "value": "text"}, False),
    ],
)
def test_preference_value_union(value: dict[str, Any], expected: bool) -> None:
    preference = base_preference()
    preference["value"] = value

    assert is_schema_valid(document_with_preference(preference)) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"kind": "coded", "value": {"system": "s", "code": "c"}}, True),
        ({"kind": "text", "value": "text"}, True),
        ({"kind": "boolean", "value": False}, False),
        ({"kind": "coded", "value": "text"}, False),
    ],
)
def test_context_value_union(value: dict[str, Any], expected: bool) -> None:
    behavior = base_behavior()
    behavior["contexts"] = [{"value": value}]

    assert is_schema_valid(document_with_behavior(behavior)) is expected


@pytest.mark.parametrize(
    ("factor", "expected"),
    [
        ({"kind": "coded", "value": {"system": "s", "code": "c"}}, True),
        ({"kind": "text", "value": "text"}, True),
        ({"ref": "preference_1"}, False),
        ({"kind": "coded", "value": "text"}, False),
    ],
)
def test_factor_value_union(factor: dict[str, Any], expected: bool) -> None:
    behavior = base_behavior()
    behavior["factors"] = [
        {
            "role": "observed_association",
            "factor": factor,
            "direction": "unspecified",
        }
    ]

    assert is_schema_valid(document_with_behavior(behavior)) is expected


@pytest.mark.parametrize(
    ("role", "direction", "expected"),
    [
        ("reported_reason", "factor_to_behavior", True),
        ("reported_reason", "behavior_to_factor", False),
        ("reported_reason", "unspecified", False),
        ("antecedent", "factor_to_behavior", True),
        ("antecedent", "behavior_to_factor", False),
        ("antecedent", "unspecified", False),
        ("observed_association", "factor_to_behavior", True),
        ("observed_association", "behavior_to_factor", True),
        ("observed_association", "unspecified", True),
        ("explanatory", "factor_to_behavior", True),
        ("explanatory", "behavior_to_factor", True),
        ("explanatory", "unspecified", True),
    ],
)
def test_behavior_factor_direction_condition(
    role: str, direction: str, expected: bool
) -> None:
    behavior = base_behavior()
    behavior["factors"] = [
        {
            "role": role,
            "factor": {"kind": "text", "value": "factor"},
            "direction": direction,
        }
    ]

    assert is_schema_valid(document_with_behavior(behavior)) is expected


def test_unicode_white_space_boundary_on_coding_system() -> None:
    invalid_behavior = base_behavior()
    invalid_behavior["type"]["system"] = "\u0085"
    valid_behavior = base_behavior()
    valid_behavior["type"]["system"] = "\ufeff"

    # U+0085 属于规范冻结的 Unicode White_Space 集合，而 U+FEFF 不属于。
    # 这里通过正式 Schema 防止实现退化成语言运行时自己的空白字符近似。
    assert is_schema_valid(document_with_behavior(invalid_behavior)) is False
    assert is_schema_valid(document_with_behavior(valid_behavior)) is True


def test_unicode_white_space_boundary_on_annotation_text() -> None:
    invalid_behavior = base_behavior()
    invalid_behavior["annotations"] = [
        {"text": "\u0085", "provenance": [direct_provenance()]}
    ]
    valid_behavior = base_behavior()
    valid_behavior["annotations"] = [
        {"text": "\ufeff", "provenance": [direct_provenance()]}
    ]

    assert is_schema_valid(document_with_behavior(invalid_behavior)) is False
    assert is_schema_valid(document_with_behavior(valid_behavior)) is True


def _document_for_local_provenance(surface: str, state: str) -> dict[str, Any]:
    behavior = base_behavior()
    local = [direct_provenance()] if state == "nonempty" else []

    if surface == "temporal":
        value: dict[str, Any] = {"kind": "instant", "at": "2026-09"}
        if state != "omitted":
            value["provenance"] = local
        behavior["temporal"] = value
    elif surface == "frequency":
        value = {"kind": "qualitative", "value": "often"}
        if state != "omitted":
            value["provenance"] = local
        behavior["frequencies"] = [value]
    elif surface == "context":
        value = {"value": {"kind": "text", "value": "home"}}
        if state != "omitted":
            value["provenance"] = local
        behavior["contexts"] = [value]
    elif surface == "factor":
        value = {
            "role": "observed_association",
            "factor": {"kind": "text", "value": "support"},
            "direction": "unspecified",
        }
        if state != "omitted":
            value["provenance"] = local
        behavior["factors"] = [value]
    else:
        raise AssertionError(surface)
    return document_with_behavior(behavior)


@pytest.mark.parametrize("surface", ["temporal", "frequency", "context", "factor"])
@pytest.mark.parametrize(
    ("state", "expected"),
    [("omitted", True), ("nonempty", True), ("empty", False)],
)
def test_local_provenance_is_optional_but_nonempty_when_present(
    surface: str, state: str, expected: bool
) -> None:
    assert is_schema_valid(_document_for_local_provenance(surface, state)) is expected


def test_duplicate_entity_id_remains_schema_valid() -> None:
    document = minimal_document()
    document["subjects"] = [{"id": "subject_1"}, {"id": "subject_1"}]

    # 文档级 identity uniqueness 依赖跨实体解析，不是 JSON structural equality；
    # 结构验证层必须保留这个输入，交给独立的文档语义组件判断。
    assert is_schema_valid(document) is True


def test_unresolved_subject_reference_remains_schema_valid() -> None:
    behavior = base_behavior()
    behavior["subject"] = {"ref": "missing_subject"}

    # reference object 在这里仅检查结构和 EntityId 词法格式；
    # 被引用实体是否存在需要 document-wide resolution。
    assert is_schema_valid(document_with_behavior(behavior)) is True


def test_unresolved_core_entity_reference_remains_schema_valid() -> None:
    relation = base_relation()
    relation["source"] = {"ref": "missing_entity"}

    assert is_schema_valid(document_with_relation(relation)) is True


def test_impossible_gregorian_date_remains_schema_valid() -> None:
    behavior = base_behavior()
    behavior["temporal"] = {"kind": "instant", "at": "2026-02-30"}

    # 日期词法结构在这里检查；月份对应的真实天数需要日历语义，
    # 因此符合当前词法 profile 的 2026-02-30 仍应通过 Schema 层。
    assert is_schema_valid(document_with_behavior(behavior)) is True


def test_inverted_confidence_scale_remains_schema_valid() -> None:
    behavior = base_behavior()
    behavior["provenance"][0]["confidence"] = {
        "value": 20,
        "metric": "example",
        "scale": {"min": 100, "max": 0},
    }

    assert validate_document(document_with_behavior(behavior)).valid is True

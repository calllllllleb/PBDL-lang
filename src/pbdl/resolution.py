from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, cast

from .schema_validation import (
    PathSegment,
    SchemaValidationResult,
    _path_sort_key,
    validate_document,
)


ResolutionKind = Literal[
    "duplicate_entity_id",
    "unresolved_reference",
    "wrong_target_kind",
    "ambiguous_reference",
]
IdentityKind = Literal["subject", "behavior", "preference"]


class ResolutionInputError(ValueError):
    """Raised when reference resolution receives a schema-invalid document."""

    def __init__(self, schema_result: SchemaValidationResult) -> None:
        super().__init__(
            "reference resolution requires a document that passes schema validation"
        )
        self.schema_result = schema_result
        self.schema_violations = schema_result.violations


@dataclass(frozen=True, slots=True)
class ResolutionViolation:
    instance_path: tuple[PathSegment, ...]
    kind: str
    entity_id: str
    message: str


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    valid: bool
    violations: tuple[ResolutionViolation, ...]

    def __post_init__(self) -> None:
        if self.valid != (len(self.violations) == 0):
            raise ValueError("valid must be true exactly when violations is empty")


@dataclass(frozen=True, slots=True)
class _IdentityOccurrence:
    kind: IdentityKind
    instance_path: tuple[PathSegment, ...]


IdentityIndex = dict[str, tuple[_IdentityOccurrence, ...]]


def _build_identity_index(
    document: dict[str, Any],
) -> tuple[IdentityIndex, tuple[ResolutionViolation, ...]]:
    # Subject、Behavior 与 Preference 共享文档内 EntityId 命名空间。
    # 索引必须保留所有 collision，不能用普通 dict 覆盖后出现的实体。
    mutable_index: dict[str, list[_IdentityOccurrence]] = {}
    duplicates: list[ResolutionViolation] = []

    collections: tuple[tuple[str, IdentityKind], ...] = (
        ("subjects", "subject"),
        ("behaviors", "behavior"),
        ("preferences", "preference"),
    )
    for collection_name, entity_kind in collections:
        for index, entity in enumerate(document[collection_name]):
            entity_id = entity["id"]
            occurrence = _IdentityOccurrence(
                kind=entity_kind,
                instance_path=(collection_name, index),
            )
            bucket = mutable_index.setdefault(entity_id, [])
            if bucket:
                duplicates.append(
                    ResolutionViolation(
                        instance_path=(collection_name, index, "id"),
                        kind="duplicate_entity_id",
                        entity_id=entity_id,
                        message=(
                            f"EntityId {entity_id!r} is duplicated in the shared "
                            "document-local namespace"
                        ),
                    )
                )
            bucket.append(occurrence)

    return (
        {entity_id: tuple(items) for entity_id, items in mutable_index.items()},
        tuple(duplicates),
    )


def _reference_violation(
    *,
    index: IdentityIndex,
    entity_id: str,
    instance_path: tuple[PathSegment, ...],
    expected_kinds: frozenset[IdentityKind],
    expected_description: str,
) -> ResolutionViolation | None:
    matches = index.get(entity_id, ())
    if not matches:
        return ResolutionViolation(
            instance_path=instance_path,
            kind="unresolved_reference",
            entity_id=entity_id,
            message=f"EntityId {entity_id!r} does not exist in the document",
        )

    # 重复 EntityId 会让引用失去唯一目标。这里不能采用 first-wins，
    # 否则会把非法文档悄悄解释成一个看似确定的对象图。
    if len(matches) > 1:
        return ResolutionViolation(
            instance_path=instance_path,
            kind="ambiguous_reference",
            entity_id=entity_id,
            message=(
                f"EntityId {entity_id!r} has {len(matches)} identity-bearing "
                "occurrences and cannot resolve exactly one target"
            ),
        )

    actual_kind = matches[0].kind
    if actual_kind not in expected_kinds:
        return ResolutionViolation(
            instance_path=instance_path,
            kind="wrong_target_kind",
            entity_id=entity_id,
            message=(
                f"EntityId {entity_id!r} resolves to {actual_kind}, "
                f"but this reference requires {expected_description}"
            ),
        )
    return None


def _resolve_subject_references(
    document: dict[str, Any], index: IdentityIndex
) -> list[ResolutionViolation]:
    violations: list[ResolutionViolation] = []
    subject_kinds: frozenset[IdentityKind] = frozenset({"subject"})

    for item_index, behavior in enumerate(document["behaviors"]):
        # SubjectRef 不只是“某个存在的 EntityId”；目标必须是 Subject。
        # 因此存在但指向其他实体类型与完全不存在是不同的 resolution failure。
        subject_id = behavior["subject"]["ref"]
        violation = _reference_violation(
            index=index,
            entity_id=subject_id,
            instance_path=("behaviors", item_index, "subject", "ref"),
            expected_kinds=subject_kinds,
            expected_description="a Subject",
        )
        if violation is not None:
            violations.append(violation)

        executor = behavior.get("executor")
        if executor is not None and "ref" in executor:
            executor_id = executor["ref"]
            violation = _reference_violation(
                index=index,
                entity_id=executor_id,
                instance_path=("behaviors", item_index, "executor", "ref"),
                expected_kinds=subject_kinds,
                expected_description="a Subject",
            )
            if violation is not None:
                violations.append(violation)
        # ExternalActorRef 是嵌入式 actor descriptor，不属于 Core EntityId 命名空间。
        # external_id 可表达外部身份，但不能参与 PBDL Core reference resolution。

    for item_index, preference in enumerate(document["preferences"]):
        subject_id = preference["subject"]["ref"]
        violation = _reference_violation(
            index=index,
            entity_id=subject_id,
            instance_path=("preferences", item_index, "subject", "ref"),
            expected_kinds=subject_kinds,
            expected_description="a Subject",
        )
        if violation is not None:
            violations.append(violation)

    return violations


def _resolve_relation_references(
    document: dict[str, Any], index: IdentityIndex
) -> list[ResolutionViolation]:
    violations: list[ResolutionViolation] = []
    core_entity_kinds: frozenset[IdentityKind] = frozenset(
        {"behavior", "preference"}
    )

    for relation_index, relation in enumerate(document["relations"]):
        # CoreEntityRef 只要求目标是 Behavior 或 Preference；Subject 被明确排除。
        # 具体 relation code 对 endpoint role 的约束属于关系语义，不在通用 resolver 中判断。
        for field_name in ("source", "target"):
            entity_id = relation[field_name]["ref"]
            violation = _reference_violation(
                index=index,
                entity_id=entity_id,
                instance_path=("relations", relation_index, field_name, "ref"),
                expected_kinds=core_entity_kinds,
                expected_description="a Behavior or Preference",
            )
            if violation is not None:
                violations.append(violation)

    return violations


def _violation_sort_key(
    violation: ResolutionViolation,
) -> tuple[
    tuple[tuple[int, int | str], ...],
    str,
    str,
    str,
]:
    return (
        _path_sort_key(violation.instance_path),
        violation.kind,
        violation.entity_id,
        violation.message,
    )


def resolve_references(document: object) -> ResolutionResult:
    # 结构无效的输入必须停在 Schema 边界；继续解析会迫使 resolver
    # 重复处理缺字段、错误类型、非法 union 等已经有唯一责任归属的问题。
    schema_result = validate_document(document)
    if not schema_result.valid:
        raise ResolutionInputError(schema_result)

    # Schema 已证明根对象与各必需 collection 的结构，因此下面只读取引用相关字段。
    # 整个过程不回填 target、不排序原数组，也不执行任何 canonicalization。
    validated_document = cast(dict[str, Any], document)
    index, duplicate_violations = _build_identity_index(validated_document)

    violations = list(duplicate_violations)
    violations.extend(_resolve_subject_references(validated_document, index))
    violations.extend(_resolve_relation_references(validated_document, index))
    ordered = tuple(sorted(violations, key=_violation_sort_key))

    return ResolutionResult(valid=not ordered, violations=ordered)


def are_references_valid(document: object) -> bool:
    return resolve_references(document).valid

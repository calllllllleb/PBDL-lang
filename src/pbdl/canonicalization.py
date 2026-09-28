from __future__ import annotations

from copy import deepcopy
from functools import partial
from typing import Any, Callable, TypeVar, cast

from .semantic_validation import (
    SemanticInputError,
    SemanticValidationResult,
    validate_semantics,
)
from .relation_vocabulary import (
    RelationVocabulary,
    VocabularyInputError,
    VocabularyValidationResult,
    validate_relation_vocabulary,
)


T = TypeVar("T")
EqualFn = Callable[[T, T], bool]


class CanonicalizationInputError(ValueError):
    """Raised when canonicalization receives input invalid at an earlier layer."""

    def __init__(
        self,
        *,
        schema_result: object | None = None,
        resolution_result: object | None = None,
        semantic_result: SemanticValidationResult | None = None,
        vocabulary_result: VocabularyValidationResult | None = None,
    ) -> None:
        results = [
            schema_result,
            resolution_result,
            semantic_result,
            vocabulary_result,
        ]
        if sum(result is not None for result in results) != 1:
            raise ValueError("exactly one validation result must be provided")
        if schema_result is not None:
            message = "canonicalization requires a schema-valid document"
            validation_result = schema_result
        elif resolution_result is not None:
            message = "canonicalization requires a reference-valid document"
            validation_result = resolution_result
        elif semantic_result is not None:
            message = "canonicalization requires a semantic-valid document"
            validation_result = semantic_result
        else:
            message = "canonicalization requires a vocabulary-valid document"
            validation_result = vocabulary_result
        super().__init__(message)
        self.schema_result = schema_result
        self.resolution_result = resolution_result
        self.semantic_result = semantic_result
        self.vocabulary_result = vocabulary_result
        self.validation_result = validation_result
        self.lower_layer_result = validation_result


def _optional_scalar_equal(
    left: dict[str, Any], right: dict[str, Any], field: str
) -> bool:
    if (field in left) != (field in right):
        return False
    return field not in left or left[field] == right[field]


def _collection_equal(
    left: list[T], right: list[T], equal: EqualFn[T]
) -> bool:
    if len(left) != len(right):
        return False
    matched = [False] * len(right)
    for left_item in left:
        for index, right_item in enumerate(right):
            if not matched[index] and equal(left_item, right_item):
                matched[index] = True
                break
        else:
            return False
    return True


def _stable_deduplicate(items: list[T], equal: EqualFn[T]) -> list[T]:
    # Collection semantics 是 order-insensitive，但当前规范没有冻结排序。
    # 因此只稳定删除 full-equal redundancy，并保留第一个 survivor 与原有顺序。
    survivors: list[T] = []
    for item in items:
        if not any(equal(item, existing) for existing in survivors):
            survivors.append(item)
    return survivors


def _coding_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["system"] == right["system"]
        and left["code"] == right["code"]
        and _optional_scalar_equal(left, right, "version")
        and _optional_scalar_equal(left, right, "display")
    )


def _confidence_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["metric"] != right["metric"] or left["value"] != right["value"]:
        return False
    if ("scale" in left) != ("scale" in right):
        return False
    if "scale" not in left:
        return True
    return (
        left["scale"]["min"] == right["scale"]["min"]
        and left["scale"]["max"] == right["scale"]["max"]
    )


def _time_event_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left["role"] == right["role"] and left["at"] == right["at"]


def _optional_times_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if ("times" in left) != ("times" in right):
        return False
    if "times" not in left:
        return True
    return _collection_equal(left["times"], right["times"], _time_event_equal)


def _source_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["kind"] == right["kind"]
        and _optional_scalar_equal(left, right, "locator")
        and _optional_scalar_equal(left, right, "display")
        and _optional_times_equal(left, right)
    )


def _generator_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["kind"] == right["kind"]
        and _optional_scalar_equal(left, right, "identifier")
        and _optional_scalar_equal(left, right, "version")
        and _optional_scalar_equal(left, right, "display")
        and _optional_times_equal(left, right)
    )


def _evidence_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["kind"] == right["kind"]
        and _optional_scalar_equal(left, right, "content")
        and _optional_scalar_equal(left, right, "locator")
        and _optional_times_equal(left, right)
    )


def _optional_object_equal(
    left: dict[str, Any],
    right: dict[str, Any],
    field: str,
    equal: Callable[[dict[str, Any], dict[str, Any]], bool],
) -> bool:
    if (field in left) != (field in right):
        return False
    return field not in left or equal(left[field], right[field])


def _provenance_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["derivation"] != right["derivation"]:
        return False
    if not _optional_object_equal(left, right, "source", _source_equal):
        return False
    if not _optional_object_equal(left, right, "generator", _generator_equal):
        return False

    left_evidence = left.get("evidence", [])
    right_evidence = right.get("evidence", [])
    if not _collection_equal(left_evidence, right_evidence, _evidence_equal):
        return False

    return _optional_object_equal(left, right, "confidence", _confidence_equal)


def _provenance_collection_equal(
    left: list[dict[str, Any]], right: list[dict[str, Any]]
) -> bool:
    return _collection_equal(left, right, _provenance_equal)


def _canonicalize_times(owner: dict[str, Any]) -> None:
    if "times" not in owner:
        return
    if not owner["times"]:
        del owner["times"]
        return
    owner["times"] = _stable_deduplicate(owner["times"], _time_event_equal)


def _canonicalize_evidence(evidence: dict[str, Any]) -> None:
    _canonicalize_times(evidence)


def _canonicalize_provenance(provenance: dict[str, Any]) -> None:
    if "source" in provenance:
        _canonicalize_times(provenance["source"])
    if "generator" in provenance:
        _canonicalize_times(provenance["generator"])

    if "evidence" in provenance:
        if not provenance["evidence"]:
            del provenance["evidence"]
        else:
            for evidence in provenance["evidence"]:
                _canonicalize_evidence(evidence)
            provenance["evidence"] = _stable_deduplicate(
                provenance["evidence"], _evidence_equal
            )


def _canonicalize_provenance_collection(
    collection: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    for provenance in collection:
        _canonicalize_provenance(provenance)
    return _stable_deduplicate(collection, _provenance_equal)


def _effective_provenance(
    qualifier: dict[str, Any], inherited: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return qualifier.get("provenance", inherited)


def _canonicalize_local_provenance(
    qualifier: dict[str, Any], inherited: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if "provenance" not in qualifier:
        return inherited

    local = _canonicalize_provenance_collection(qualifier["provenance"])
    # local provenance 是 complete override，而不是 inherited + local 的 additive merge。
    # 只有 complete local set 与直接 owner 的 effective set 等价时才能省略。
    if _provenance_collection_equal(local, inherited):
        del qualifier["provenance"]
        return inherited

    qualifier["provenance"] = local
    return local


def _temporal_content_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["kind"] != right["kind"]:
        return False
    if left["kind"] == "instant":
        return left["at"] == right["at"]
    return (
        _optional_scalar_equal(left, right, "start")
        and _optional_scalar_equal(left, right, "end")
    )


def _temporal_full_equal(
    left: dict[str, Any],
    left_inherited: list[dict[str, Any]],
    right: dict[str, Any],
    right_inherited: list[dict[str, Any]],
) -> bool:
    return _temporal_content_equal(left, right) and _provenance_collection_equal(
        _effective_provenance(left, left_inherited),
        _effective_provenance(right, right_inherited),
    )


def _canonicalize_temporal_extent(
    extent: dict[str, Any], inherited: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return _canonicalize_local_provenance(extent, inherited)


def _context_content_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_value = left["value"]
    right_value = right["value"]
    if left_value["kind"] != right_value["kind"]:
        return False
    if left_value["kind"] == "coded":
        return _coding_equal(left_value["value"], right_value["value"])
    return left_value["value"] == right_value["value"]


def _factor_content_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["role"] != right["role"] or left["direction"] != right["direction"]:
        return False
    left_factor = left["factor"]
    right_factor = right["factor"]
    if left_factor["kind"] != right_factor["kind"]:
        return False
    if left_factor["kind"] == "coded":
        return _coding_equal(left_factor["value"], right_factor["value"])
    return left_factor["value"] == right_factor["value"]


def _period_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left["value"] == right["value"] and left["unit"] == right["unit"]


def _optional_numeric_equal(
    left: dict[str, Any], right: dict[str, Any], field: str
) -> bool:
    return _optional_scalar_equal(left, right, field)


def _frequency_content_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["kind"] != right["kind"]:
        return False

    kind = left["kind"]
    if kind == "observed_count":
        if left["count"] != right["count"] or left["precision"] != right["precision"]:
            return False
        if ("window" in left) != ("window" in right):
            return False
        return "window" not in left or _temporal_content_equal(
            left["window"], right["window"]
        )

    if kind == "rate":
        return (
            left["value"] == right["value"]
            and _period_equal(left["period"], right["period"])
            and left["precision"] == right["precision"]
        )

    if kind == "recurrence":
        if not (
            _period_equal(left["period"], right["period"])
            and left["precision"] == right["precision"]
            and _optional_numeric_equal(left, right, "times_per_period")
            and _optional_scalar_equal(left, right, "day_part")
        ):
            return False
        if ("days_of_week" in left) != ("days_of_week" in right):
            return False
        return "days_of_week" not in left or set(left["days_of_week"]) == set(
            right["days_of_week"]
        )

    return left["value"] == right["value"]


def _frequency_full_equal(
    left: dict[str, Any],
    left_effective: list[dict[str, Any]],
    right: dict[str, Any],
    right_effective: list[dict[str, Any]],
) -> bool:
    if not _frequency_content_equal(left, right):
        return False
    if not _provenance_collection_equal(left_effective, right_effective):
        return False
    if left["kind"] == "observed_count" and "window" in left:
        return _temporal_full_equal(
            left["window"],
            left_effective,
            right["window"],
            right_effective,
        )
    return True


def _preference_value_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["kind"] != right["kind"]:
        return False
    kind = left["kind"]
    if kind == "coded":
        return _coding_equal(left["value"], right["value"])
    if kind in {"text", "boolean"}:
        return left["value"] == right["value"]
    return (
        left["operator"] == right["operator"]
        and left["value"] == right["value"]
        and _optional_object_equal(left, right, "unit", _coding_equal)
    )


def _canonicalize_annotation(annotation: dict[str, Any]) -> None:
    annotation["provenance"] = _canonicalize_provenance_collection(
        annotation["provenance"]
    )


def _annotation_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left["text"] == right["text"] and _provenance_collection_equal(
        left["provenance"], right["provenance"]
    )


def _canonicalize_annotations(owner: dict[str, Any]) -> None:
    if "annotations" not in owner:
        return
    if not owner["annotations"]:
        del owner["annotations"]
        return
    for annotation in owner["annotations"]:
        _canonicalize_annotation(annotation)
    owner["annotations"] = _stable_deduplicate(
        owner["annotations"], _annotation_equal
    )


def _canonicalize_frequency(
    frequency: dict[str, Any], inherited: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    effective = _canonicalize_local_provenance(frequency, inherited)
    if frequency["kind"] == "observed_count" and "window" in frequency:
        # window 的直接 owner 是 Frequency；必须继承 Frequency 的 effective provenance，
        # 不能越级回到 Behavior provenance。
        _canonicalize_temporal_extent(frequency["window"], effective)
    return effective


def _canonicalize_context_or_factor(
    qualifier: dict[str, Any], inherited: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return _canonicalize_local_provenance(qualifier, inherited)


def _deduplicate_qualifiers(
    pairs: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    content_equal: Callable[[dict[str, Any], dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    survivors: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    for item, effective in pairs:
        duplicate = False
        for existing, existing_effective in survivors:
            if content_equal(item, existing) and _provenance_collection_equal(
                effective, existing_effective
            ):
                duplicate = True
                break
        if not duplicate:
            survivors.append((item, effective))
    return [item for item, _ in survivors]


def _canonicalize_behavior(behavior: dict[str, Any]) -> None:
    behavior["provenance"] = _canonicalize_provenance_collection(
        behavior["provenance"]
    )
    owner_provenance = behavior["provenance"]

    if "temporal" in behavior:
        _canonicalize_temporal_extent(behavior["temporal"], owner_provenance)

    if "frequencies" in behavior:
        if not behavior["frequencies"]:
            del behavior["frequencies"]
        else:
            pairs: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
            for frequency in behavior["frequencies"]:
                effective = _canonicalize_frequency(frequency, owner_provenance)
                pairs.append((frequency, effective))
            survivors: list[
                tuple[dict[str, Any], list[dict[str, Any]]]
            ] = []
            for frequency, effective in pairs:
                if not any(
                    _frequency_full_equal(
                        frequency,
                        effective,
                        existing,
                        existing_effective,
                    )
                    for existing, existing_effective in survivors
                ):
                    survivors.append((frequency, effective))
            behavior["frequencies"] = [item for item, _ in survivors]

    if "contexts" in behavior:
        if not behavior["contexts"]:
            del behavior["contexts"]
        else:
            context_pairs = [
                (
                    context,
                    _canonicalize_context_or_factor(
                        context, owner_provenance
                    ),
                )
                for context in behavior["contexts"]
            ]
            behavior["contexts"] = _deduplicate_qualifiers(
                context_pairs, _context_content_equal
            )

    if "factors" in behavior:
        if not behavior["factors"]:
            del behavior["factors"]
        else:
            factor_pairs = [
                (
                    factor,
                    _canonicalize_context_or_factor(
                        factor, owner_provenance
                    ),
                )
                for factor in behavior["factors"]
            ]
            behavior["factors"] = _deduplicate_qualifiers(
                factor_pairs, _factor_content_equal
            )

    _canonicalize_annotations(behavior)


def _canonicalize_preference(preference: dict[str, Any]) -> None:
    preference["provenance"] = _canonicalize_provenance_collection(
        preference["provenance"]
    )
    owner_provenance = preference["provenance"]

    if "temporal" in preference:
        _canonicalize_temporal_extent(preference["temporal"], owner_provenance)

    if "contexts" in preference:
        if not preference["contexts"]:
            del preference["contexts"]
        else:
            pairs = [
                (
                    context,
                    _canonicalize_context_or_factor(
                        context, owner_provenance
                    ),
                )
                for context in preference["contexts"]
            ]
            preference["contexts"] = _deduplicate_qualifiers(
                pairs, _context_content_equal
            )

    _canonicalize_annotations(preference)


def _relation_equal(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    relation_vocabulary: RelationVocabulary | None = None,
) -> bool:
    # Relation.type 的完整 Coding 信息始终先比较；vocabulary lookup 只使用
    # system + code，不能弱化 version/display 对 full equality 的影响。
    if not _coding_equal(left["type"], right["type"]):
        return False

    directionality = (
        None
        if relation_vocabulary is None
        else relation_vocabulary.directionality_for(left["type"])
    )
    if directionality in {"symmetric", "non_directional"}:
        same_endpoints = (
            left["source"]["ref"] == right["source"]["ref"]
            and left["target"]["ref"] == right["target"]["ref"]
        )
        swapped_endpoints = (
            left["source"]["ref"] == right["target"]["ref"]
            and left["target"]["ref"] == right["source"]["ref"]
        )
        if not (same_endpoints or swapped_endpoints):
            return False
    else:
        # 无 vocabulary 或 directional entry 时保持既有保守行为。
        if left["source"]["ref"] != right["source"]["ref"]:
            return False
        if left["target"]["ref"] != right["target"]["ref"]:
            return False
    if ("temporal" in left) != ("temporal" in right):
        return False
    if "temporal" in left and not _temporal_full_equal(
        left["temporal"],
        left["provenance"],
        right["temporal"],
        right["provenance"],
    ):
        return False
    if not _provenance_collection_equal(
        left["provenance"], right["provenance"]
    ):
        return False
    left_annotations = left.get("annotations", [])
    right_annotations = right.get("annotations", [])
    return _collection_equal(
        left_annotations, right_annotations, _annotation_equal
    )


def _canonicalize_relation(relation: dict[str, Any]) -> None:
    relation["provenance"] = _canonicalize_provenance_collection(
        relation["provenance"]
    )
    if "temporal" in relation:
        _canonicalize_temporal_extent(
            relation["temporal"], relation["provenance"]
        )
    _canonicalize_annotations(relation)


def _canonicalize_valid_document(
    document: dict[str, Any],
    *,
    relation_vocabulary: RelationVocabulary | None = None,
) -> dict[str, Any]:
    canonical = deepcopy(document)

    # Identity-bearing root collections 保持原顺序且绝不 dedup；其冲突已经由 resolver 拒绝。
    for behavior in canonical["behaviors"]:
        _canonicalize_behavior(behavior)
    for preference in canonical["preferences"]:
        _canonicalize_preference(preference)

    for relation in canonical["relations"]:
        _canonicalize_relation(relation)
    relation_equal: EqualFn[dict[str, Any]]
    if relation_vocabulary is None:
        relation_equal = _relation_equal
    else:
        relation_equal = partial(
            _relation_equal,
            relation_vocabulary=relation_vocabulary,
        )
    canonical["relations"] = _stable_deduplicate(
        canonical["relations"], relation_equal
    )

    return canonical


def _canonicalization_error_from_vocabulary_input(
    error: VocabularyInputError,
) -> CanonicalizationInputError:
    if error.schema_result is not None:
        return CanonicalizationInputError(schema_result=error.schema_result)
    if error.resolution_result is not None:
        return CanonicalizationInputError(
            resolution_result=error.resolution_result
        )
    return CanonicalizationInputError(semantic_result=error.semantic_result)


def canonicalize_document(
    document: object,
    *,
    relation_vocabulary: RelationVocabulary | None = None,
) -> dict[str, Any]:
    if relation_vocabulary is None:
        try:
            semantic_result = validate_semantics(document)
        except SemanticInputError as error:
            if error.schema_result is not None:
                raise CanonicalizationInputError(
                    schema_result=error.schema_result
                ) from error
            raise CanonicalizationInputError(
                resolution_result=error.resolution_result
            ) from error

        if not semantic_result.valid:
            raise CanonicalizationInputError(
                semantic_result=semantic_result
            )
    else:
        try:
            vocabulary_result = validate_relation_vocabulary(
                document, relation_vocabulary
            )
        except VocabularyInputError as error:
            raise _canonicalization_error_from_vocabulary_input(error) from error
        if not vocabulary_result.valid:
            raise CanonicalizationInputError(
                vocabulary_result=vocabulary_result
            )

    canonical = _canonicalize_valid_document(
        cast(dict[str, Any], document),
        relation_vocabulary=relation_vocabulary,
    )

    # Normalization 只能删除表示冗余；有 vocabulary 时还必须保持 VOCABULARY-valid。
    if relation_vocabulary is None:
        try:
            post_result = validate_semantics(canonical)
        except SemanticInputError as error:
            raise RuntimeError(
                "canonicalization produced a lower-layer-invalid document"
            ) from error
        if not post_result.valid:
            raise RuntimeError(
                "canonicalization produced a semantic-invalid document"
            )
    else:
        try:
            post_vocabulary_result = validate_relation_vocabulary(
                canonical, relation_vocabulary
            )
        except VocabularyInputError as error:
            raise RuntimeError(
                "canonicalization produced a lower-layer-invalid document"
            ) from error
        if not post_vocabulary_result.valid:
            raise RuntimeError(
                "canonicalization produced a vocabulary-invalid document"
            )

    return canonical


def is_canonical_normal_form(
    document: object,
    *,
    relation_vocabulary: RelationVocabulary | None = None,
) -> bool:
    canonical = canonicalize_document(
        document,
        relation_vocabulary=relation_vocabulary,
    )
    # dict member order 与 collection sorting 都不属于当前 normal form；
    # canonicalizer 只稳定删除冗余，不执行 endpoint sorting。
    return canonical == document

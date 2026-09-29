from __future__ import annotations

from functools import partial
from typing import Any, Callable, Literal

from .canonicalization import (
    CanonicalizationInputError,
    _annotation_equal,
    _coding_equal,
    _collection_equal,
    _context_content_equal,
    _effective_provenance,
    _factor_content_equal,
    _frequency_full_equal,
    _optional_object_equal,
    _optional_scalar_equal,
    _preference_value_equal,
    _provenance_collection_equal,
    _relation_equal,
    _temporal_full_equal,
    canonicalize_document,
)
from .relation_vocabulary import (
    RelationVocabulary,
    VocabularyValidationResult,
)
from .resolution import ResolutionResult
from .schema_validation import SchemaValidationResult
from .semantic_validation import SemanticValidationResult


DocumentSide = Literal["left", "right"]


class DocumentEqualityInputError(ValueError):
    """Raised when document equality receives invalid input on either side."""

    def __init__(
        self,
        *,
        side: DocumentSide,
        schema_result: SchemaValidationResult | None = None,
        resolution_result: ResolutionResult | None = None,
        semantic_result: SemanticValidationResult | None = None,
        vocabulary_result: VocabularyValidationResult | None = None,
    ) -> None:
        if side not in {"left", "right"}:
            raise ValueError("side must be 'left' or 'right'")
        results = [
            schema_result,
            resolution_result,
            semantic_result,
            vocabulary_result,
        ]
        if sum(result is not None for result in results) != 1:
            raise ValueError("exactly one validation result must be provided")

        if schema_result is not None:
            layer = "schema"
            validation_result = schema_result
        elif resolution_result is not None:
            layer = "reference"
            validation_result = resolution_result
        elif semantic_result is not None:
            layer = "semantic"
            validation_result = semantic_result
        else:
            layer = "vocabulary"
            validation_result = vocabulary_result

        super().__init__(
            f"document equality requires a {layer}-valid {side} document"
        )
        self.side = side
        self.schema_result = schema_result
        self.resolution_result = resolution_result
        self.semantic_result = semantic_result
        self.vocabulary_result = vocabulary_result
        self.validation_result = validation_result
        self.lower_layer_result = validation_result


def _equality_input_error(
    side: DocumentSide,
    error: CanonicalizationInputError,
) -> DocumentEqualityInputError:
    return DocumentEqualityInputError(
        side=side,
        schema_result=error.schema_result,
        resolution_result=error.resolution_result,
        semantic_result=error.semantic_result,
        vocabulary_result=error.vocabulary_result,
    )


def _external_id_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left["system"] == right["system"] and left["value"] == right["value"]


def _actor_ref_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_is_subject = "ref" in left
    right_is_subject = "ref" in right
    if left_is_subject != right_is_subject:
        return False
    if left_is_subject:
        return left["ref"] == right["ref"]

    return (
        left["kind"] == right["kind"]
        and _optional_object_equal(
            left,
            right,
            "external_id",
            _external_id_equal,
        )
        and _optional_scalar_equal(left, right, "display")
        and _optional_scalar_equal(left, right, "role")
    )


def _optional_temporal_equal(
    left: dict[str, Any],
    right: dict[str, Any],
    left_owner_provenance: list[dict[str, Any]],
    right_owner_provenance: list[dict[str, Any]],
) -> bool:
    if ("temporal" in left) != ("temporal" in right):
        return False
    return "temporal" not in left or _temporal_full_equal(
        left["temporal"],
        left_owner_provenance,
        right["temporal"],
        right_owner_provenance,
    )


def _qualifier_full_equal(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    left_owner_provenance: list[dict[str, Any]],
    right_owner_provenance: list[dict[str, Any]],
    content_equal: Callable[[dict[str, Any], dict[str, Any]], bool],
) -> bool:
    return content_equal(left, right) and _provenance_collection_equal(
        _effective_provenance(left, left_owner_provenance),
        _effective_provenance(right, right_owner_provenance),
    )


def _behavior_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["id"] != right["id"]:
        return False
    if left["subject"]["ref"] != right["subject"]["ref"]:
        return False
    if not _coding_equal(left["type"], right["type"]):
        return False
    if not _optional_object_equal(left, right, "executor", _actor_ref_equal):
        return False

    left_provenance = left["provenance"]
    right_provenance = right["provenance"]
    if not _provenance_collection_equal(left_provenance, right_provenance):
        return False
    if not _optional_temporal_equal(
        left,
        right,
        left_provenance,
        right_provenance,
    ):
        return False

    def frequency_equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
        return _frequency_full_equal(
            a,
            _effective_provenance(a, left_provenance),
            b,
            _effective_provenance(b, right_provenance),
        )

    if not _collection_equal(
        left.get("frequencies", []),
        right.get("frequencies", []),
        frequency_equal,
    ):
        return False

    context_equal = partial(
        _qualifier_full_equal,
        left_owner_provenance=left_provenance,
        right_owner_provenance=right_provenance,
        content_equal=_context_content_equal,
    )
    if not _collection_equal(
        left.get("contexts", []),
        right.get("contexts", []),
        context_equal,
    ):
        return False

    factor_equal = partial(
        _qualifier_full_equal,
        left_owner_provenance=left_provenance,
        right_owner_provenance=right_provenance,
        content_equal=_factor_content_equal,
    )
    if not _collection_equal(
        left.get("factors", []),
        right.get("factors", []),
        factor_equal,
    ):
        return False

    return _collection_equal(
        left.get("annotations", []),
        right.get("annotations", []),
        _annotation_equal,
    )


def _preference_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["id"] != right["id"]:
        return False
    if left["subject"]["ref"] != right["subject"]["ref"]:
        return False
    if not _coding_equal(left["category"], right["category"]):
        return False
    if not _preference_value_equal(left["value"], right["value"]):
        return False

    left_provenance = left["provenance"]
    right_provenance = right["provenance"]
    if not _provenance_collection_equal(left_provenance, right_provenance):
        return False
    if not _optional_temporal_equal(
        left,
        right,
        left_provenance,
        right_provenance,
    ):
        return False

    context_equal = partial(
        _qualifier_full_equal,
        left_owner_provenance=left_provenance,
        right_owner_provenance=right_provenance,
        content_equal=_context_content_equal,
    )
    if not _collection_equal(
        left.get("contexts", []),
        right.get("contexts", []),
        context_equal,
    ):
        return False

    return _collection_equal(
        left.get("annotations", []),
        right.get("annotations", []),
        _annotation_equal,
    )


def _identity_collection_equal(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
    equal: Callable[[dict[str, Any], dict[str, Any]], bool],
) -> bool:
    if len(left) != len(right):
        return False
    right_by_id = {item["id"]: item for item in right}
    if len(right_by_id) != len(right):
        return False
    return all(
        (candidate := right_by_id.get(item["id"])) is not None
        and equal(item, candidate)
        for item in left
    )


def _subject_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left["id"] == right["id"]


def _canonical_documents_equal(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    relation_vocabulary: RelationVocabulary | None,
) -> bool:
    if left["pbdl_version"] != right["pbdl_version"]:
        return False
    if not _identity_collection_equal(
        left["subjects"], right["subjects"], _subject_equal
    ):
        return False
    if not _identity_collection_equal(
        left["behaviors"], right["behaviors"], _behavior_equal
    ):
        return False
    if not _identity_collection_equal(
        left["preferences"], right["preferences"], _preference_equal
    ):
        return False

    relation_equal = (
        _relation_equal
        if relation_vocabulary is None
        else partial(
            _relation_equal,
            relation_vocabulary=relation_vocabulary,
        )
    )
    return _collection_equal(
        left["relations"], right["relations"], relation_equal
    )


def documents_canonically_equal(
    left: object,
    right: object,
    *,
    relation_vocabulary: RelationVocabulary | None = None,
) -> bool:
    """Return whether two valid PBDL documents carry the same canonical information."""

    try:
        canonical_left = canonicalize_document(
            left,
            relation_vocabulary=relation_vocabulary,
        )
    except CanonicalizationInputError as error:
        raise _equality_input_error("left", error) from error

    try:
        canonical_right = canonicalize_document(
            right,
            relation_vocabulary=relation_vocabulary,
        )
    except CanonicalizationInputError as error:
        raise _equality_input_error("right", error) from error

    return _canonical_documents_equal(
        canonical_left,
        canonical_right,
        relation_vocabulary=relation_vocabulary,
    )

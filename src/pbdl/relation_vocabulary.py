from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, cast

from .schema_validation import (
    PathSegment,
    SchemaValidationResult,
    _path_sort_key,
)
from .resolution import ResolutionResult
from .semantic_validation import (
    SemanticInputError,
    SemanticValidationResult,
    validate_semantics,
)


Directionality = Literal["directional", "symmetric", "non_directional"]
EndpointKind = Literal["behavior", "preference"]
CausalStatus = Literal["causal", "non_causal"]


class RelationVocabularyDefinitionError(ValueError):
    """Raised when a relation vocabulary registry violates the frozen contract."""


class VocabularyInputError(ValueError):
    """Raised when vocabulary validation receives invalid lower-layer input."""

    def __init__(
        self,
        *,
        schema_result: SchemaValidationResult | None = None,
        resolution_result: ResolutionResult | None = None,
        semantic_result: SemanticValidationResult | None = None,
    ) -> None:
        results = [schema_result, resolution_result, semantic_result]
        if sum(result is not None for result in results) != 1:
            raise ValueError("exactly one lower-layer result must be provided")
        if schema_result is not None:
            message = "vocabulary validation requires a schema-valid document"
            validation_result = schema_result
        elif resolution_result is not None:
            message = "vocabulary validation requires a reference-valid document"
            validation_result = resolution_result
        else:
            message = "vocabulary validation requires a semantic-valid document"
            validation_result = semantic_result
        super().__init__(message)
        self.schema_result = schema_result
        self.resolution_result = resolution_result
        self.semantic_result = semantic_result
        self.validation_result = validation_result
        self.lower_layer_result = validation_result


@dataclass(frozen=True, slots=True)
class VocabularyViolation:
    instance_path: tuple[PathSegment, ...]
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class VocabularyValidationResult:
    valid: bool
    violations: tuple[VocabularyViolation, ...]

    def __post_init__(self) -> None:
        if self.valid != (len(self.violations) == 0):
            raise ValueError("valid must be true exactly when violations is empty")


@dataclass(frozen=True, slots=True)
class _Endpoint:
    kind: EndpointKind
    role: str


@dataclass(frozen=True, slots=True)
class _DirectionalSignature:
    source: _Endpoint
    target: _Endpoint


@dataclass(frozen=True, slots=True)
class _UnorderedSignature:
    endpoints: tuple[_Endpoint, _Endpoint]


EndpointSignature = _DirectionalSignature | _UnorderedSignature


@dataclass(frozen=True, slots=True)
class _RelationTypeRef:
    system: str
    code: str
    version: str | None


@dataclass(frozen=True, slots=True)
class _RelationTypeEntry:
    system: str
    code: str
    version: str | None
    directionality: Directionality
    endpoint_signatures: tuple[EndpointSignature, ...]
    causal_status: CausalStatus
    inverse: _RelationTypeRef | None
    display: str | None
    description: str | None


def _is_unicode_white_space(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x0009 <= codepoint <= 0x000D
        or codepoint
        in {
            0x0020,
            0x0085,
            0x00A0,
            0x1680,
            0x2028,
            0x2029,
            0x202F,
            0x205F,
            0x3000,
        }
        or 0x2000 <= codepoint <= 0x200A
    )


def _is_nonblank(value: object) -> bool:
    return isinstance(value, str) and any(
        not _is_unicode_white_space(char) for char in value
    )


def _definition_error(message: str) -> RelationVocabularyDefinitionError:
    return RelationVocabularyDefinitionError(message)


def _require_mapping(value: object, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _definition_error(f"{context} must be a mapping")
    return cast(Mapping[str, Any], value)


def _require_nonblank_string(value: object, *, context: str) -> str:
    if not _is_nonblank(value):
        raise _definition_error(f"{context} must be a nonblank string")
    return cast(str, value)


def _optional_string(
    mapping: Mapping[str, Any],
    field: str,
    *,
    context: str,
) -> str | None:
    if field not in mapping:
        return None
    value = mapping[field]
    if not isinstance(value, str):
        raise _definition_error(f"{context}.{field} must be a string")
    return value


def _parse_endpoint(value: object, *, context: str) -> _Endpoint:
    mapping = _require_mapping(value, context=context)
    if set(mapping) != {"kind", "role"}:
        raise _definition_error(
            f"{context} must contain exactly kind and role"
        )

    kind = mapping["kind"]
    if kind not in {"behavior", "preference"}:
        raise _definition_error(
            f"{context}.kind must be behavior or preference"
        )
    role = _require_nonblank_string(mapping["role"], context=f"{context}.role")
    return _Endpoint(kind=cast(EndpointKind, kind), role=role)


def _parse_signatures(
    value: object,
    *,
    entry_index: int,
    directionality: Directionality,
) -> tuple[EndpointSignature, ...]:
    if not isinstance(value, list) or not value:
        raise _definition_error(
            f"entries[{entry_index}].endpoint_signatures must be a nonempty list"
        )

    signatures: list[EndpointSignature] = []
    for signature_index, raw_signature in enumerate(value):
        context = (
            f"entries[{entry_index}].endpoint_signatures[{signature_index}]"
        )
        signature = _require_mapping(raw_signature, context=context)

        if directionality == "directional":
            if set(signature) != {"source", "target"}:
                raise _definition_error(
                    f"{context} must contain exactly source and target "
                    "for a directional relation type"
                )
            signatures.append(
                _DirectionalSignature(
                    source=_parse_endpoint(
                        signature["source"], context=f"{context}.source"
                    ),
                    target=_parse_endpoint(
                        signature["target"], context=f"{context}.target"
                    ),
                )
            )
            continue

        if set(signature) != {"endpoints"}:
            raise _definition_error(
                f"{context} must contain exactly endpoints "
                "for a symmetric or non_directional relation type"
            )
        raw_endpoints = signature["endpoints"]
        if not isinstance(raw_endpoints, list) or len(raw_endpoints) != 2:
            raise _definition_error(
                f"{context}.endpoints must contain exactly two endpoint descriptors"
            )
        first = _parse_endpoint(
            raw_endpoints[0], context=f"{context}.endpoints[0]"
        )
        second = _parse_endpoint(
            raw_endpoints[1], context=f"{context}.endpoints[1]"
        )
        if first.kind == second.kind and first.role != second.role:
            raise _definition_error(
                f"{context} uses different roles for endpoints of the same kind"
            )
        signatures.append(_UnorderedSignature(endpoints=(first, second)))

    return tuple(signatures)


def _parse_inverse(
    value: object,
    *,
    entry_index: int,
) -> _RelationTypeRef:
    context = f"entries[{entry_index}].inverse"
    mapping = _require_mapping(value, context=context)
    if not {"system", "code"}.issubset(mapping):
        raise _definition_error(f"{context} requires system and code")
    if not set(mapping).issubset({"system", "code", "version"}):
        raise _definition_error(
            f"{context} may contain only system, code, and version"
        )
    return _RelationTypeRef(
        system=_require_nonblank_string(
            mapping["system"], context=f"{context}.system"
        ),
        code=_require_nonblank_string(
            mapping["code"], context=f"{context}.code"
        ),
        version=(
            _require_nonblank_string(
                mapping["version"], context=f"{context}.version"
            )
            if "version" in mapping
            else None
        ),
    )


def _parse_entry(value: object, *, entry_index: int) -> _RelationTypeEntry:
    context = f"entries[{entry_index}]"
    mapping = _require_mapping(value, context=context)

    required = {
        "system",
        "code",
        "directionality",
        "endpoint_signatures",
        "causal_status",
    }
    missing = required.difference(mapping)
    if missing:
        joined = ", ".join(sorted(missing))
        raise _definition_error(f"{context} is missing required fields: {joined}")

    system = _require_nonblank_string(
        mapping["system"], context=f"{context}.system"
    )
    code = _require_nonblank_string(mapping["code"], context=f"{context}.code")
    version = (
        _require_nonblank_string(
            mapping["version"], context=f"{context}.version"
        )
        if "version" in mapping
        else None
    )

    directionality_value = mapping["directionality"]
    if directionality_value not in {
        "directional",
        "symmetric",
        "non_directional",
    }:
        raise _definition_error(
            f"{context}.directionality must be directional, symmetric, "
            "or non_directional"
        )
    directionality = cast(Directionality, directionality_value)

    causal_value = mapping["causal_status"]
    if causal_value not in {"causal", "non_causal"}:
        raise _definition_error(
            f"{context}.causal_status must be causal or non_causal"
        )
    causal_status = cast(CausalStatus, causal_value)

    inverse = None
    if "inverse" in mapping:
        if directionality != "directional":
            raise _definition_error(
                f"{context}.inverse is allowed only for directional entries"
            )
        inverse = _parse_inverse(mapping["inverse"], entry_index=entry_index)
        if (inverse.system, inverse.code) == (system, code):
            raise _definition_error(
                f"{context}.inverse must not self-reference the same system + code"
            )

    return _RelationTypeEntry(
        system=system,
        code=code,
        version=version,
        directionality=directionality,
        endpoint_signatures=_parse_signatures(
            mapping["endpoint_signatures"],
            entry_index=entry_index,
            directionality=directionality,
        ),
        causal_status=causal_status,
        inverse=inverse,
        display=_optional_string(mapping, "display", context=context),
        description=_optional_string(mapping, "description", context=context),
    )


@dataclass(frozen=True, slots=True, init=False)
class RelationVocabulary:
    """Immutable runtime representation of the PBDL relation vocabulary contract."""

    _entries: tuple[_RelationTypeEntry, ...]

    def __init__(self) -> None:
        raise TypeError("use RelationVocabulary.from_mapping()")

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> RelationVocabulary:
        registry = _require_mapping(mapping, context="relation vocabulary")

        if "pbdl_version" in registry and registry["pbdl_version"] != "1.0":
            raise _definition_error(
                "relation vocabulary pbdl_version must be exactly '1.0'"
            )
        raw_entries = registry.get("entries")
        if not isinstance(raw_entries, list):
            raise _definition_error("relation vocabulary entries must be a list")

        entries = tuple(
            _parse_entry(value, entry_index=index)
            for index, value in enumerate(raw_entries)
        )

        by_identity: dict[tuple[str, str], _RelationTypeEntry] = {}
        for entry in entries:
            identity = (entry.system, entry.code)
            if identity in by_identity:
                raise _definition_error(
                    "duplicate relation vocabulary system + code: "
                    f"{entry.system!r} + {entry.code!r}"
                )
            by_identity[identity] = entry

        for entry in entries:
            inverse = entry.inverse
            if inverse is None:
                continue
            target = by_identity.get((inverse.system, inverse.code))
            if target is None:
                raise _definition_error(
                    "inverse relation type does not resolve by system + code: "
                    f"{inverse.system!r} + {inverse.code!r}"
                )
            if (
                inverse.version is not None
                and target.version is not None
                and inverse.version != target.version
            ):
                raise _definition_error(
                    "inverse relation type version is incompatible with "
                    "the resolved entry version"
                )

        instance = object.__new__(cls)
        object.__setattr__(instance, "_entries", entries)
        return instance

    def _entry_for(
        self, system: str, code: str
    ) -> _RelationTypeEntry | None:
        for entry in self._entries:
            if entry.system == system and entry.code == code:
                return entry
        return None

    def directionality_for(
        self, coding: Mapping[str, Any]
    ) -> Directionality | None:
        entry = self._entry_for(
            cast(str, coding["system"]),
            cast(str, coding["code"]),
        )
        return None if entry is None else entry.directionality


def _endpoint_kind_index(document: dict[str, Any]) -> dict[str, EndpointKind]:
    index: dict[str, EndpointKind] = {}
    for behavior in document["behaviors"]:
        index[behavior["id"]] = "behavior"
    for preference in document["preferences"]:
        index[preference["id"]] = "preference"
    return index


def _signature_matches(
    entry: _RelationTypeEntry,
    source_kind: EndpointKind,
    target_kind: EndpointKind,
) -> bool:
    if entry.directionality == "directional":
        return any(
            isinstance(signature, _DirectionalSignature)
            and signature.source.kind == source_kind
            and signature.target.kind == target_kind
            for signature in entry.endpoint_signatures
        )

    return any(
        isinstance(signature, _UnorderedSignature)
        and (
            (
                signature.endpoints[0].kind == source_kind
                and signature.endpoints[1].kind == target_kind
            )
            or (
                signature.endpoints[0].kind == target_kind
                and signature.endpoints[1].kind == source_kind
            )
        )
        for signature in entry.endpoint_signatures
    )


def _violation_sort_key(
    violation: VocabularyViolation,
) -> tuple[tuple[tuple[int, int | str], ...], str, str]:
    return (
        _path_sort_key(violation.instance_path),
        violation.kind,
        violation.message,
    )


def validate_relation_vocabulary(
    document: object,
    vocabulary: RelationVocabulary,
) -> VocabularyValidationResult:
    if not isinstance(vocabulary, RelationVocabulary):
        raise TypeError("vocabulary must be a RelationVocabulary")

    # VOCABULARY 是独立于 document-intrinsic SEMANTIC 的符合性层。
    # lower-layer failure 必须保留真实结果，不能改写成 vocabulary violation。
    try:
        semantic_result = validate_semantics(document)
    except SemanticInputError as error:
        if error.schema_result is not None:
            raise VocabularyInputError(
                schema_result=error.schema_result
            ) from error
        raise VocabularyInputError(
            resolution_result=error.resolution_result
        ) from error
    if not semantic_result.valid:
        raise VocabularyInputError(semantic_result=semantic_result)

    validated_document = cast(dict[str, Any], document)
    endpoint_kinds = _endpoint_kind_index(validated_document)
    violations: list[VocabularyViolation] = []

    for relation_index, relation in enumerate(validated_document["relations"]):
        relation_type = relation["type"]
        entry = vocabulary._entry_for(
            relation_type["system"],
            relation_type["code"],
        )
        type_path: tuple[PathSegment, ...] = (
            "relations",
            relation_index,
            "type",
        )

        if entry is None:
            violations.append(
                VocabularyViolation(
                    instance_path=type_path,
                    kind="unknown_relation_type",
                    message=(
                        "Relation.type does not resolve to a relation "
                        "vocabulary entry by system + code"
                    ),
                )
            )
            continue

        relation_version = relation_type.get("version")
        if (
            relation_version is not None
            and entry.version is not None
            and relation_version != entry.version
        ):
            violations.append(
                VocabularyViolation(
                    instance_path=type_path + ("version",),
                    kind="relation_type_version_mismatch",
                    message=(
                        "Relation.type.version is incompatible with the "
                        "resolved vocabulary entry version"
                    ),
                )
            )

        source_kind = endpoint_kinds[relation["source"]["ref"]]
        target_kind = endpoint_kinds[relation["target"]["ref"]]
        if not _signature_matches(entry, source_kind, target_kind):
            violations.append(
                VocabularyViolation(
                    instance_path=("relations", relation_index),
                    kind="endpoint_signature_mismatch",
                    message=(
                        "resolved Relation endpoint kinds do not match any "
                        "allowed endpoint signature for Relation.type"
                    ),
                )
            )

    ordered = tuple(sorted(violations, key=_violation_sort_key))
    return VocabularyValidationResult(valid=not ordered, violations=ordered)


def is_relation_vocabulary_valid(
    document: object,
    vocabulary: RelationVocabulary,
) -> bool:
    return validate_relation_vocabulary(document, vocabulary).valid

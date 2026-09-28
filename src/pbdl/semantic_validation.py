from __future__ import annotations

import calendar
import math
import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal, cast

from .resolution import ResolutionInputError, ResolutionResult, resolve_references
from .schema_validation import PathSegment, SchemaValidationResult, _path_sort_key


_NANOSECONDS_PER_SECOND = 1_000_000_000
_SECONDS_PER_DAY = 86_400
_DATETIME_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T(?P<hour>\d{2}):(?P<minute>\d{2})"
    r"(?::(?P<second>\d{2})(?:\.(?P<fraction>\d{1,9}))?)?"
    r"(?P<zone>Z(?:\[[A-Za-z0-9._+/-]+\])?"
    r"|[+-]\d{2}:\d{2}(?:\[[A-Za-z0-9._+/-]+\])?"
    r"|\[[A-Za-z0-9._+/-]+\])?$"
)


class SemanticInputError(ValueError):
    """Raised when semantic validation receives invalid lower-layer input."""

    def __init__(
        self,
        *,
        schema_result: SchemaValidationResult | None = None,
        resolution_result: ResolutionResult | None = None,
    ) -> None:
        if (schema_result is None) == (resolution_result is None):
            raise ValueError("exactly one lower-layer result must be provided")
        if schema_result is not None:
            message = "semantic validation requires a schema-valid document"
        else:
            message = "semantic validation requires a reference-valid document"
        super().__init__(message)
        self.schema_result = schema_result
        self.resolution_result = resolution_result
        self.lower_layer_result = (
            schema_result if schema_result is not None else resolution_result
        )


@dataclass(frozen=True, slots=True)
class SemanticViolation:
    instance_path: tuple[PathSegment, ...]
    kind: str
    message: str


@dataclass(frozen=True, slots=True)
class SemanticValidationResult:
    valid: bool
    violations: tuple[SemanticViolation, ...]

    def __post_init__(self) -> None:
        if self.valid != (len(self.violations) == 0):
            raise ValueError("valid must be true exactly when violations is empty")


@dataclass(frozen=True, slots=True)
class _TemporalRange:
    family: Literal["date", "datetime"]
    earliest: int
    latest: int
    mode: Literal["date", "local", "offset", "zone_only"]


def _is_finite_number(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    try:
        return math.isfinite(value)  # type: ignore[arg-type]
    except (TypeError, OverflowError, ValueError):
        return False


def _calendar_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _date_family_range(value: str) -> _TemporalRange | None:
    parts = value.split("-")
    year = int(parts[0])
    if len(parts) == 1:
        return _TemporalRange(
            family="date",
            earliest=date(year, 1, 1).toordinal(),
            latest=date(year, 12, 31).toordinal(),
            mode="date",
        )

    month = int(parts[1])
    if len(parts) == 2:
        last_day = calendar.monthrange(year, month)[1]
        return _TemporalRange(
            family="date",
            earliest=date(year, month, 1).toordinal(),
            latest=date(year, month, last_day).toordinal(),
            mode="date",
        )

    day_value = _calendar_date(year, month, int(parts[2]))
    if day_value is None:
        return None
    ordinal = day_value.toordinal()
    return _TemporalRange("date", ordinal, ordinal, "date")


def _zone_mode_and_offset(
    zone: str | None,
) -> tuple[Literal["local", "offset", "zone_only"], int]:
    if zone is None:
        return ("local", 0)
    if zone.startswith("["):
        return ("zone_only", 0)

    numeric = zone.split("[", 1)[0]
    if numeric == "Z":
        return ("offset", 0)

    sign = 1 if numeric[0] == "+" else -1
    hours = int(numeric[1:3])
    minutes = int(numeric[4:6])
    return ("offset", sign * (hours * 60 + minutes))


def _datetime_family_range(value: str) -> _TemporalRange | None:
    match = _DATETIME_RE.fullmatch(value)
    if match is None:
        raise RuntimeError("schema-valid TemporalValue is outside the semantic parser")

    year = int(match.group("year"))
    month = int(match.group("month"))
    day = int(match.group("day"))
    day_value = _calendar_date(year, month, day)
    if day_value is None:
        return None

    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    second_text = match.group("second")
    fraction = match.group("fraction")

    if second_text is None:
        earliest_second = 0
        latest_second = 59
        earliest_fraction = 0
        latest_fraction = _NANOSECONDS_PER_SECOND - 1
    else:
        earliest_second = latest_second = int(second_text)
        if fraction is None:
            earliest_fraction = 0
            latest_fraction = _NANOSECONDS_PER_SECOND - 1
        else:
            place = 10 ** (9 - len(fraction))
            earliest_fraction = int(fraction) * place
            latest_fraction = earliest_fraction + place - 1

    day_base_seconds = day_value.toordinal() * _SECONDS_PER_DAY
    minute_base_seconds = day_base_seconds + hour * 3600 + minute * 60
    earliest = (
        (minute_base_seconds + earliest_second) * _NANOSECONDS_PER_SECOND
        + earliest_fraction
    )
    latest = (
        (minute_base_seconds + latest_second) * _NANOSECONDS_PER_SECOND
        + latest_fraction
    )

    mode, offset_minutes = _zone_mode_and_offset(match.group("zone"))
    if mode == "offset":
        offset_ns = offset_minutes * 60 * _NANOSECONDS_PER_SECOND
        earliest -= offset_ns
        latest -= offset_ns

    return _TemporalRange("datetime", earliest, latest, mode)


def _temporal_range(value: str) -> _TemporalRange | None:
    if "T" in value:
        return _datetime_family_range(value)
    return _date_family_range(value)


def _validate_temporal_value(
    value: str,
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> _TemporalRange | None:
    temporal_range = _temporal_range(value)
    if temporal_range is None:
        violations.append(
            SemanticViolation(
                instance_path=instance_path,
                kind="invalid_temporal_date",
                message=f"TemporalValue {value!r} contains an impossible Gregorian date",
            )
        )
    return temporal_range


def _ranges_are_comparable(start: _TemporalRange, end: _TemporalRange) -> bool:
    if start.family != end.family:
        return False
    if start.family == "date":
        return True
    if start.mode == "offset" and end.mode == "offset":
        return True
    if start.mode == "local" and end.mode == "local":
        return True
    return False


def _validate_temporal_extent(
    extent: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    if extent["kind"] == "instant":
        _validate_temporal_value(
            extent["at"], instance_path + ("at",), violations
        )
    else:
        start_range = None
        end_range = None
        if "start" in extent:
            start_range = _validate_temporal_value(
                extent["start"], instance_path + ("start",), violations
            )
        if "end" in extent:
            end_range = _validate_temporal_value(
                extent["end"], instance_path + ("end",), violations
            )

        # Interval 只在当前信息足以建立共同 ordering domain 时比较。
        # 部分精度保持为 possible range；只有 start 最早值仍晚于 end 最晚值才拒绝。
        if (
            start_range is not None
            and end_range is not None
            and _ranges_are_comparable(start_range, end_range)
            and start_range.earliest > end_range.latest
        ):
            violations.append(
                SemanticViolation(
                    instance_path=instance_path + ("start",),
                    kind="interval_order",
                    message="interval start is definitely later than interval end",
                )
            )

    if "provenance" in extent:
        _validate_provenance_collection(
            extent["provenance"], instance_path + ("provenance",), violations
        )


def _validate_time_events(
    owner: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    for index, event in enumerate(owner.get("times", [])):
        _validate_temporal_value(
            event["at"], instance_path + ("times", index, "at"), violations
        )


def _validate_confidence(
    confidence: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    value = confidence["value"]
    value_finite = _is_finite_number(value)
    if not value_finite:
        violations.append(
            SemanticViolation(
                instance_path=instance_path + ("value",),
                kind="non_finite_number",
                message="Confidence.value must be a finite number",
            )
        )

    scale = confidence.get("scale")
    if scale is None:
        return

    minimum = scale["min"]
    maximum = scale["max"]
    minimum_finite = _is_finite_number(minimum)
    maximum_finite = _is_finite_number(maximum)

    if not minimum_finite:
        violations.append(
            SemanticViolation(
                instance_path=instance_path + ("scale", "min"),
                kind="non_finite_number",
                message="Confidence.scale.min must be a finite number",
            )
        )
    if not maximum_finite:
        violations.append(
            SemanticViolation(
                instance_path=instance_path + ("scale", "max"),
                kind="non_finite_number",
                message="Confidence.scale.max must be a finite number",
            )
        )

    # 跨字段数值关系只在参与比较的值均 finite 时判断，避免由一个坏 leaf
    # 级联产生没有独立信息量的 scale/order diagnostics。
    if minimum_finite and maximum_finite:
        if not minimum < maximum:
            violations.append(
                SemanticViolation(
                    instance_path=instance_path + ("scale",),
                    kind="invalid_confidence_scale",
                    message="Confidence.scale.min must be strictly less than max",
                )
            )
        elif value_finite and not minimum <= value <= maximum:
            violations.append(
                SemanticViolation(
                    instance_path=instance_path + ("value",),
                    kind="confidence_value_out_of_range",
                    message="Confidence.value must be within the inclusive declared scale",
                )
            )


def _validate_provenance(
    provenance: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    source = provenance.get("source")
    if source is not None:
        _validate_time_events(source, instance_path + ("source",), violations)

    generator = provenance.get("generator")
    if generator is not None:
        _validate_time_events(generator, instance_path + ("generator",), violations)

    for evidence_index, evidence in enumerate(provenance.get("evidence", [])):
        _validate_time_events(
            evidence,
            instance_path + ("evidence", evidence_index),
            violations,
        )

    confidence = provenance.get("confidence")
    if confidence is not None:
        _validate_confidence(
            confidence, instance_path + ("confidence",), violations
        )


def _validate_provenance_collection(
    collection: list[dict[str, Any]],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    # Provenance equality、inheritance 等价与冗余省略不在本 validator 中实现；
    # 这里只沿正式 ownership traversal 检查 provenance 内自身可机械判断的值。
    for index, provenance in enumerate(collection):
        _validate_provenance(provenance, instance_path + (index,), violations)


def _validate_optional_local_provenance(
    owner: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    if "provenance" in owner:
        _validate_provenance_collection(
            owner["provenance"], instance_path + ("provenance",), violations
        )


def _validate_behavior(
    behavior: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    if "temporal" in behavior:
        _validate_temporal_extent(
            behavior["temporal"], instance_path + ("temporal",), violations
        )

    for frequency_index, frequency in enumerate(behavior.get("frequencies", [])):
        frequency_path = instance_path + ("frequencies", frequency_index)
        if frequency["kind"] == "observed_count" and "window" in frequency:
            _validate_temporal_extent(
                frequency["window"], frequency_path + ("window",), violations
            )
        elif frequency["kind"] == "rate":
            if not _is_finite_number(frequency["value"]):
                violations.append(
                    SemanticViolation(
                        instance_path=frequency_path + ("value",),
                        kind="non_finite_number",
                        message="RateFrequency.value must be a finite number",
                    )
                )
        _validate_optional_local_provenance(frequency, frequency_path, violations)

    for context_index, context in enumerate(behavior.get("contexts", [])):
        _validate_optional_local_provenance(
            context, instance_path + ("contexts", context_index), violations
        )

    for factor_index, factor in enumerate(behavior.get("factors", [])):
        _validate_optional_local_provenance(
            factor, instance_path + ("factors", factor_index), violations
        )

    _validate_provenance_collection(
        behavior["provenance"], instance_path + ("provenance",), violations
    )
    for annotation_index, annotation in enumerate(behavior.get("annotations", [])):
        _validate_provenance_collection(
            annotation["provenance"],
            instance_path + ("annotations", annotation_index, "provenance"),
            violations,
        )


def _validate_preference(
    preference: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    value = preference["value"]
    if value["kind"] == "number" and not _is_finite_number(value["value"]):
        violations.append(
            SemanticViolation(
                instance_path=instance_path + ("value", "value"),
                kind="non_finite_number",
                message="NumericPreferenceValue.value must be a finite number",
            )
        )

    if "temporal" in preference:
        _validate_temporal_extent(
            preference["temporal"], instance_path + ("temporal",), violations
        )
    for context_index, context in enumerate(preference.get("contexts", [])):
        _validate_optional_local_provenance(
            context, instance_path + ("contexts", context_index), violations
        )

    _validate_provenance_collection(
        preference["provenance"], instance_path + ("provenance",), violations
    )
    for annotation_index, annotation in enumerate(preference.get("annotations", [])):
        _validate_provenance_collection(
            annotation["provenance"],
            instance_path + ("annotations", annotation_index, "provenance"),
            violations,
        )


def _validate_relation(
    relation: dict[str, Any],
    instance_path: tuple[PathSegment, ...],
    violations: list[SemanticViolation],
) -> None:
    if "temporal" in relation:
        _validate_temporal_extent(
            relation["temporal"], instance_path + ("temporal",), violations
        )
    _validate_provenance_collection(
        relation["provenance"], instance_path + ("provenance",), violations
    )
    for annotation_index, annotation in enumerate(relation.get("annotations", [])):
        _validate_provenance_collection(
            annotation["provenance"],
            instance_path + ("annotations", annotation_index, "provenance"),
            violations,
        )


def _violation_sort_key(
    violation: SemanticViolation,
) -> tuple[tuple[tuple[int, int | str], ...], str, str]:
    return (
        _path_sort_key(violation.instance_path),
        violation.kind,
        violation.message,
    )


def validate_semantics(document: object) -> SemanticValidationResult:
    # Semantic validation 建立在既有 Schema + reference resolution 之上。
    # lower-layer invalidity 保留原诊断结果，不改写成 SemanticViolation。
    try:
        resolution_result = resolve_references(document)
    except ResolutionInputError as error:
        raise SemanticInputError(schema_result=error.schema_result) from error
    if not resolution_result.valid:
        raise SemanticInputError(resolution_result=resolution_result)

    validated_document = cast(dict[str, Any], document)
    violations: list[SemanticViolation] = []

    for index, behavior in enumerate(validated_document["behaviors"]):
        _validate_behavior(behavior, ("behaviors", index), violations)
    for index, preference in enumerate(validated_document["preferences"]):
        _validate_preference(preference, ("preferences", index), violations)
    for index, relation in enumerate(validated_document["relations"]):
        _validate_relation(relation, ("relations", index), violations)

    ordered = tuple(sorted(violations, key=_violation_sort_key))
    return SemanticValidationResult(valid=not ordered, violations=ordered)


def are_semantics_valid(document: object) -> bool:
    return validate_semantics(document).valid

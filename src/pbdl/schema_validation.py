from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


PathSegment = str | int


@dataclass(frozen=True, slots=True)
class SchemaViolation:
    instance_path: tuple[PathSegment, ...]
    schema_path: tuple[PathSegment, ...]
    keyword: str | None
    message: str


@dataclass(frozen=True, slots=True)
class SchemaValidationResult:
    valid: bool
    violations: tuple[SchemaViolation, ...]

    def __post_init__(self) -> None:
        if self.valid != (len(self.violations) == 0):
            raise ValueError("valid must be true exactly when violations is empty")


def _find_schema_path(module_file: Path) -> Path:
    # Source checkouts keep the canonical machine-readable Schema under spec/schema.
    # This fallback is used only when no build-injected package resource exists.
    for parent in module_file.resolve().parents:
        candidate = parent / "spec" / "schema" / "pbdl-v1.schema.json"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("cannot locate spec/schema/pbdl-v1.schema.json")


def _canonical_schema_path() -> Path:
    return _find_schema_path(Path(__file__))


def _packaged_schema_resource():
    return resources.files("pbdl").joinpath("_data").joinpath("pbdl-v1.schema.json")


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    packaged_schema = _packaged_schema_resource()
    if packaged_schema.is_file():
        with packaged_schema.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
    else:
        with _canonical_schema_path().open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
    if not isinstance(schema, dict):
        raise TypeError("canonical JSON Schema must be a JSON object")
    return schema


@lru_cache(maxsize=1)
def _get_validator() -> Draft202012Validator:
    schema = _load_schema()
    # 当前规范明确使用 JSON Schema Draft 2020-12。显式指定 validator，
    # 避免依赖自动 dialect 推断而让验证行为随库默认值变化。
    Draft202012Validator.check_schema(schema)
    # Schema 自身损坏属于程序或制品错误，不是用户输入非法；
    # 因此 SchemaError 故意向外暴露，不能被包装成普通 validation failure。
    return Draft202012Validator(schema)


def _segment_sort_key(segment: PathSegment) -> tuple[int, int | str]:
    if isinstance(segment, int) and not isinstance(segment, bool):
        return (0, segment)
    return (1, str(segment))


def _path_sort_key(path: tuple[PathSegment, ...]) -> tuple[tuple[int, int | str], ...]:
    # 错误路径可能同时包含对象字段名和数组下标。先编码路径段类型，
    # 避免 Python 直接比较 str 与 int，并让多次验证得到稳定顺序。
    return tuple(_segment_sort_key(segment) for segment in path)


def _to_violation(error: ValidationError) -> SchemaViolation:
    keyword = error.validator if isinstance(error.validator, str) else None
    return SchemaViolation(
        instance_path=tuple(error.absolute_path),
        schema_path=tuple(error.absolute_schema_path),
        keyword=keyword,
        message=error.message,
    )


def _violation_sort_key(
    violation: SchemaViolation,
) -> tuple[
    tuple[tuple[int, int | str], ...],
    tuple[tuple[int, int | str], ...],
    str,
    str,
]:
    return (
        _path_sort_key(violation.instance_path),
        _path_sort_key(violation.schema_path),
        violation.keyword or "",
        violation.message,
    )


def validate_document(document: object) -> SchemaValidationResult:
    # 本层只执行正式 JSON Schema 能表达的结构约束。引用存在性、跨实体语义、
    # 术语判断和规范化都需要独立组件，不能在结构验证过程中隐式补做。
    validator = _get_validator()
    violations = tuple(
        sorted(
            (_to_violation(error) for error in validator.iter_errors(document)),
            key=_violation_sort_key,
        )
    )
    # 校验过程只读取调用方对象：不补默认值、不转换类型、不删除空集合，
    # 否则 validation 会悄悄承担 canonicalization 的职责。
    return SchemaValidationResult(valid=not violations, violations=violations)


def is_schema_valid(document: object) -> bool:
    return validate_document(document).valid

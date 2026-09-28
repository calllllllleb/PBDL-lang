from __future__ import annotations

from copy import deepcopy
from typing import Any


def direct_provenance(source_kind: str = "patient_self_report") -> dict[str, Any]:
    return {
        "derivation": "direct",
        "source": {"kind": source_kind},
    }


def generator_descriptor() -> dict[str, Any]:
    return {"kind": "analytic_model"}


def minimal_document() -> dict[str, Any]:
    return {
        "pbdl_version": "1.0",
        "subjects": [{"id": "subject_1"}],
        "behaviors": [],
        "preferences": [],
        "relations": [],
    }


def base_behavior() -> dict[str, Any]:
    return {
        "id": "behavior_1",
        "subject": {"ref": "subject_1"},
        "type": {"system": "urn:example:behavior", "code": "example"},
        "provenance": [direct_provenance()],
    }


def base_preference() -> dict[str, Any]:
    return {
        "id": "preference_1",
        "subject": {"ref": "subject_1"},
        "category": {"system": "urn:example:preference", "code": "example"},
        "value": {"kind": "text", "value": "example"},
        "provenance": [direct_provenance()],
    }


def base_relation() -> dict[str, Any]:
    return {
        "source": {"ref": "behavior_1"},
        "target": {"ref": "preference_1"},
        "type": {"system": "urn:example:relation", "code": "example"},
        "provenance": [direct_provenance("clinician_documentation")],
    }


def document_with_behavior(behavior: dict[str, Any] | None = None) -> dict[str, Any]:
    document = minimal_document()
    document["behaviors"] = [deepcopy(behavior if behavior is not None else base_behavior())]
    return document


def document_with_preference(preference: dict[str, Any] | None = None) -> dict[str, Any]:
    document = minimal_document()
    document["preferences"] = [
        deepcopy(preference if preference is not None else base_preference())
    ]
    return document


def document_with_relation(relation: dict[str, Any] | None = None) -> dict[str, Any]:
    document = minimal_document()
    document["relations"] = [deepcopy(relation if relation is not None else base_relation())]
    return document

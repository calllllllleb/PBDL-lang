from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pbdl import (
    RelationVocabulary,
    canonicalize_document,
    documents_canonically_equal,
    is_canonical_normal_form,
    resolve_references,
    validate_document,
    validate_relation_vocabulary,
    validate_semantics,
)


def _corpus_path(repository_root: Path, name: str) -> Path:
    return repository_root / "spec" / "examples" / "full-pipeline" / name


def _load_vocabulary(
    repository_root: Path,
    load_json_fixture: Callable[[Path], Any],
) -> RelationVocabulary:
    mapping = load_json_fixture(
        _corpus_path(repository_root, "relation-vocabulary.json")
    )
    return RelationVocabulary.from_mapping(mapping)


def test_valid_full_pipeline_corpus(
    repository_root: Path,
    load_json_fixture: Callable[[Path], Any],
) -> None:
    vocabulary = _load_vocabulary(repository_root, load_json_fixture)

    for name in (
        "01-canonical-symmetric.json",
        "02-swapped-symmetric.json",
        "03-normalization-required.json",
    ):
        document = load_json_fixture(_corpus_path(repository_root, name))

        assert validate_document(document).valid
        assert resolve_references(document).valid
        assert validate_semantics(document).valid
        assert validate_relation_vocabulary(document, vocabulary).valid


def test_normalization_and_equality_reference_cases(
    repository_root: Path,
    load_json_fixture: Callable[[Path], Any],
) -> None:
    vocabulary = _load_vocabulary(repository_root, load_json_fixture)
    canonical = load_json_fixture(
        _corpus_path(repository_root, "01-canonical-symmetric.json")
    )
    swapped = load_json_fixture(
        _corpus_path(repository_root, "02-swapped-symmetric.json")
    )
    normalization_required = load_json_fixture(
        _corpus_path(repository_root, "03-normalization-required.json")
    )

    assert is_canonical_normal_form(
        canonical,
        relation_vocabulary=vocabulary,
    )
    assert is_canonical_normal_form(
        swapped,
        relation_vocabulary=vocabulary,
    )
    assert not is_canonical_normal_form(
        normalization_required,
        relation_vocabulary=vocabulary,
    )

    assert documents_canonically_equal(
        canonical,
        swapped,
        relation_vocabulary=vocabulary,
    )
    assert documents_canonically_equal(
        canonical,
        normalization_required,
        relation_vocabulary=vocabulary,
    )

    normalized = canonicalize_document(
        normalization_required,
        relation_vocabulary=vocabulary,
    )
    assert is_canonical_normal_form(
        normalized,
        relation_vocabulary=vocabulary,
    )


def test_reference_invalid_corpus_case(
    repository_root: Path,
    load_json_fixture: Callable[[Path], Any],
) -> None:
    document = load_json_fixture(
        _corpus_path(repository_root, "04-reference-invalid.json")
    )

    assert validate_document(document).valid
    assert not resolve_references(document).valid


def test_semantic_and_vocabulary_invalid_corpus_cases(
    repository_root: Path,
    load_json_fixture: Callable[[Path], Any],
) -> None:
    vocabulary = _load_vocabulary(repository_root, load_json_fixture)

    semantic_invalid = load_json_fixture(
        _corpus_path(repository_root, "05-semantic-invalid.json")
    )
    assert validate_document(semantic_invalid).valid
    assert resolve_references(semantic_invalid).valid
    assert not validate_semantics(semantic_invalid).valid

    vocabulary_invalid = load_json_fixture(
        _corpus_path(repository_root, "06-vocabulary-invalid.json")
    )
    assert validate_document(vocabulary_invalid).valid
    assert resolve_references(vocabulary_invalid).valid
    assert validate_semantics(vocabulary_invalid).valid

    result = validate_relation_vocabulary(vocabulary_invalid, vocabulary)
    assert not result.valid
    assert any(
        violation.kind == "endpoint_signature_mismatch"
        for violation in result.violations
    )

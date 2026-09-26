# PBDL Design Rationale

This document records design reasoning for the 2026 PBDL redesign. It is **non-normative**. The normative language source is [`../spec/PBDL-v1.0-SPEC.md`](../spec/PBDL-v1.0-SPEC.md).

Historical project reports from the original 2024 work may inform design discussion, but they do not determine PBDL v1 semantics.

## DR-001 — PBDL is not an LLM replacement

### Decision

Modern LLMs may understand and extract patient behaviors and preferences from unstructured text. NLP systems, manual entry, surveys, devices, and rules may also provide candidate information.

PBDL exists to provide a stable structured semantic contract after or alongside those extraction processes.

The intended architectural separation is:

```text
Natural language / EHR / survey
        ↓
LLM / NLP / manual input
        ↓
Candidate PBDL
        ↓
Parser / Validator
        ↓
Canonical PBDL
        ↓
Applications
```

The parser and validator shown here are future architectural components, not R0 implementations.

### Rationale

Extraction technology can change independently of the representation contract. Keeping these concerns separate allows upstream methods to evolve without making the PBDL language itself dependent on one inference technology.

## DR-002 — PBDL-Core describes, applications reason

### Decision

PBDL-Core is responsible for representing patient behaviors, preferences, and the contextual, evidential, and relational information needed to interpret them.

Reasoning and action are outside Core, including:

- diagnosis
- recommendation
- risk prediction
- causal inference
- knowledge-base reasoning
- pathway recommendation
- workflow execution

### Rationale

Mixing descriptive statements with inferred conclusions causes semantic ambiguity: downstream consumers can no longer tell what came from a source and what was computed by another system.

Derived artifacts may be represented explicitly when future design defines how to mark their derivation, but they must not silently become source facts.

## DR-003 — Pathway is not Core in the initial redesign

### Decision

Treatment Pathway is not part of PBDL-Core in the initial redesign.

It remains a candidate for:

- a future PBDL extension, or
- an application layer built on PBDL.

### Rationale

The project's original research focus is the description of patient behaviors and preferences. Freezing pathway semantics into Core before the behavior/preference language is stable would expand the ontology prematurely and blur the boundary between description and recommendation/workflow.

## DR-004 — Historical report is non-normative

### Decision

Historical reports preserve the project's design history and may provide concepts worth reconsidering, but they are not development specifications.

If a historical report conflicts with the normative specification, the normative specification takes precedence.

### Rationale

Earlier material contains definition drift, field conflicts, and boundaries that mix language ontology with inference capabilities. Treating it as authoritative would carry those inconsistencies into the redesigned language.

## DR-005 — Avoid unsupported clinical semantics

### Decision

PBDL must not use field names or default constructs that imply unverified causal relationships, treatment effects, or clinical conclusions.

Candidate relations for later design discussion include:

- `related_to`
- `associated_with`
- `reported_reason_for`
- `precedes`
- `follows`
- `derived_from`

These are **design candidates only** and are not a frozen Core vocabulary.

`causal_effect` is deliberately not assumed as a default Core relation.

### Rationale

Descriptive proximity, sequence, association, or a reported reason do not by themselves establish causality. Causal inference and causal weighting require evidence and methods outside the default descriptive language core.

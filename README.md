# PBDL-lang

**PBDL — Patient Behavior Description Language**

PBDL is a declarative domain-specific language for representing patient behaviors and preferences in a structured, explicit, and machine-verifiable form.

中文：**面向患者行为与偏好的声明式领域专用描述语言。**

## What is PBDL

PBDL is designed to provide a stable representation layer for patient behaviors and preferences. It does **not** replace natural-language understanding.

Modern LLMs, NLP systems, manual data entry, rule-based systems, and other upstream methods may all produce candidate PBDL information. PBDL is responsible for:

- standardized representation
- explicit semantics
- validation
- persistence
- interoperability between upstream extraction and downstream applications

## Core architectural boundary

**PBDL-Core describes; external applications reason and act.**

PBDL-Core does not itself perform:

- clinical diagnosis
- clinical recommendation
- risk prediction
- causal inference
- knowledge-base reasoning
- LLM inference
- pathway recommendation
- workflow execution

These capabilities may be implemented by future systems that consume or produce PBDL artifacts, but they are outside the PBDL-Core language boundary.

## Normative source

[`spec/PBDL-v1.0-SPEC.md`](spec/PBDL-v1.0-SPEC.md) is the normative specification.

When documentation, examples, historical reports, and implementation behavior conflict with the normative specification, the normative specification takes precedence.

Historical project reports are design background only and are not development specifications.

## Current status

**PBDL v0.1 Draft preparation**

The repository is currently establishing the language foundation for a redesigned PBDL specification. It does not claim a mature language, clinical validation, or a production implementation.

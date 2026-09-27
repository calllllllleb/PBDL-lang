# R2B0 — Representation Semantics & Identity Stress Test

> **NON-NORMATIVE**
>
> 本文记录 R2B0 architecture stress-test cases、分析与 phase ownership。Normative conclusions 以 `spec/PBDL-v1.0-SPEC.md` 为准。

## Baseline

Start HEAD: `69e3b7301eb19b516dabb5d2e0829dad79b6d6eb`

Stress-test scope:

1. Relation identity viability
2. Provenance inheritance / canonical equality
3. Unknown / unspecified derivation migration
4. ActorRef viability

R2B0 不设计 JSON Schema、EBNF、parser、validator implementation 或完整 leaf-type schemas。

## Decision Table A — Relation identity

| Case | Current no-id result | Ambiguity / failure | Decision | Normative consequence | Deferred work |
|---|---|---|---|---|---|
| A1 same endpoints, different type | 可表达为两个 Relation | 无 Core ambiguity | KEEP | type 是 relation semantics 的一部分 | none |
| A2 same endpoints/type, different temporal | 可表达为两个 Relation | 无 Core ambiguity | KEEP | temporal difference 可区分 assertion | none |
| A3 same endpoints/type/temporal, different provenance | 可表达并保持 distinct | structural matching 必须考虑 provenance semantics | KEEP | provenance distinction 继续决定 semantic distinction | canonical serialization details → R2B |
| A4 next version only annotation changes | no stable lifecycle identity | diff engine 需知道 annotation 非 Core identity | KEEP | annotation-only change 不要求 Core id | cross-version diff policy → application tooling |
| A5 next version only temporal changes | 新版本可视作不同 assertion | “same lifecycle object” 不是 Core promise | KEEP | temporal semantic change 可表示 replace/add-delete | lifecycle tracking → application |
| A6 derived relation-strength artifact targets one relation | endpoints alone 不足 | Core 无 stable RelationRef | KEEP | 不为 Core convenience 增 id；artifact 必须使用完整 relation assertion locator / app handle | derived artifact design |
| A7 audit log says relation transformed/reviewed | Core no-id 不提供 lifecycle handle | audit lifecycle 超出 Core | KEEP | audit handle 属 application / extension | audit design |
| A8 diff engine with multiple Relations | 需要 structural matching | matching 可能复杂但不等于 identity requirement | KEEP | Core 不使用 collection position 作为 identity | diff / hashing implementation |

**Conclusion: KEEP — Relation no required identity.**

Stress test 没有发现需要修改 R1 §16 #33 的 Core identity requirement。

Core semantic distinctness 由 canonical semantic content 支持；跨版本 lifecycle identity 是另外一层问题。

## Decision Table B — Provenance inheritance / equality

| Case | Current model result | Ambiguity / failure | Decision | Normative consequence | Deferred work |
|---|---|---|---|---|---|
| B1 owner {P1}, child omitted | inherit {P1} | 无 | ACCEPT | omitted = complete current applicable owner set | serialization → R2B |
| B2 owner {P1}, child explicit {P1} | semantic same as B1 | 两种 representation | NORMALIZE | redundant local MUST omit | ordering syntax → R2B |
| B3 owner {P1,P2}, child only P1 | local required | 无 | KEEP | child explicit complete set {P1} | none |
| B4 owner {P1,P2}, child local {P1,P2} | semantic same as omit | redundant representation | NORMALIZE | canonical form omit local | none |
| B5 owner gains P3 while child omitted | child meaning becomes {P1,P2,P3} | snapshot interpretation would need hidden history | DYNAMIC | inheritance is structural current-document semantics | transforms preserving old subset must materialize local |
| B6 inherit P1 + local P3 | additive merge ambiguous | multiple complete-set interpretations | FORBID | local present = complete override | none |
| B7 Frequency / Context / Factor | same architecture | divergence would complicate equality | UNIFY | same inheritance rules apply | Temporal qualifier decision → R2B |
| B8 local provenance ordering differs | same semantic set | ordering must not create meaning | IGNORE ORDER | order has no semantic effect | canonical sorting → R2B |

**Final representation rule**

- local absent → inherit complete current applicable owner set;
- local present → complete override;
- no additive merge;
- explicit local == inherited complete set → semantic-equivalent and canonical normalization omits local;
- collection ordering has no semantic meaning.

## Decision Table C — Unknown derivation

| Case | Current direct/inferred-only result | Ambiguity / failure | Decision | Normative consequence | Deferred work |
|---|---|---|---|---|---|
| C1 new canonical document, derivation known | direct/inferred sufficient | none | keep classification | UNDETERMINED forbidden as escape hatch | enum serialization → R2B |
| C2 legacy source exists, extraction vs inference unknown | forced binary would invent certainty | real migration gap | ADD UNDETERMINED | use source legacy record; warning | validator code → later |
| C3 legacy final fields, original metadata absent | can still trace imported legacy record as source | original derivation unknown | ADD UNDETERMINED | source path required; do not invent original metadata | SourceDescriptor fields → R2B |
| C4 historical migration pipeline cannot classify | forced binary unsafe | same as C2/C3 | ADD UNDETERMINED | preserve known migration generator if available | GeneratorDescriptor fields → R2B |
| C5 upstream should know but omits classification | unknown would hide producer failure | governance risk | REJECT MISUSE | semantic non-conformance; UNDETERMINED not general fallback | validation profile → later |

**Conclusion: ADD — semantic state `UNDETERMINED`.**

Meaning: derivation metadata unavailable / undetermined.

It is **not** partly direct, partly inferred, or “consumer may assume direct.”

Legacy migration may use it when historical metadata genuinely cannot classify. Native producer that can classify must not use it.

UNDETERMINED requires a traceable source path. If no source path can be preserved, provenance requirement is not satisfied.

Canonical validity: allowed migration semantics; validator SHOULD emit provenance-quality warning.

## Decision Table D — ActorRef viability

| Case | Current ActorRef question | Ambiguity / failure | Decision | Normative consequence | Deferred work |
|---|---|---|---|---|---|
| D1 executor = Subject | SubjectRef sufficient | none | SubjectRef | use Core Subject identity | reference serialization → R2B |
| D2 caregiver | not a Core Subject | needs external representation | ExternalActorRef | embedded descriptor | leaf fields → R2B |
| D3 clinician | same | same | ExternalActorRef | embedded descriptor | leaf fields → R2B |
| D4 device | same | actor kind differs | ExternalActorRef | kind must support device | leaf fields → R2B |
| D5 external software/system | same | actor kind differs | ExternalActorRef | kind must support system/software | leaf fields → R2B |
| D6 same caregiver across Behaviors | display alone cannot prove sameness | stable id optional | ExternalActorRef | external identity may express stable sameness | identity field syntax → R2B |
| D7 only human-readable role | can describe role, not stable instance | must not invent identity | ExternalActorRef | role/display does not establish same actor | leaf fields → R2B |
| D8 external system id exists | stable external identity available | none | ExternalActorRef | may preserve external identity | namespace/system shape → R2B |

**Conclusion: Category B — `ActorRef = SubjectRef | embedded ExternalActorRef`.**

No Actor / Participant Core entity is added. R1B identity namespace and Relation endpoint matrix remain unchanged.

## Cross-checks

### Relation identity × derived artifacts / migration / references

No Core entity currently needs a RelationRef. Derived relation-strength artifacts and audit lifecycle handles are outside Core. They must not use collection position as identity.

### Provenance equality × hashing / dedup / diff / round-trip

Redundant explicit local provenance creates duplicate representations. Canonical omission of an explicit set equal to the inherited complete owner set removes that ambiguity.

Canonical hashing / dedup must compare provenance semantically independent of collection order. Concrete sorting is R2B work.

### UNDETERMINED × DIRECT / INFERRED requirements

DIRECT still requires source. INFERRED still requires generator.

UNDETERMINED does not weaken either rule. It has its own restricted migration semantics and requires a traceable source path.

### ActorRef × identity / endpoint matrix

ExternalActorRef does not enter Core identity namespace and is not a Relation endpoint. Participant model is not introduced.

## Architecture Debt Schedule

### CLOSED in R2B0

- Relation required identity viability → **KEEP no required identity**
- Nested qualifier provenance inheritance semantics → **CLOSED**
- Provenance semantic/canonical equality direction → **CLOSED**
- Additive provenance inheritance → **FORBIDDEN**
- Unknown derivation architecture → **ADD UNDETERMINED**
- ActorRef architecture category → **SubjectRef | ExternalActorRef**

### Assigned to R2B concrete representation

Must be concretized before R2C Schema work:

- ExternalActorRef leaf fields: actor kind, external identity representation, display / role
- DerivationKind lexical / enum serialization including UNDETERMINED
- SourceDescriptor / GeneratorDescriptor concrete fields needed for migration traceability
- nested local provenance serialization
- provenance collection canonical ordering / sorting
- Temporal qualifier local-provenance decision

### Not a Core R2C blocker

- cross-version Relation lifecycle handles → application / audit layer
- derived relation-strength artifact locator → derived artifact design
- diff engine matching algorithm → tooling

R2B0 does not start any leaf-type implementation.

# R2C5 — Final Schema Fidelity Audit

> **Status:** R2C5 FINAL SCHEMA FIDELITY AUDIT → **PASS**
>
> **R2C:** **CLOSED**
>
> Audit mode: **AUDIT ONLY**. No Schema, SPEC, projection-contract, grammar, vocabulary, README, CHANGELOG, or example fixture was modified by this audit.

## 1. Audit baseline

- Repository: `calllllllleb/PBDL-lang`
- Branch: `main`
- HEAD before audit: `4878a075df8790f1c07a0250b8d54c6584530bcb`
- Schema: `spec/schema/pbdl-v1.schema.json`
- Schema blob before audit: `a27802260f7cf3d1444e2090af7d2094e26480b5`
- SPEC blob: `5a89f77e95a517ec2dce185f198c0bfaa231c495`
- Projection contract blob: `40826a0bb9236b61c28bd647f6bb54f4231526cb`
- Dialect: `https://json-schema.org/draft/2020-12/schema`
- Root: `#/$defs/PBDLDocument`
- Named definitions: **54**
- Formal corpus: **4 valid + 12 invalid = 16**
- Temporary mechanical audit code was not added to the repository.

The current SPEC blob is byte-identical to the SPEC at the R2B frozen authority commit `329ac9e643adb56ee4d5e89a9515947f34b5a0aa`; there is no intervening normative semantic drift.

## 2. Scope / authority

Authority was applied in the required order:

1. `spec/PBDL-v1.0-SPEC.md`
2. `docs/r2c-schema-projection.md`
3. current JSON Schema
4. examples / implementation evidence

The audit independently re-read the current Schema and corpus. Earlier R2C1–R2C4 closure reports were not treated as substitutes for current-source evidence.

Denominator recovered from the projection contract:

- named types: **54**
- field / constraint rows: **124**
- cross-cutting invariants: **40**
- total projection entries: **218**
- projection status totals: **91 SCHEMA / 107 PARTIAL / 20 NOT_SCHEMA**

Every denominator entry has an audit classification in Appendices A–C.

## 3. 54-type denominator result

**54 / 54 named types reviewed.**

- exact expected-vs-actual `$defs` set equality: **PASS**
- missing defs: **[]**
- extra defs: **[]**
- R2C1: **10 / 10**
- R2C2: **38 / 38**
- R2C3: **5 / 5**
- R2C4: **1 / 1**
- type-level defects: **0**

All PARTIAL types implement their structural portion and leave the frozen semantic / resolver / terminology / canonicalization remainder outside Schema.

## 4. 124 field/constraint inventory result

**124 / 124 rows reviewed; 124 PASS; 0 DEFECT.**

A mechanical row checker resolved each field against current `$defs`, checked declared presence, requiredness, `$ref` target where applicable, scalar type/minimum, array/items/minItems/uniqueItems, nonblank pattern presence, and the two cross-field `anyOf` rows. No row mismatched the projection contract.

The full row ledger is Appendix B.

## 5. 40 cross-cutting invariant result

**40 / 40 invariants reviewed.**

- SCHEMA: **17 / 17 PASS**
- PARTIAL: **3 / 3 structural projection PASS**, semantic remainder correctly deferred
- NOT_SCHEMA: **20 / 20 NON_SCHEMA_CORRECTLY_DEFERRED**
- defects: **0**

The full invariant ledger is Appendix C.

## 6. Closed-object audit

Recursive scan found **36 concrete structured object schemas**, including embedded `Confidence.scale` and `ExternalActorRef.external_id`.

- closed concrete objects: **36 / 36**
- closure defects: **0**
- mechanism: `unevaluatedProperties:false` at every concrete object boundary

This includes Coding, Confidence and scale, all reference/descriptor/evidence/provenance objects, temporal/frequency/value variants, Context, BehaviorFactor, the Core five, and PBDLDocument.

## 7. Union audit

Frozen union definitions are exact:

| Union | Exact variants | Attack result |
|---|---|---:|
| ActorRef | SubjectRef / ExternalActorRef | PASS |
| TemporalExtent | Instant / Interval | PASS |
| BehaviorFrequency | ObservedCountFrequency / RateFrequency / RecurrenceFrequency / QualitativeFrequency | PASS |
| PreferenceValue | CodedPreferenceValue / TextPreferenceValue / BooleanPreferenceValue / NumericPreferenceValue | PASS |
| ContextValue | CodedContextValue / TextContextValue | PASS |
| FactorValue | CodedFactorValue / TextFactorValue | PASS |

A separate branch-count matrix exercised **28 cases**. Every valid variant matched **exactly one** branch; every unknown-kind / hybrid attack matched **zero** branches. No case matched 2+ branches.

`ActorRef` specifically rejects `{"ref":"subject_1","kind":"person"}`.

## 8. Conditional invariant audit

### Provenance

11 direct/inferred/undetermined attacks all behaved as frozen:

- direct requires source; generator may coexist
- inferred requires generator; source may coexist
- undetermined requires source and accepts locator **or** nonempty evidence, including both
- source-kind only and empty evidence do not satisfy undetermined traceability

### RecurrenceFrequency

8 attacks PASS:

- days_of_week present ⇒ nonempty, unique, period exactly `{value:1,unit:"week"}`, times_per_period absent
- empty/duplicate weekdays, wrong unit, week value 2, and days+times are invalid
- without days_of_week, nonweekly period and times_per_period remain allowed

### BehaviorFactor

All **12 role × direction** combinations were tested:

- reported_reason / antecedent permit only factor_to_behavior
- observed_association / explanatory are not over-constrained

Conditional invariant defects: **0**.

## 9. Unicode White_Space audit

Frozen nonblank pattern:

`[^\\u0009-\\u000D\\u0020\\u0085\\u00A0\\u1680\\u2000-\\u200A\\u2028\\u2029\\u202F\\u205F\\u3000]`

Results:

- exact direct nonblank-pattern surfaces: **11 / 11**
- `Text`-referencing fields inherit the same contract
- U+0085-only attacks: **INVALID**
- U+FEFF-only attacks: **VALID**
- paired U+0085/U+FEFF attacks: **22 / 22 PASS**
- `\\s` / `\\S` approximations: **0**
- `minLength` approximations: **0**
- Unicode nonblank defects: **0**

## 10. TemporalValue audit

All six precision profiles were exercised: Year, Month, Date, minute datetime, second datetime, fraction datetime.

**28 TemporalValue attacks PASS**, covering year/month/day component bounds, hour/minute/second bounds, fraction length, ±14:00 offset ceiling, ZoneToken characters/whitespace/brackets, date-only+zone, time-only, and trailing newline / line-separator rejection.

`2026-02-30` remains Schema-valid and is classified **NON_SCHEMA_CORRECTLY_DEFERRED** because real Gregorian-date validation belongs to the semantic validator.

TemporalValue lexical defects: **0**.

## 11. Cardinality / null audit

Programmatic inventory found **28 array-valued properties**:

- required 1..*: **5**, all `minItems:1`
- optional 1..*: **9**, all `minItems:1` when present
- required 0..*: **3**, none has `minItems:1`
- optional 0..*: **11**, none has `minItems:1`

The optional 0..* fields remain Schema-valid as `[]`; that state is normalization-required, not Schema-invalid.

Programmatic optional-property audit found **46 optional properties**. **0 / 46** accept `null`.

- cardinality defects: **0**
- null-policy defects: **0**

## 12. uniqueItems audit

Recursive Schema scan found exactly one `uniqueItems:true`:

`#/$defs/RecurrenceFrequency/properties/days_of_week`

No other array uses `uniqueItems:true`.

- missing required occurrence: **0**
- forbidden extra occurrences: **0**
- uniqueItems defects: **0**

## 13. Root audit

PBDLDocument has exactly:

`pbdl_version, subjects, behaviors, preferences, relations`

and requires exactly those five fields.

Root attacks verified:

- missing any one of five ⇒ INVALID
- wrong version ⇒ INVALID
- subjects=[] ⇒ INVALID
- behaviors/preferences/relations=[] ⇒ VALID
- unknown root property ⇒ INVALID
- full-schema root `$ref` activates these constraints

Root defects: **0**.

## 14. Corpus audit

All 16 fixture files parse as JSON.

| Fixture | Expected | Observed | Structural reason |
|---|---:|---:|---|
| valid/01-minimal-document.json | VALID | VALID | minimal required root |
| valid/02-populated-document.json | VALID | VALID | populated Core graph shape |
| valid/03-empty-optional-collections.json | VALID | VALID | optional 0..* arrays may be [] |
| valid/04-external-actor-and-structured-values.json | VALID | VALID | external actor / interval / recurrence / context / factor shape |
| invalid/01-missing-version.json | INVALID | INVALID | missing required root version |
| invalid/02-wrong-version.json | INVALID | INVALID | VersionToken const violation |
| invalid/03-missing-subjects.json | INVALID | INVALID | missing required subjects |
| invalid/04-empty-subjects.json | INVALID | INVALID | subjects minItems violation |
| invalid/05-missing-behaviors.json | INVALID | INVALID | missing required root array |
| invalid/06-missing-preferences.json | INVALID | INVALID | missing required root array |
| invalid/07-missing-relations.json | INVALID | INVALID | missing required root array |
| invalid/08-unknown-root-field.json | INVALID | INVALID | root closure |
| invalid/09-invalid-subject.json | INVALID | INVALID | Subject closure |
| invalid/10-behavior-empty-provenance.json | INVALID | INVALID | required 1..* provenance |
| invalid/11-relation-extra-id.json | INVALID | INVALID | Relation closure |
| invalid/12-null-optional-field.json | INVALID | INVALID | null forbidden for optional temporal |

- valid corpus failures: **0**
- invalid corpus unexpected passes: **0**
- invalid fixtures whose only fault is semantic/resolver/normalization/vocabulary-only: **0**
- corpus classification defects: **0**

### Formal corpus coverage gaps

The current 16-file corpus does **not** provide complete positive+negative root-integrated boundary coverage for the following 13 high-risk mechanisms:

ActorRef exclusivity; Evidence anyOf; Provenance conditionals; Interval anyOf; TemporalExtent oneOf; BehaviorFrequency oneOf; RecurrenceFrequency weekday conditional; PreferenceValue oneOf; ContextValue oneOf; FactorValue oneOf; BehaviorFactor direction conditional; Unicode White_Space regression; local provenance minItems.

Some are positively exercised by valid fixture 04, but the formal corpus does not close their negative boundary.

Classification: **NON-BLOCKING R3A test-harness debt**. Reason: independent current-Schema mechanical attacks cover these boundaries (including 132 contract attack cases plus the 28-case union branch-count matrix), so Schema correctness does not depend on adding fixtures during this audit-only round.

## 15. Non-overreach audit

Required semantic-invalid-but-schema-valid / unresolved / normalization-boundary attacks PASS:

- Confidence inverted/out-of-range sibling values remain Schema-valid
- unresolved SubjectRef remains Schema-valid
- unresolved CoreEntityRef remains Schema-valid
- duplicate Subject ids remain Schema-valid
- duplicate Provenance / Relation values remain Schema-valid
- arbitrary structurally valid Relation Coding remains Schema-valid
- reverse temporal interval remains Schema-valid
- Text Preference/Context/Factor fallback shapes remain Schema-valid
- optional 0..* explicit [] remains Schema-valid
- `2026-02-30` remains Schema-valid

Relation extra structural fields `id/weight/direction/directionality/inverse/symmetric` are all rejected by closure, while vocabulary membership, directionality, inverse semantics and swapped-endpoint equality remain unencoded.

The explicit no-approximation matrix is Appendix D; the complete non-Schema responsibility matrix is Appendix E.

## 16. $ref / reachability audit

- internal `$ref` occurrences: **101**
- broken internal ref targets: **0**
- reachable named defs from root: **54 / 54**
- unreachable defs: **[]**
- duplicate JSON object keys in Schema source: **0**
- orphan / shadow root model: **0**
- second root model: **0**

`Draft202012Validator.check_schema(schema)`: **PASS**.

## 17. Draft 2020-12 portability audit

- declared dialect: Draft 2020-12
- patterns: **18**
- ECMAScript `RegExp` compilation failures: **0**
- lookbehind: **0**
- Unicode property-escape assumptions: **0**
- inline PCRE-only flag constructs: **0**
- custom / implementation-specific assertion keywords: **0**
- TemporalValue negative lookahead compiles under ECMAScript

Portability defects: **0**.

## 18. Findings

### NOTE — Authority remained stable

Current SPEC is byte-identical to the R2B frozen SPEC authority blob used by R2C0.

### MINOR — Cosmetic title duplication

`PBDLDocument.title` is currently:

`"PBDL PBDLDocument"`

This is a non-assertion annotation and does not alter machine validity. It is recorded as non-blocking polish debt and was not changed in this audit.

### NOTE — Formal corpus coverage debt

The 13 high-risk mechanisms listed in §14 lack complete positive+negative root-integrated formal fixtures. Independent attacks establish current correctness, so this is deferred to R3A rather than treated as an R2C5 blocker.

## 19. Blocking defects

**None.**

| Defect class | Count |
|---|---:|
| concrete-object closure defects | 0 |
| union fidelity defects | 0 |
| conditional invariant defects | 0 |
| cardinality defects | 0 |
| null-policy defects | 0 |
| uniqueItems defects | 0 |
| Unicode nonblank defects | 0 |
| TemporalValue lexical defects | 0 |
| root defects | 0 |
| $ref defects | 0 |
| portability defects | 0 |
| under-projection blockers | 0 |
| over-projection blockers | 0 |
| corpus defects | 0 |
| SPEC/Schema contradictions | 0 |
| Draft validity defects | 0 |
| corpus classification defects | 0 |

## 20. Non-blocking debt

1. **MINOR / polish:** `PBDLDocument.title = "PBDL PBDLDocument"`.
2. **NOTE / R3A harness debt:** add formal root-integrated positive+negative fixtures for the 13 high-risk mechanisms listed in §14.

Neither changes the Draft 2020-12 assertion contract.

## 21. Final verdict

```text
R2C5 FINAL SCHEMA FIDELITY AUDIT
→ PASS

54 / 54 named types accounted
124 / 124 field/constraint rows accounted
40 / 40 cross-cutting invariants accounted
218 / 218 projection entries accounted

Schema under-projection blockers:
0

Schema over-projection blockers:
0

Schema/SPEC contradictions:
0

broken internal refs:
0

Draft 2020-12 validity:
PASS

valid corpus failures:
0

invalid corpus unexpected passes:
0

R2C5
→ PASS
→ CLOSED

R2C
→ CLOSED

Next:
R3A — Schema Validation Harness
```

---

# Appendix A — 54 named-type audit ledger

| # | Type | Partition | Projection status | Actual Schema evidence | Audit classification |
|---:|---|---|---|---|---|
| 1 | PBDLDocument | R2C4 | PARTIAL | `$ref -> #/$defs/PBDLDocument`; five exact required root fields; closure/root attacks PASS | PASS |
| 2 | Subject | R2C3 | PARTIAL | `$defs.Subject` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 3 | Behavior | R2C3 | PARTIAL | `$defs.Behavior` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 4 | Preference | R2C3 | PARTIAL | `$defs.Preference` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 5 | Relation | R2C3 | PARTIAL | `$defs.Relation` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 6 | Annotation | R2C3 | PARTIAL | `$defs.Annotation` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 7 | VersionToken | R2C1 | SCHEMA | `$defs.VersionToken` present; primitive/token enum/const/type reviewed | PASS |
| 8 | EntityId | R2C1 | SCHEMA | `$defs.EntityId` present; primitive/token enum/const/type reviewed | PASS |
| 9 | Text | R2C1 | SCHEMA | `$defs.Text` present; primitive/token enum/const/type reviewed | PASS |
| 10 | TemporalValue | R2C1 | PARTIAL | 6 lexical `oneOf` profiles; 28 TemporalValue attacks PASS; Gregorian-date semantics deferred | PASS |
| 11 | Coding | R2C1 | PARTIAL | `$defs.Coding` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 12 | Confidence | R2C1 | PARTIAL | `$defs.Confidence` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 13 | SubjectRef | R2C1 | PARTIAL | `$defs.SubjectRef` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 14 | CoreEntityRef | R2C1 | PARTIAL | `$defs.CoreEntityRef` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 15 | ExternalActorRef | R2C1 | SCHEMA | `$defs.ExternalActorRef` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 16 | ActorRef | R2C1 | PARTIAL | `$defs.ActorRef` present; exact oneOf variant set; union branch-count attacks PASS | PASS |
| 17 | DerivationKind | R2C2 | SCHEMA | `$defs.DerivationKind` present; primitive/token enum/const/type reviewed | PASS |
| 18 | SourceKind | R2C2 | SCHEMA | `$defs.SourceKind` present; primitive/token enum/const/type reviewed | PASS |
| 19 | SourceDescriptor | R2C2 | PARTIAL | `$defs.SourceDescriptor` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 20 | SourceTimeEvent | R2C2 | PARTIAL | `$defs.SourceTimeEvent` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 21 | GeneratorKind | R2C2 | SCHEMA | `$defs.GeneratorKind` present; primitive/token enum/const/type reviewed | PASS |
| 22 | GeneratorDescriptor | R2C2 | PARTIAL | `$defs.GeneratorDescriptor` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 23 | GeneratorTimeEvent | R2C2 | PARTIAL | `$defs.GeneratorTimeEvent` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 24 | EvidenceKind | R2C2 | SCHEMA | `$defs.EvidenceKind` present; primitive/token enum/const/type reviewed | PASS |
| 25 | Evidence | R2C2 | PARTIAL | `$defs.Evidence` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 26 | Provenance | R2C2 | PARTIAL | `$defs.Provenance` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 27 | Instant | R2C2 | PARTIAL | `$defs.Instant` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 28 | Interval | R2C2 | PARTIAL | `$defs.Interval` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 29 | TemporalExtent | R2C2 | PARTIAL | `$defs.TemporalExtent` present; exact oneOf variant set; union branch-count attacks PASS | PASS |
| 30 | QuantitativeFrequencyPrecision | R2C2 | SCHEMA | `$defs.QuantitativeFrequencyPrecision` present; primitive/token enum/const/type reviewed | PASS |
| 31 | FrequencyPeriod | R2C2 | SCHEMA | `$defs.FrequencyPeriod` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 32 | Weekday | R2C2 | SCHEMA | `$defs.Weekday` present; primitive/token enum/const/type reviewed | PASS |
| 33 | DayPart | R2C2 | SCHEMA | `$defs.DayPart` present; primitive/token enum/const/type reviewed | PASS |
| 34 | QualitativeFrequencyToken | R2C2 | SCHEMA | `$defs.QualitativeFrequencyToken` present; primitive/token enum/const/type reviewed | PASS |
| 35 | ObservedCountFrequency | R2C2 | PARTIAL | `$defs.ObservedCountFrequency` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 36 | RateFrequency | R2C2 | PARTIAL | `$defs.RateFrequency` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 37 | RecurrenceFrequency | R2C2 | PARTIAL | `$defs.RecurrenceFrequency` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 38 | QualitativeFrequency | R2C2 | PARTIAL | `$defs.QualitativeFrequency` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 39 | BehaviorFrequency | R2C2 | PARTIAL | `$defs.BehaviorFrequency` present; exact oneOf variant set; union branch-count attacks PASS | PASS |
| 40 | CodedPreferenceValue | R2C2 | PARTIAL | `$defs.CodedPreferenceValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 41 | TextPreferenceValue | R2C2 | PARTIAL | `$defs.TextPreferenceValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 42 | BooleanPreferenceValue | R2C2 | PARTIAL | `$defs.BooleanPreferenceValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 43 | NumericPreferenceValue | R2C2 | PARTIAL | `$defs.NumericPreferenceValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 44 | PreferenceValue | R2C2 | PARTIAL | `$defs.PreferenceValue` present; exact oneOf variant set; union branch-count attacks PASS | PASS |
| 45 | CodedContextValue | R2C2 | PARTIAL | `$defs.CodedContextValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 46 | TextContextValue | R2C2 | PARTIAL | `$defs.TextContextValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 47 | ContextValue | R2C2 | PARTIAL | `$defs.ContextValue` present; exact oneOf variant set; union branch-count attacks PASS | PASS |
| 48 | Context | R2C2 | PARTIAL | `$defs.Context` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 49 | FactorRole | R2C2 | SCHEMA | `$defs.FactorRole` present; primitive/token enum/const/type reviewed | PASS |
| 50 | FactorDirection | R2C2 | SCHEMA | `$defs.FactorDirection` present; primitive/token enum/const/type reviewed | PASS |
| 51 | CodedFactorValue | R2C2 | PARTIAL | `$defs.CodedFactorValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 52 | TextFactorValue | R2C2 | PARTIAL | `$defs.TextFactorValue` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |
| 53 | FactorValue | R2C2 | PARTIAL | `$defs.FactorValue` present; exact oneOf variant set; union branch-count attacks PASS | PASS |
| 54 | BehaviorFactor | R2C2 | PARTIAL | `$defs.BehaviorFactor` present; declared fields/required set reviewed; concrete-object closure PASS | PASS |

# Appendix B — 124 field / constraint audit ledger

For PARTIAL rows, `PASS` means the complete Schema-owned structural portion is present and the explicitly non-Schema remainder stays with its frozen owner.

| # | Type / field | Frozen rule | Projection status | Actual Schema mechanism | Verdict | Evidence |
|---:|---|---|---|---|---|---|
| 1 | PBDLDocument.pbdl_version | required VersionToken; exactly "1.0" | SCHEMA | required + $ref VersionToken | PASS | `#/$defs/PBDLDocument/properties/pbdl_version`; mechanical row check PASS |
| 2 | PBDLDocument.subjects | required Subject[1..*] | PARTIAL | required; array/items $ref; minItems:1 | PASS | `#/$defs/PBDLDocument/properties/subjects`; mechanical row check PASS |
| 3 | PBDLDocument.behaviors | required Behavior[0..*], [] valid | PARTIAL | required; array/items $ref; no minItems:1 | PASS | `#/$defs/PBDLDocument/properties/behaviors`; mechanical row check PASS |
| 4 | PBDLDocument.preferences | required Preference[0..*], [] valid | PARTIAL | required; array/items $ref; no minItems:1 | PASS | `#/$defs/PBDLDocument/properties/preferences`; mechanical row check PASS |
| 5 | PBDLDocument.relations | required Relation[0..*], [] valid | PARTIAL | required; array/items $ref; no minItems:1 | PASS | `#/$defs/PBDLDocument/properties/relations`; mechanical row check PASS |
| 6 | Subject.id | required EntityId | PARTIAL | required + $ref EntityId | PASS | `#/$defs/Subject/properties/id`; mechanical row check PASS |
| 7 | Behavior.id | required EntityId | PARTIAL | required + $ref EntityId | PASS | `#/$defs/Behavior/properties/id`; mechanical row check PASS |
| 8 | Behavior.subject | required SubjectRef | PARTIAL | required + $ref SubjectRef | PASS | `#/$defs/Behavior/properties/subject`; mechanical row check PASS |
| 9 | Behavior.type | required Coding | PARTIAL | required + $ref Coding | PASS | `#/$defs/Behavior/properties/type`; mechanical row check PASS |
| 10 | Behavior.executor | optional ActorRef | PARTIAL | $ref ActorRef; omit from required | PASS | `#/$defs/Behavior/properties/executor`; mechanical row check PASS |
| 11 | Behavior.temporal | optional TemporalExtent | PARTIAL | $ref TemporalExtent; omit from required | PASS | `#/$defs/Behavior/properties/temporal`; mechanical row check PASS |
| 12 | Behavior.frequencies | optional BehaviorFrequency[0..*]; [] noncanonical but valid | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Behavior/properties/frequencies`; mechanical row check PASS |
| 13 | Behavior.contexts | optional Context[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Behavior/properties/contexts`; mechanical row check PASS |
| 14 | Behavior.factors | optional BehaviorFactor[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Behavior/properties/factors`; mechanical row check PASS |
| 15 | Behavior.provenance | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | PASS | `#/$defs/Behavior/properties/provenance`; mechanical row check PASS |
| 16 | Behavior.annotations | optional Annotation[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Behavior/properties/annotations`; mechanical row check PASS |
| 17 | Preference.id | required EntityId | PARTIAL | required + $ref EntityId | PASS | `#/$defs/Preference/properties/id`; mechanical row check PASS |
| 18 | Preference.subject | required SubjectRef | PARTIAL | required + $ref SubjectRef | PASS | `#/$defs/Preference/properties/subject`; mechanical row check PASS |
| 19 | Preference.category | required Coding | PARTIAL | required + $ref Coding | PASS | `#/$defs/Preference/properties/category`; mechanical row check PASS |
| 20 | Preference.value | required PreferenceValue | PARTIAL | required + $ref PreferenceValue | PASS | `#/$defs/Preference/properties/value`; mechanical row check PASS |
| 21 | Preference.temporal | optional TemporalExtent | PARTIAL | $ref TemporalExtent | PASS | `#/$defs/Preference/properties/temporal`; mechanical row check PASS |
| 22 | Preference.contexts | optional Context[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Preference/properties/contexts`; mechanical row check PASS |
| 23 | Preference.provenance | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | PASS | `#/$defs/Preference/properties/provenance`; mechanical row check PASS |
| 24 | Preference.annotations | optional Annotation[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Preference/properties/annotations`; mechanical row check PASS |
| 25 | Relation.source | required CoreEntityRef | PARTIAL | required + $ref CoreEntityRef | PASS | `#/$defs/Relation/properties/source`; mechanical row check PASS |
| 26 | Relation.target | required CoreEntityRef | PARTIAL | required + $ref CoreEntityRef | PASS | `#/$defs/Relation/properties/target`; mechanical row check PASS |
| 27 | Relation.type | required Coding | PARTIAL | required + $ref Coding | PASS | `#/$defs/Relation/properties/type`; mechanical row check PASS |
| 28 | Relation.temporal | optional TemporalExtent | PARTIAL | $ref TemporalExtent | PASS | `#/$defs/Relation/properties/temporal`; mechanical row check PASS |
| 29 | Relation.provenance | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | PASS | `#/$defs/Relation/properties/provenance`; mechanical row check PASS |
| 30 | Relation.annotations | optional Annotation[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Relation/properties/annotations`; mechanical row check PASS |
| 31 | Annotation.text | required Text | SCHEMA | required + $ref Text | PASS | `#/$defs/Annotation/properties/text`; mechanical row check PASS |
| 32 | Annotation.provenance | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | PASS | `#/$defs/Annotation/properties/provenance`; mechanical row check PASS |
| 33 | Coding.system | required nonblank semantic string | SCHEMA | required; type:string + nonblank pattern | PASS | `#/$defs/Coding/properties/system`; mechanical row check PASS |
| 34 | Coding.code | required nonblank semantic string | SCHEMA | required; type:string + nonblank pattern | PASS | `#/$defs/Coding/properties/code`; mechanical row check PASS |
| 35 | Coding.display | optional Text | SCHEMA | $ref Text | PASS | `#/$defs/Coding/properties/display`; mechanical row check PASS |
| 36 | Coding.version | optional nonblank semantic string | SCHEMA | type:string + nonblank pattern | PASS | `#/$defs/Coding/properties/version`; mechanical row check PASS |
| 37 | Confidence.value | required number | PARTIAL | required; type:number | PASS | `#/$defs/Confidence/properties/value`; mechanical row check PASS |
| 38 | Confidence.metric | required nonblank semantic string | SCHEMA | required; type:string + nonblank pattern | PASS | `#/$defs/Confidence/properties/metric`; mechanical row check PASS |
| 39 | Confidence.scale | optional closed {min:number,max:number} | PARTIAL | object; required min,max; closure | PASS | `#/$defs/Confidence/properties/scale`; mechanical row check PASS |
| 40 | SubjectRef.ref | required EntityId; exactly one Subject resolution | PARTIAL | required + $ref EntityId | PASS | `#/$defs/SubjectRef/properties/ref`; mechanical row check PASS |
| 41 | CoreEntityRef.ref | required EntityId; exactly one Behavior/Preference resolution | PARTIAL | required + $ref EntityId | PASS | `#/$defs/CoreEntityRef/properties/ref`; mechanical row check PASS |
| 42 | ExternalActorRef.kind | required person\|device\|software\|other | SCHEMA | required + enum | PASS | `#/$defs/ExternalActorRef/properties/kind`; mechanical row check PASS |
| 43 | ExternalActorRef.external_id | optional closed object with required system,value | SCHEMA | object/properties/required/closure | PASS | `#/$defs/ExternalActorRef/properties/external_id`; mechanical row check PASS |
| 44 | ExternalActorRef.external_id.system | required nonblank string | SCHEMA | type:string + nonblank pattern | PASS | `#/$defs/ExternalActorRef/properties/external_id/properties/system`; mechanical row check PASS |
| 45 | ExternalActorRef.external_id.value | required nonblank string | SCHEMA | type:string + nonblank pattern | PASS | `#/$defs/ExternalActorRef/properties/external_id/properties/value`; mechanical row check PASS |
| 46 | ExternalActorRef.display | optional Text | SCHEMA | $ref Text | PASS | `#/$defs/ExternalActorRef/properties/display`; mechanical row check PASS |
| 47 | ExternalActorRef.role | optional Text | SCHEMA | $ref Text | PASS | `#/$defs/ExternalActorRef/properties/role`; mechanical row check PASS |
| 48 | Provenance.derivation | required direct\|inferred\|undetermined | SCHEMA | required + enum | PASS | `#/$defs/Provenance/properties/derivation`; mechanical row check PASS |
| 49 | Provenance.source | optional SourceDescriptor, conditionally required for direct/undetermined | PARTIAL | $ref + if/then required | PASS | `#/$defs/Provenance/properties/source`; mechanical row check PASS |
| 50 | Provenance.generator | optional GeneratorDescriptor, required for inferred | PARTIAL | $ref + if/then required | PASS | `#/$defs/Provenance/properties/generator`; mechanical row check PASS |
| 51 | Provenance.evidence | optional Evidence[0..*]; [] noncanonical | PARTIAL | array/items $ref; no minItems by default | PASS | `#/$defs/Provenance/properties/evidence`; mechanical row check PASS |
| 52 | Provenance.confidence | optional Confidence | PARTIAL | $ref Confidence | PASS | `#/$defs/Provenance/properties/confidence`; mechanical row check PASS |
| 53 | SourceDescriptor.kind | required patient_self_report\|questionnaire\|clinician_documentation\|ehr_record\|device_observation\|legacy_record\|other | SCHEMA | required + enum | PASS | `#/$defs/SourceDescriptor/properties/kind`; mechanical row check PASS |
| 54 | SourceDescriptor.locator | optional nonblank string | SCHEMA | type:string + nonblank pattern | PASS | `#/$defs/SourceDescriptor/properties/locator`; mechanical row check PASS |
| 55 | SourceDescriptor.display | optional Text | SCHEMA | $ref Text | PASS | `#/$defs/SourceDescriptor/properties/display`; mechanical row check PASS |
| 56 | SourceDescriptor.times | optional SourceTimeEvent[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/SourceDescriptor/properties/times`; mechanical row check PASS |
| 57 | SourceTimeEvent.role | required reported\|recorded\|observed | SCHEMA | required + enum | PASS | `#/$defs/SourceTimeEvent/properties/role`; mechanical row check PASS |
| 58 | SourceTimeEvent.at | required TemporalValue | PARTIAL | required + $ref TemporalValue | PASS | `#/$defs/SourceTimeEvent/properties/at`; mechanical row check PASS |
| 59 | GeneratorDescriptor.kind | required human\|llm\|rule_engine\|analytic_model\|migration_process\|other | SCHEMA | required + enum | PASS | `#/$defs/GeneratorDescriptor/properties/kind`; mechanical row check PASS |
| 60 | GeneratorDescriptor.identifier | optional nonblank string | SCHEMA | type:string + nonblank pattern | PASS | `#/$defs/GeneratorDescriptor/properties/identifier`; mechanical row check PASS |
| 61 | GeneratorDescriptor.version | optional nonblank string | SCHEMA | type:string + nonblank pattern | PASS | `#/$defs/GeneratorDescriptor/properties/version`; mechanical row check PASS |
| 62 | GeneratorDescriptor.display | optional Text | SCHEMA | $ref Text | PASS | `#/$defs/GeneratorDescriptor/properties/display`; mechanical row check PASS |
| 63 | GeneratorDescriptor.times | optional GeneratorTimeEvent[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/GeneratorDescriptor/properties/times`; mechanical row check PASS |
| 64 | GeneratorTimeEvent.role | required extracted\|generated\|transformed\|migrated | SCHEMA | required + enum | PASS | `#/$defs/GeneratorTimeEvent/properties/role`; mechanical row check PASS |
| 65 | GeneratorTimeEvent.at | required TemporalValue | PARTIAL | required + $ref TemporalValue | PASS | `#/$defs/GeneratorTimeEvent/properties/at`; mechanical row check PASS |
| 66 | Evidence.kind | required text_excerpt\|document_reference\|questionnaire_response\|device_observation\|legacy_material\|other | SCHEMA | required + enum | PASS | `#/$defs/Evidence/properties/kind`; mechanical row check PASS |
| 67 | Evidence.content | optional Text | SCHEMA | $ref Text | PASS | `#/$defs/Evidence/properties/content`; mechanical row check PASS |
| 68 | Evidence.locator | optional nonblank string | SCHEMA | type:string + nonblank pattern | PASS | `#/$defs/Evidence/properties/locator`; mechanical row check PASS |
| 69 | Evidence.times | optional SourceTimeEvent[0..*] | PARTIAL | array/items $ref; no minItems:1 | PASS | `#/$defs/Evidence/properties/times`; mechanical row check PASS |
| 70 | Evidence.(content\|locator) | at least one present; both allowed | SCHEMA | anyOf required content / required locator | PASS | `#/$defs/Evidence/anyOf`: content-only, locator-only, and both accepted |
| 71 | Instant.kind | required const instant | SCHEMA | required + const | PASS | `#/$defs/Instant/properties/kind`; mechanical row check PASS |
| 72 | Instant.at | required TemporalValue | PARTIAL | required + $ref TemporalValue | PASS | `#/$defs/Instant/properties/at`; mechanical row check PASS |
| 73 | Instant.provenance | optional Provenance[1..*] | PARTIAL | array/items $ref + minItems:1 if present | PASS | `#/$defs/Instant/properties/provenance`; mechanical row check PASS |
| 74 | Interval.kind | required const interval | SCHEMA | required + const | PASS | `#/$defs/Interval/properties/kind`; mechanical row check PASS |
| 75 | Interval.start | optional TemporalValue | PARTIAL | $ref TemporalValue | PASS | `#/$defs/Interval/properties/start`; mechanical row check PASS |
| 76 | Interval.end | optional TemporalValue | PARTIAL | $ref TemporalValue | PASS | `#/$defs/Interval/properties/end`; mechanical row check PASS |
| 77 | Interval.(start\|end) | at least one boundary present | SCHEMA | anyOf required start / required end | PASS | `#/$defs/Interval/anyOf`: start-only, end-only, and both accepted |
| 78 | Interval.provenance | optional Provenance[1..*] | PARTIAL | array/items $ref + minItems:1 if present | PASS | `#/$defs/Interval/properties/provenance`; mechanical row check PASS |
| 79 | FrequencyPeriod.value | required positive integer >=1 | SCHEMA | required; type:integer; minimum:1 | PASS | `#/$defs/FrequencyPeriod/properties/value`; mechanical row check PASS |
| 80 | FrequencyPeriod.unit | required day\|week\|month\|year | SCHEMA | required + enum | PASS | `#/$defs/FrequencyPeriod/properties/unit`; mechanical row check PASS |
| 81 | ObservedCountFrequency.kind | required const observed_count | SCHEMA | required + const | PASS | `#/$defs/ObservedCountFrequency/properties/kind`; mechanical row check PASS |
| 82 | ObservedCountFrequency.count | required integer >=0 | SCHEMA | required; type:integer; minimum:0 | PASS | `#/$defs/ObservedCountFrequency/properties/count`; mechanical row check PASS |
| 83 | ObservedCountFrequency.precision | required exact\|approximate | SCHEMA | required + enum | PASS | `#/$defs/ObservedCountFrequency/properties/precision`; mechanical row check PASS |
| 84 | ObservedCountFrequency.window | optional Interval | PARTIAL | $ref Interval | PASS | `#/$defs/ObservedCountFrequency/properties/window`; mechanical row check PASS |
| 85 | ObservedCountFrequency.provenance | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | PASS | `#/$defs/ObservedCountFrequency/properties/provenance`; mechanical row check PASS |
| 86 | RateFrequency.kind | required const rate | SCHEMA | required + const | PASS | `#/$defs/RateFrequency/properties/kind`; mechanical row check PASS |
| 87 | RateFrequency.value | required number >=0 | SCHEMA | required; type:number; minimum:0 | PASS | `#/$defs/RateFrequency/properties/value`; mechanical row check PASS |
| 88 | RateFrequency.period | required FrequencyPeriod | SCHEMA | required + $ref FrequencyPeriod | PASS | `#/$defs/RateFrequency/properties/period`; mechanical row check PASS |
| 89 | RateFrequency.precision | required exact\|approximate | SCHEMA | required + enum | PASS | `#/$defs/RateFrequency/properties/precision`; mechanical row check PASS |
| 90 | RateFrequency.provenance | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | PASS | `#/$defs/RateFrequency/properties/provenance`; mechanical row check PASS |
| 91 | RecurrenceFrequency.kind | required const recurrence | SCHEMA | required + const | PASS | `#/$defs/RecurrenceFrequency/properties/kind`; mechanical row check PASS |
| 92 | RecurrenceFrequency.period | required FrequencyPeriod | SCHEMA | required + $ref FrequencyPeriod | PASS | `#/$defs/RecurrenceFrequency/properties/period`; mechanical row check PASS |
| 93 | RecurrenceFrequency.precision | required exact\|approximate | SCHEMA | required + enum | PASS | `#/$defs/RecurrenceFrequency/properties/precision`; mechanical row check PASS |
| 94 | RecurrenceFrequency.times_per_period | optional integer >=1 | SCHEMA | type:integer; minimum:1 | PASS | `#/$defs/RecurrenceFrequency/properties/times_per_period`; mechanical row check PASS |
| 95 | RecurrenceFrequency.days_of_week | optional Weekday[1..*], duplicate token invalid | SCHEMA | array/items Weekday; minItems:1; uniqueItems:true | PASS | `#/$defs/RecurrenceFrequency/properties/days_of_week`; mechanical row check PASS |
| 96 | RecurrenceFrequency.day_part | optional morning\|afternoon\|evening\|night | SCHEMA | enum | PASS | `#/$defs/RecurrenceFrequency/properties/day_part`; mechanical row check PASS |
| 97 | RecurrenceFrequency.provenance | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | PASS | `#/$defs/RecurrenceFrequency/properties/provenance`; mechanical row check PASS |
| 98 | QualitativeFrequency.kind | required const qualitative | SCHEMA | required + const | PASS | `#/$defs/QualitativeFrequency/properties/kind`; mechanical row check PASS |
| 99 | QualitativeFrequency.value | required never\|rarely\|occasionally\|sometimes\|often\|frequently\|usually\|intermittently\|always | SCHEMA | required + enum | PASS | `#/$defs/QualitativeFrequency/properties/value`; mechanical row check PASS |
| 100 | QualitativeFrequency.provenance | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | PASS | `#/$defs/QualitativeFrequency/properties/provenance`; mechanical row check PASS |
| 101 | CodedPreferenceValue.kind | required const coded | SCHEMA | required + const | PASS | `#/$defs/CodedPreferenceValue/properties/kind`; mechanical row check PASS |
| 102 | CodedPreferenceValue.value | required Coding | PARTIAL | required + $ref Coding | PASS | `#/$defs/CodedPreferenceValue/properties/value`; mechanical row check PASS |
| 103 | TextPreferenceValue.kind | required const text | SCHEMA | required + const | PASS | `#/$defs/TextPreferenceValue/properties/kind`; mechanical row check PASS |
| 104 | TextPreferenceValue.value | required Text | PARTIAL | required + $ref Text | PASS | `#/$defs/TextPreferenceValue/properties/value`; mechanical row check PASS |
| 105 | BooleanPreferenceValue.kind | required const boolean | SCHEMA | required + const | PASS | `#/$defs/BooleanPreferenceValue/properties/kind`; mechanical row check PASS |
| 106 | BooleanPreferenceValue.value | required boolean | PARTIAL | required; type:boolean | PASS | `#/$defs/BooleanPreferenceValue/properties/value`; mechanical row check PASS |
| 107 | NumericPreferenceValue.kind | required const number | SCHEMA | required + const | PASS | `#/$defs/NumericPreferenceValue/properties/kind`; mechanical row check PASS |
| 108 | NumericPreferenceValue.operator | required eq\|lt\|lte\|gt\|gte | SCHEMA | required + enum | PASS | `#/$defs/NumericPreferenceValue/properties/operator`; mechanical row check PASS |
| 109 | NumericPreferenceValue.value | required number | SCHEMA | required; type:number | PASS | `#/$defs/NumericPreferenceValue/properties/value`; mechanical row check PASS |
| 110 | NumericPreferenceValue.unit | optional Coding; may be semantically required by source/category | PARTIAL | $ref Coding | PASS | `#/$defs/NumericPreferenceValue/properties/unit`; mechanical row check PASS |
| 111 | CodedContextValue.kind | required const coded | SCHEMA | required + const | PASS | `#/$defs/CodedContextValue/properties/kind`; mechanical row check PASS |
| 112 | CodedContextValue.value | required Coding | PARTIAL | required + $ref Coding | PASS | `#/$defs/CodedContextValue/properties/value`; mechanical row check PASS |
| 113 | TextContextValue.kind | required const text | SCHEMA | required + const | PASS | `#/$defs/TextContextValue/properties/kind`; mechanical row check PASS |
| 114 | TextContextValue.value | required Text | PARTIAL | required + $ref Text | PASS | `#/$defs/TextContextValue/properties/value`; mechanical row check PASS |
| 115 | Context.value | required ContextValue | PARTIAL | required + $ref ContextValue | PASS | `#/$defs/Context/properties/value`; mechanical row check PASS |
| 116 | Context.provenance | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | PASS | `#/$defs/Context/properties/provenance`; mechanical row check PASS |
| 117 | CodedFactorValue.kind | required const coded | SCHEMA | required + const | PASS | `#/$defs/CodedFactorValue/properties/kind`; mechanical row check PASS |
| 118 | CodedFactorValue.value | required Coding | PARTIAL | required + $ref Coding | PASS | `#/$defs/CodedFactorValue/properties/value`; mechanical row check PASS |
| 119 | TextFactorValue.kind | required const text | SCHEMA | required + const | PASS | `#/$defs/TextFactorValue/properties/kind`; mechanical row check PASS |
| 120 | TextFactorValue.value | required Text | PARTIAL | required + $ref Text | PASS | `#/$defs/TextFactorValue/properties/value`; mechanical row check PASS |
| 121 | BehaviorFactor.role | required reported_reason\|observed_association\|antecedent\|explanatory | SCHEMA | required + enum | PASS | `#/$defs/BehaviorFactor/properties/role`; mechanical row check PASS |
| 122 | BehaviorFactor.factor | required FactorValue | PARTIAL | required + $ref FactorValue | PASS | `#/$defs/BehaviorFactor/properties/factor`; mechanical row check PASS |
| 123 | BehaviorFactor.direction | required factor_to_behavior\|behavior_to_factor\|unspecified; conditional role rule | SCHEMA | required + enum + if/then const for reported_reason/antecedent | PASS | `#/$defs/BehaviorFactor/properties/direction`; mechanical row check PASS |
| 124 | BehaviorFactor.provenance | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | PASS | `#/$defs/BehaviorFactor/properties/provenance`; mechanical row check PASS |

# Appendix C — 40 cross-cutting invariant audit ledger

| # | Invariant | Projection status | Frozen owner / mechanism | Audit classification | Evidence |
|---:|---|---|---|---|---|
| 1 | Optional scalar/object absence | SCHEMA | mechanism: required controls presence; property schema excludes null | PASS | 46 optional properties enumerated; 0 accept null |
| 2 | Closed Core field sets | SCHEMA | mechanism: unevaluatedProperties:false at concrete object boundary; additionalProperties:false only when all allowed properties are declared in that same non-composed object schema | PASS | 36/36 concrete structured object schemas closed; defects 0 |
| 3 | Required 1 / optional 0..1 | SCHEMA | mechanism: required + single property schema | PASS | 124-row field ledger and required-set audit PASS |
| 4 | Required 0..* | SCHEMA | mechanism: required + type:array + items; no minItems:1 | PASS | 3 root required-0..* arrays: no minItems:1 |
| 5 | Required 1..* | SCHEMA | mechanism: required + array + minItems:1 | PASS | 5 required-1..* arrays carry minItems:1 |
| 6 | Optional 0..* empty | PARTIAL | mechanism: Schema must accept [] (no minItems:1); remainder owner: canonicalizer | PASS | 11 optional-0..* arrays accept []; canonical omission remains deferred |
| 7 | Optional 1..* empty | SCHEMA | mechanism: minItems:1 when property present | PASS | 9 optional-1..* arrays carry minItems:1 |
| 8 | Root subjects non-empty | SCHEMA | mechanism: minItems:1 | PASS | PBDLDocument.subjects required + minItems:1; root attacks PASS |
| 9 | Mechanical tagged unions | SCHEMA | mechanism: oneOf + const discriminator; ActorRef oneOf by required ref vs kind | PASS | 6 frozen unions exact; 28 branch-count attacks PASS |
| 10 | Text / semantic-string nonblank | SCHEMA | mechanism: pattern with explicit Unicode White_Space exclusion | PASS | 11 direct nonblank patterns exactly equal frozen White_Space complement; 22 U+0085/U+FEFF attacks PASS |
| 11 | Temporal lexical + calendar validity | PARTIAL | mechanism: oneOf/pattern for lexical profiles/component ranges; remainder owner: semantic validator | PASS | 6 lexical branches; 28 attacks PASS; 2026-02-30 remains Schema-valid by design |
| 12 | Collection semantic order-insensitivity | NOT_SCHEMA | owner: canonicalizer / equality semantics | NON_SCHEMA_CORRECTLY_DEFERRED | No ordering/sorting assertion encoded |
| 13 | Full-equal duplicate normalization | NOT_SCHEMA | owner: canonicalizer | NON_SCHEMA_CORRECTLY_DEFERRED | Only days_of_week uses uniqueItems; generic duplicate arrays remain Schema-valid |
| 14 | days_of_week duplicate token | SCHEMA | mechanism: uniqueItems:true because items are exact enum strings | PASS | Exactly one uniqueItems:true occurrence, on RecurrenceFrequency.days_of_week |
| 15 | Shared EntityId uniqueness | NOT_SCHEMA | owner: resolver / semantic validator | NON_SCHEMA_CORRECTLY_DEFERRED | Duplicate Subject ids remain Schema-valid |
| 16 | SubjectRef resolution | NOT_SCHEMA | owner: resolver | NON_SCHEMA_CORRECTLY_DEFERRED | Unresolved SubjectRef remains Schema-valid |
| 17 | CoreEntityRef resolution | NOT_SCHEMA | owner: resolver | NON_SCHEMA_CORRECTLY_DEFERRED | Unresolved CoreEntityRef remains Schema-valid |
| 18 | Identity vs canonical-information equality | NOT_SCHEMA | owner: semantic equality layer | NON_SCHEMA_CORRECTLY_DEFERRED | No equality/canonical-state assertion encoded |
| 19 | PBDLDocument equality | NOT_SCHEMA | owner: canonicalizer / equality semantics | NON_SCHEMA_CORRECTLY_DEFERRED | No order-insensitive equality approximation encoded |
| 20 | Text fallback dimension locality | NOT_SCHEMA | owner: semantic validator / canonicalizer | NON_SCHEMA_CORRECTLY_DEFERRED | Text Preference/Context/Factor fallbacks remain shape-valid; no NLP-like rule |
| 21 | Relation object shape | SCHEMA | mechanism: properties/required/$ref/closure | PASS | Exact six-property Relation surface; extra id/weight/direction/directionality/inverse/symmetric rejected |
| 22 | Relation directionality | NOT_SCHEMA | owner: Relation Vocabulary + semantic validator | NON_SCHEMA_CORRECTLY_DEFERRED | No generic directionality keyword/field/code rule |
| 23 | Symmetric swapped-endpoint equality | NOT_SCHEMA | owner: Relation Vocabulary + semantic validator | NON_SCHEMA_CORRECTLY_DEFERRED | No endpoint swap/equality rule encoded |
| 24 | Symmetric swapped-endpoint dedup | NOT_SCHEMA | owner: Relation Vocabulary + canonicalizer | NON_SCHEMA_CORRECTLY_DEFERRED | No endpoint sorting or generic uniqueItems approximation |
| 25 | Relation inverse conventions | NOT_SCHEMA | owner: Relation Vocabulary | NON_SCHEMA_CORRECTLY_DEFERRED | No inverse vocabulary encoded |
| 26 | Concrete terminology validation | NOT_SCHEMA | owner: terminology layer | NON_SCHEMA_CORRECTLY_DEFERRED | Arbitrary structurally valid Coding remains valid |
| 27 | Context vs BehaviorFactor classification | NOT_SCHEMA | owner: semantic validator / canonicalizer | NON_SCHEMA_CORRECTLY_DEFERRED | No discriminator/semantic classification rule added |
| 28 | Nested provenance present/non-empty | SCHEMA | mechanism: array + minItems:1 | PASS | 8 local provenance arrays are optional with minItems:1 |
| 29 | Nested provenance inheritance/equality | NOT_SCHEMA | owner: canonicalizer / semantic validator | NON_SCHEMA_CORRECTLY_DEFERRED | No owner/local provenance comparison encoded |
| 30 | Provenance derivation conditions | PARTIAL | mechanism: if/then/required + anyOf for structural traceability; remainder owner: semantic validator | PASS | 11 direct/inferred/undetermined attack cases PASS; semantic quality remains deferred |
| 31 | Evidence content-or-locator | SCHEMA | mechanism: anyOf required content\|required locator | PASS | content-only / locator-only / both valid; neither invalid |
| 32 | Interval boundary presence | SCHEMA | mechanism: anyOf required start\|required end | PASS | start-only / end-only / both valid; neither invalid |
| 33 | Interval temporal ordering | NOT_SCHEMA | owner: semantic validator | NON_SCHEMA_CORRECTLY_DEFERRED | Reverse interval remains Schema-valid; comparison deferred |
| 34 | Confidence scale comparisons | NOT_SCHEMA | owner: semantic validator | NON_SCHEMA_CORRECTLY_DEFERRED | Inverted scale {min:100,max:0,value:20} remains Schema-valid |
| 35 | Recurrence weekday conditional | SCHEMA | mechanism: if required days_of_week then period const-shaped constraint + not(required times_per_period) | PASS | 8 conditional attacks PASS |
| 36 | BehaviorFactor role-direction conditional | SCHEMA | mechanism: if role enum[...] then direction const | PASS | 12 role×direction attacks PASS |
| 37 | Explanatory factor derivation | NOT_SCHEMA | owner: semantic validator | NON_SCHEMA_CORRECTLY_DEFERRED | No effective-provenance inference rule encoded |
| 38 | Dimensioned NumericPreference unit preservation | NOT_SCHEMA | owner: semantic validator + terminology layer | NON_SCHEMA_CORRECTLY_DEFERRED | unit remains optional structurally; no source/category guessing |
| 39 | Canonical field aliases | SCHEMA | mechanism: closed object field sets | PASS | Concrete object closure rejects undeclared legacy aliases |
| 40 | Deterministic byte-level JSON ordering | NOT_SCHEMA | owner: serialization profile | NON_SCHEMA_CORRECTLY_DEFERRED | No serializer/order profile encoded |

# Appendix D — Explicit no-approximation matrix

| # | Prohibited approximation | Audit evidence | Verdict |
|---:|---|---|---|
| 1 | semantic duplicate prohibition → generic uniqueItems | only days_of_week uses uniqueItems; duplicate Provenance/Relation instances remain valid | NON_SCHEMA_CORRECTLY_DEFERRED |
| 2 | reference existence → EntityId shape | unresolved SubjectRef/CoreEntityRef attacks remain valid | NON_SCHEMA_CORRECTLY_DEFERRED |
| 3 | symmetric Relation → endpoint sorting | no endpoint sorting/equality assertion exists | NON_SCHEMA_CORRECTLY_DEFERRED |
| 4 | optional [] omission → structural invalidity | all optional 0..* arrays accept [] | NON_SCHEMA_CORRECTLY_DEFERRED |
| 5 | terminology validation → invented code enum | arbitrary structurally valid Coding accepted | NON_SCHEMA_CORRECTLY_DEFERRED |
| 6 | Context vs BehaviorFactor → added discriminator | no classification discriminator added | NON_SCHEMA_CORRECTLY_DEFERRED |
| 7 | Relation directionality → guessed generic rule | no directionality rule/code enum added | NON_SCHEMA_CORRECTLY_DEFERRED |
| 8 | order-insensitive equality → sorting profile | no sorting/order profile encoded | NON_SCHEMA_CORRECTLY_DEFERRED |
| 9 | Confidence semantics → universal 0..1 / sibling comparisons | inverted/out-of-range structural example remains valid | NON_SCHEMA_CORRECTLY_DEFERRED |
| 10 | TemporalValue semantics → format/timezone/precision approximation | explicit lexical profiles only; Gregorian invalid date remains valid | NON_SCHEMA_CORRECTLY_DEFERRED |

# Appendix E — Non-Schema responsibility matrix

| Responsibility | Frozen owner | Current Schema result |
|---|---|---|
| reference resolution | resolver | NOT ENCODED — CORRECTLY DEFERRED |
| shared EntityId uniqueness | resolver / semantic validator | NOT ENCODED — CORRECTLY DEFERRED |
| semantic source-support interpretation | semantic validator / canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| Context vs BehaviorFactor classification | semantic validator / canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| provenance semantic equality | semantic validator / canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| provenance inheritance | canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| Relation directionality | Relation Vocabulary + semantic validator | NOT ENCODED — CORRECTLY DEFERRED |
| Relation vocabulary | Relation Vocabulary | NOT ENCODED — CORRECTLY DEFERRED |
| Relation inverse rules | Relation Vocabulary | NOT ENCODED — CORRECTLY DEFERRED |
| symmetric swapped equality | Relation Vocabulary + semantic validator | NOT ENCODED — CORRECTLY DEFERRED |
| symmetric dedup | Relation Vocabulary + canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| terminology validation | terminology layer | NOT ENCODED — CORRECTLY DEFERRED |
| canonical duplicate removal | canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| canonical-information equality | semantic equality / canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| Text fallback interpretation | semantic validator / canonicalizer | NOT ENCODED — CORRECTLY DEFERRED |
| interval comparison | semantic validator | NOT ENCODED — CORRECTLY DEFERRED |
| Confidence sibling comparison | semantic validator | NOT ENCODED — CORRECTLY DEFERRED |
| deterministic serialization | future serialization profile | NOT ENCODED — CORRECTLY DEFERRED |

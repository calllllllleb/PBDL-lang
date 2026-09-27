# R2B4 — Canonical Representation & Serialization Audit

> **NON-NORMATIVE**
>
> 本文记录 R2B4 audit inventory、decision tables 与 R2C施工地图。所有 normative conclusions 以 `spec/PBDL-v1.0-SPEC.md` §22 为准。

## Baseline

- Repository: `calllllllleb/PBDL-lang`
- Start HEAD: `f410e7039af945ea7e48281ee0646dfeffbcfe41`
- Branch: `r2b4-canonical-representation-audit`

R2B4没有发现需要重开 frozen business architecture 的 mechanical contradiction。

## 1. Complete canonical type inventory

| Type | Required fields / value | Optional fields | Collections | Union discriminator | Identity-bearing | Provenance-bearing | Equality / ordering |
|---|---|---|---|---|---|---|---|
| PBDLDocument | pbdl_version, subjects, behaviors, preferences, relations | — | 4 root arrays | — | document root | via contained assertions | root order-insensitive |
| Subject | id | — | — | — | YES | NO | identity=id; info=id |
| Behavior | id, subject, type, provenance | executor, temporal | frequencies, contexts, factors, annotations | — | YES | YES | identity=id; full fields |
| Preference | id, subject, category, value, provenance | temporal | contexts, annotations | — | YES | YES | identity=id; full fields |
| Relation | source, target, type, provenance | temporal | annotations | — | NO | YES | content + full equality |
| Annotation | text, provenance | — | provenance | — | NO | YES | text content + full provenance |
| VersionToken | exactly "1.0" | — | — | — | NO | NO | exact token |
| EntityId | regex token | — | — | — | instance key | NO | exact token |
| Text | Unicode nonblank string | — | — | — | NO | NO | exact scalar sequence |
| TemporalValue | constrained temporal string | — | — | lexical profile | NO | NO | exact canonical information |
| Coding | system, code | display, version | — | — | terminology identity | NO | system+code identity; full info includes display/version |
| Confidence | value, metric | scale | — | — | NO | NO | exact numeric + metric + scale |
| SubjectRef | ref | — | — | structural ref | NO | NO | ref exact |
| CoreEntityRef | ref | — | — | structural ref | NO | NO | ref exact |
| ExternalActorRef | kind | external_id, display, role | — | kind | NO Core identity | NO | all fields |
| ActorRef | variant | — | — | ref vs kind | NO | NO | same variant + variant equality |
| SourceDescriptor | kind | locator, display, times | times | kind token family | NO | NO | all fields, times unordered |
| SourceTimeEvent | role, at | — | — | role token | NO | NO | role + TemporalValue |
| GeneratorDescriptor | kind | identifier, version, display, times | times | kind token family | NO | NO | all fields, times unordered |
| GeneratorTimeEvent | role, at | — | — | role token | NO | NO | role + TemporalValue |
| Evidence | kind + content or locator | content, locator, times | times | kind token family | NO | NO | all fields, times unordered |
| Provenance | derivation | source, generator, evidence, confidence | evidence | derivation token | NO | self | §17.10.3 |
| Instant | kind="instant", at | provenance | provenance | kind | NO | optional local | content/full |
| Interval | kind="interval", start or end | start, end, provenance | provenance | kind | NO | optional local | content/full |
| TemporalExtent | variant | — | — | kind | NO | optional local | content/full |
| FrequencyPeriod | value, unit | — | — | — | NO | NO | exact numeric+unit |
| ObservedCountFrequency | kind,count,precision | window, provenance | provenance | kind | NO | optional local | content/full |
| RateFrequency | kind,value,period,precision | provenance | provenance | kind | NO | optional local | content/full |
| RecurrenceFrequency | kind,period,precision | times_per_period, days_of_week, day_part, provenance | days_of_week, provenance | kind | NO | optional local | content/full |
| QualitativeFrequency | kind,value | provenance | provenance | kind | NO | optional local | content/full |
| BehaviorFrequency | variant | — | — | kind | NO | optional local | content/full |
| CodedPreferenceValue | kind,value | — | — | kind | NO | NO | Coding full equality |
| TextPreferenceValue | kind,value | — | — | kind | NO | NO | Text equality |
| BooleanPreferenceValue | kind,value | — | — | kind | NO | NO | boolean equality |
| NumericPreferenceValue | kind,operator,value | unit | — | kind | NO | NO | operator+number+unit |
| PreferenceValue | variant | — | — | kind | NO | NO | same variant |
| CodedContextValue | kind,value | — | — | kind | NO | NO | Coding equality |
| TextContextValue | kind,value | — | — | kind | NO | NO | Text equality |
| ContextValue | variant | — | — | kind | NO | NO | same variant |
| Context | value | provenance | provenance | — | NO | optional local | content/full |
| FactorRole | token | — | — | — | NO | NO | exact token |
| FactorDirection | token | — | — | — | NO | NO | exact token |
| CodedFactorValue | kind,value | — | — | kind | NO | NO | Coding equality |
| TextFactorValue | kind,value | — | — | kind | NO | NO | Text equality |
| FactorValue | variant | — | — | kind | NO | NO | same variant |
| BehaviorFactor | role,factor,direction | provenance | provenance | — | NO | optional local | content/full |

### Token / enum families

- DerivationKind: direct / inferred / undetermined
- SourceKind: patient_self_report / questionnaire / clinician_documentation / ehr_record / device_observation / legacy_record / other
- SourceTimeEvent.role: reported / recorded / observed
- GeneratorKind: human / llm / rule_engine / analytic_model / migration_process / other
- GeneratorTimeEvent.role: extracted / generated / transformed / migrated
- EvidenceKind: text_excerpt / document_reference / questionnaire_response / device_observation / legacy_material / other
- ExternalActorRef.kind: person / device / software / other
- QuantitativeFrequencyPrecision: exact / approximate
- FrequencyPeriod.unit: day / week / month / year
- Weekday: mon / tue / wed / thu / fri / sat / sun
- DayPart: morning / afternoon / evening / night
- QualitativeFrequencyToken: never / rarely / occasionally / sometimes / often / frequently / usually / intermittently / always
- NumericPreference operator: eq / lt / lte / gt / gte
- FactorRole: reported_reason / observed_association / antecedent / explanatory
- FactorDirection: factor_to_behavior / behavior_to_factor / unspecified

## 2. Absent / null / empty

| Case | Decision |
|---|---|
| optional field absent | canonical absence |
| optional field = null | invalid |
| required root array empty | behaviors/preferences/relations allowed; subjects not allowed |
| optional collection cardinality 0..* and empty | MAY be semantic-valid but normalization-required → omit |
| optional collection cardinality 1..* and present empty | invalid |
| days_of_week=[] | invalid; field is 1..* when present |
| local provenance=[] | invalid; field is 1..* when present and omission means inheritance |
| required provenance=[] | invalid |

## 3. Union discrimination

| Union | Mechanical key |
|---|---|
| ActorRef | ref XOR kind |
| TemporalExtent | kind=instant/interval |
| BehaviorFrequency | kind=observed_count/rate/recurrence/qualitative |
| PreferenceValue | kind=coded/text/boolean/number |
| ContextValue | kind=coded/text |
| FactorValue | kind=coded/text |

Closed field sets prevent one object matching multiple variants.

## 4. Collection audit

| Collection | Ordered? | Duplicate policy |
|---|---|---|
| subjects/behaviors/preferences | no | duplicate id invalid |
| relations | no | full-equal duplicate normalized under Relation.type directionality contract; symmetric swapped endpoints may dedup only when applicable vocabulary contract establishes symmetry |
| provenance collections | no | full-equal duplicate normalized |
| evidence | no | full-equal duplicate normalized |
| annotations | no | full-equal duplicate normalized |
| frequencies | no | full qualifier-equal normalized |
| contexts | no | full qualifier-equal normalized |
| factors | no | full qualifier-equal normalized |
| days_of_week | no | duplicate token invalid |
| source/generator/evidence times | no | full-equal event normalized |

## 5. Equality audit

### Relation

Content:
- type
- temporal content
- directional type: source==source and target==target
- symmetric / non-directional type: endpoint pair compared unordered
- directionality contract unavailable: do not guess, swap, normalize, or deduplicate swapped endpoints

Full:
- content
- temporal full provenance
- relation provenance
- annotations

Same endpoints alone never equal. Symmetric swapped-endpoint equality / dedup requires the applicable Relation vocabulary contract and is owned by VOCABULARY + SEMANTIC + NORMALIZATION.

### TemporalExtent

Content:
- kind
- at / start / end

Full:
- content
- effective provenance

### Annotation

Content:
- text

Full:
- text
- provenance

### Entities

Identity equality:
- Subject / Behavior / Preference id

Canonical-information equality:
- all canonical fields

Same id can have different state.

### PBDLDocument

- same version
- order-insensitive one-to-one full entity match
- order-insensitive full Relation match using type-contract-aware Relation equality

## 6. Fallback purity

Text fallback is dimension-local.

`在家里比较规律`:
- 在家里 → Context when supported
- 比较规律 → BehaviorFrequency when supported
- unresolved original wording → Evidence / Annotation
- whole sentence MUST NOT become one Context machine value

Preference text does not hide associated Behavior link.
Factor text does not hide CoreEntityRef.
Context text does not hide workflow/frequency/temporal/reason semantics.

## 7. Conditional invariant and Schema-expressibility map

| Invariant | Owner class |
|---|---|
| EntityId regex | STRUCTURAL |
| subjects minItems=1 | STRUCTURAL |
| root behaviors/preferences/relations required | STRUCTURAL |
| closed Core fields | STRUCTURAL |
| optional null forbidden | STRUCTURAL |
| union discriminators | STRUCTURAL |
| ActorRef ref xor kind | STRUCTURAL |
| Interval start or end | STRUCTURAL |
| Evidence content or locator | STRUCTURAL |
| direct requires source | STRUCTURAL |
| inferred requires generator | STRUCTURAL |
| undetermined requires source | STRUCTURAL |
| undetermined traceability locator/evidence | STRUCTURAL + SEMANTIC |
| Confidence scale conditions | SEMANTIC / numeric |
| frequency numeric ranges | STRUCTURAL |
| recurrence weekday conditional | STRUCTURAL + SEMANTIC |
| reported_reason direction | STRUCTURAL conditional |
| antecedent direction | STRUCTURAL conditional |
| SubjectRef/CoreEntityRef resolution | REFERENCE |
| shared EntityId uniqueness | REFERENCE / SEMANTIC |
| relation endpoint type contract | VOCABULARY + SEMANTIC |
| Context vs Factor source meaning | SEMANTIC |
| text fallback purity | SEMANTIC |
| unit preservation when source provides unit | SEMANTIC |
| redundant local provenance | NORMALIZATION |
| full-equal duplicate removal | NORMALIZATION |
| optional 0..* empty collection omission | NORMALIZATION |
| optional 1..* collection present empty | STRUCTURAL / SEMANTIC invalid |
| symmetric Relation endpoint-order equality | VOCABULARY + SEMANTIC |
| symmetric swapped-endpoint dedup | VOCABULARY + SEMANTIC + NORMALIZATION |

## 8. Canonical-valid vs normal form

Normalization-required:
- ordinary optional 0..* []
- full-equal duplicate
- redundant explicit inherited provenance
- future JSON lexical/order normalization

Invalid:
- null
- unknown field
- days_of_week=[]
- local provenance=[]
- collection whose declared cardinality requires >=1 item is empty
- invalid union
- duplicate EntityId
- violated conditional invariant

## 9. Ordering decision

R2B4 selects semantic order-insensitivity.

No byte-level deterministic JSON ordering is defined.

Object key order has no semantic meaning.

A future deterministic serialization profile owns:
- key ordering
- array sorting
- number lexical spelling
- whitespace formatting

## 10. Remaining R2B debt

Not R2C blockers:
- deterministic byte serialization profile
- generic conversion/coercion policy
- provenance pool/chaining
- Relation vocabulary
- extension mechanism
- DSL / parser / validator/runtime
- examples

## 11. Exact R2C prerequisites

R2C can now implement structural JSON Schema using:
- frozen object fields/cardinality
- closed object policy
- null policy
- optional collection minItems/omission direction
- union discriminators
- lexical/numeric constraints
- conditional structural rules

R2C must leave:
- references to resolver
- semantic meaning to validator/canonicalizer
- duplicate/equality normalization to canonicalizer
- relation code contracts, including directional vs symmetric endpoint semantics, to Relation Vocabulary phase
- generic JSON Schema must not decide symmetric swapped-endpoint equality/dedup

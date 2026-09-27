# R2C0 — JSON Schema Projection Contract

> **Status:** R2C0 projection contract
> **Normative authority:** `spec/PBDL-v1.0-SPEC.md` at R2B frozen HEAD `329ac9e643adb56ee4d5e89a9515947f34b5a0aa`
> **Target dialect:** JSON Schema Draft 2020-12
> **Scope:** projection only; this document does not modify frozen PBDL Core semantics and does not implement Schema.

## 1. Purpose and hard boundary

R2C projects the frozen R2B canonical representation into JSON Schema Draft 2020-12. It does not redesign the object model, field ownership, names, cardinality, union semantics, references, Relation semantics, canonical equality, duplicate semantics, terminology, vocabulary, or serialization profile.

Projection status vocabulary:

- **SCHEMA** — Draft 2020-12 can faithfully enforce the frozen validity rule.
- **PARTIAL** — a structural portion is Schema-expressible, but a frozen semantic / equality / normalization / reference portion must remain outside Schema.
- **NOT_SCHEMA** — the rule must not be approximated by a different structural assertion.

**Projection law:** Schema **MUST NOT approximate a non-schema semantic rule by imposing a different structural rule**.

The authoritative source is the SPEC. Design rationale and R2B audit documents may be used only as cross-checks. Existing placeholder Schema, examples, grammar, historical files, or implementation behavior must not be used to redefine the contract.

## 2. Draft 2020-12 mechanism policy

### 2.1 Closed objects

Every concrete Core object / embedded structured object is closed.

For Draft 2020-12, the default projection rule is:

- use `properties` / `required` for declared fields;
- use `unevaluatedProperties: false` at the concrete object boundary when the object is composed through `$ref`, `allOf`, `oneOf`, or adjacent applicators;
- `additionalProperties: false` is safe only where the complete allowed property set is declared in that same non-composed object schema.

R2C1–R2C4 **MUST NOT** mechanically place `additionalProperties:false` in a base subschema and assume it closes properties introduced by sibling/composed schemas.

### 2.2 Unions

Frozen tagged unions project as `oneOf` over concrete closed variants:

- `kind`-tagged unions use `const` in each branch;
- ActorRef uses required-property structural discrimination: SubjectRef requires `ref`; ExternalActorRef requires `kind`; concrete branch closure keeps the variants exclusive.

`anyOf` is reserved for rules where multiple alternatives may simultaneously hold, such as Evidence content-or-locator or Interval start-or-end presence.

### 2.3 `format`

Draft 2020-12 separates format annotation from format assertion; the default meta-schema does not make `format` alone a sufficient normative validator. PBDL TemporalValue also contains partial-date and bracketed ZoneToken profiles that do not map cleanly to the standard date-time format.

Therefore R2C **MUST NOT** claim a PBDL lexical invariant is enforced merely by writing `format`. Use explicit structural constraints/patterns for the expressible lexical portion and leave remaining calendar/comparability semantics to the semantic validator.

### 2.4 Arrays and `uniqueItems`

`uniqueItems` compares JSON instance values structurally. It is **not** the PBDL canonical-information equality engine.

R2C **MUST NOT** apply `uniqueItems:true` to arrays merely because PBDL canonicalization removes full-equal semantic duplicates. It is allowed only when frozen invalidity is exactly equivalent to JSON structural duplication. The current clear case is `days_of_week`, whose items are exact Weekday tokens and duplicate token is invalid.

## 3. Complete named-type projection inventory

The denominator is the complete §22.1 named type / token-family inventory: **54 entries**.

Type-level counts:

- SCHEMA: **15**
- PARTIAL: **39**
- NOT_SCHEMA: **0**

A PARTIAL type is not permission to weaken its structural projection. R2C must implement every listed structural rule and explicitly leave the rest to the stated owner.

| Type | Normative source | Frozen representation rule | Status | Draft 2020-12 mechanism | Non-Schema owner | Notes / traps |
|---|---|---|---|---|---|---|
| PBDLDocument | §17.1–17.2; §22.2–22.3; §22.9.7 | five required fields; 4 required root arrays; subjects 1..*, other root arrays 0..*; closed; root semantic order-insensitive | PARTIAL | object/properties/required/items/minItems; concrete-object closure | resolver; semantic validator; canonicalizer | Schema cannot enforce shared EntityId uniqueness, reference resolution, document equality, or order-insensitive semantic equality. |
| Subject | §17.3; §5.3 | closed object with required id: EntityId; identity-bearing in shared document-local namespace | PARTIAL | object/properties/required/$ref; closure | resolver / semantic validator | Schema validates id shape, not uniqueness across Subject/Behavior/Preference. |
| Behavior | §17.4; §22.2–22.3 | closed object; required id, subject, type, provenance[1..*]; optional executor, temporal, frequencies, contexts, factors, annotations | PARTIAL | object/properties/required/$ref; minItems:1 for provenance; arrays accept [] for optional 0..* | resolver; semantic validator; canonicalizer | Do not minItems:1 optional 0..* arrays; local provenance/equality semantics are non-Schema. |
| Preference | §17.5; §22.2–22.3 | closed object; required id, subject, category, value, provenance[1..*]; optional temporal, contexts, annotations | PARTIAL | object/properties/required/$ref; minItems:1 provenance | resolver; semantic validator; canonicalizer | Legacy aliases must remain unknown/invalid Core fields. |
| Relation | §17.6; §14.6–14.11; §22.9.3; §22.14 | closed no-id assertion; required source,target,type,provenance[1..*]; optional temporal,annotations; directionality owned by type contract | PARTIAL | object/properties/required/$ref; minItems:1 provenance | Relation Vocabulary; semantic validator; canonicalizer | Schema validates endpoint/reference shapes only; never infers directional/symmetric semantics or swapped equality/dedup. |
| Annotation | §17.9; §22.9.2 | embedded no-id object; required text and provenance[1..*]; closed | PARTIAL | object/properties/required/$ref; minItems:1 | canonicalizer / semantic validator | Schema validates shape; content/full equality and duplicate normalization are not Schema. |
| VersionToken | §17.1 | PBDL 1.0 token is exactly "1.0" | SCHEMA | type:string + const:"1.0" | — | Do not generalize to implementation-defined versions. |
| EntityId | §17.3; §22.13 | ASCII token [A-Za-z_][A-Za-z0-9._-]* | SCHEMA | type:string + pattern | — | Pattern does not establish reference existence or document-wide uniqueness. |
| Text | §8.1 | Unicode string containing at least one non-Unicode-White_Space code point; no trim/case-fold/Unicode normalization | SCHEMA | type:string + pattern excluding all-whitespace strings | canonicalizer for no-normalization policy | Do not use minLength alone; it would accept whitespace-only Text. |
| TemporalValue | §8.2 | constrained year/month/date/date-time lexical profiles preserving precision and optional offset/ZoneToken; real Gregorian dates; conservative comparability | PARTIAL | type:string + oneOf/pattern for lexical families and component ranges | semantic validator | Do not rely on format alone; Draft 2020-12 default format is annotation, and custom profiles exceed standard date-time. |
| Coding | §15; §22.6 | closed object; required nonblank system/code; optional Text display and nonblank version | PARTIAL | object/properties/required/pattern/$ref; closure | terminology layer; canonicalizer | Schema validates representation, not code-system membership, Coding identity, or canonical-information equality. |
| Confidence | §17.8.6; §22.7 | closed object; required finite number value + nonblank metric; optional scale{min,max}; if scale present min<max and value within [min,max] | PARTIAL | object/properties/required/type:number; closed nested scale | semantic validator | Draft 2020-12 has no standard sibling numeric data comparison for value vs scale bounds. |
| SubjectRef | §17.7.1 | closed {ref: EntityId}; must resolve to exactly one Subject | PARTIAL | object/properties/required/$ref; closure | resolver | Pattern-valid ref is not proof of existence/type. |
| CoreEntityRef | §17.7.2 | closed {ref: EntityId}; must resolve to exactly one Behavior or Preference and satisfy endpoint contracts | PARTIAL | object/properties/required/$ref; closure | resolver; Relation Vocabulary; semantic validator | Do not encode current document IDs as enum. |
| ExternalActorRef | §17.4.2; §22.4 | closed object; required kind enum; optional closed external_id{system,value}, display, role | SCHEMA | object/properties/required/enum/pattern/$ref; closure | — | display/role never establish stable identity; Schema need not infer sameness. |
| ActorRef | §17.4.2; §22.4 | SubjectRef \| ExternalActorRef, structurally disjoint; ref and kind cannot coexist | PARTIAL | oneOf [$ref SubjectRef,$ref ExternalActorRef] with concrete branches closed | resolver | Use oneOf, not guessed union dispatch. |
| DerivationKind | §17.8.1 | "direct" \| "inferred" \| "undetermined" | SCHEMA | enum | — | No synonym tokens. |
| SourceKind | §17.8.3 | seven frozen source-kind lowercase tokens | SCHEMA | enum | — | Do not add domain-specific kinds in Core. |
| SourceDescriptor | §17.8.3; §22.8 | closed; required kind; optional nonblank locator, Text display, SourceTimeEvent times[0..*] | PARTIAL | object/properties/required/enum/pattern/array/$ref | canonicalizer | times order/equality and duplicate normalization are not Schema. |
| SourceTimeEvent | §17.8.3 | closed; required role reported\|recorded\|observed and at:TemporalValue | PARTIAL | object/properties/required/enum/$ref | semantic validator | TemporalValue remains PARTIAL. |
| GeneratorKind | §17.8.4 | human\|llm\|rule_engine\|analytic_model\|migration_process\|other | SCHEMA | enum | — | Generator presence does not imply inferred. |
| GeneratorDescriptor | §17.8.4; §22.8 | closed; required kind; optional nonblank identifier/version, Text display, GeneratorTimeEvent times[0..*] | PARTIAL | object/properties/required/enum/pattern/array/$ref | canonicalizer | times semantic order/equality and duplicate normalization are non-Schema. |
| GeneratorTimeEvent | §17.8.4 | closed; required role extracted\|generated\|transformed\|migrated and at:TemporalValue | PARTIAL | object/properties/required/enum/$ref | semantic validator | TemporalValue remains PARTIAL. |
| EvidenceKind | §17.8.5 | six frozen evidence-kind tokens | SCHEMA | enum | — | Do not infer Evidence vs Annotation from strings. |
| Evidence | §17.8.5 | closed; required kind; content? Text; locator? nonblank string; at least content or locator; times? SourceTimeEvent[0..*] | PARTIAL | object/properties/required/anyOf(required content\|required locator)/$ref | canonicalizer / semantic validator | Optional times=[] must stay structurally valid but noncanonical; duplicate normalization non-Schema. |
| Provenance | §17.8; §17.10; §22.13 | closed; derivation required; conditional source/generator; evidence 0..*; confidence?; direct=>source; inferred=>generator; undetermined=>source plus locator or evidence | PARTIAL | if/then + required + anyOf/contains/minItems where structural; properties/$ref | semantic validator; canonicalizer | Undetermined misuse warning, semantic equality, inheritance, redundant-local omission are non-Schema. |
| Instant | §17.4.3; §22.4 | kind="instant", required at, optional provenance[1..*] | PARTIAL | const discriminator; required; $ref; minItems:1 if provenance present | semantic validator; canonicalizer | TemporalValue validity and local provenance inheritance/equality are PARTIAL/non-Schema. |
| Interval | §17.4.3; §8.2.6; §22.4 | kind="interval"; start?/end? with at least one; optional provenance[1..*]; definitely-later start invalid | PARTIAL | const; anyOf required start\|required end; $ref; minItems:1 local provenance | semantic validator; canonicalizer | Cross-boundary temporal comparability/order is not faithfully expressible in standard Schema. |
| TemporalExtent | §17.4.3; §22.4; §22.9.1 | Instant \| Interval, mechanical kind discriminator | PARTIAL | oneOf concrete closed variants | semantic validator; canonicalizer | Schema does not implement content/full equality or inherited provenance semantics. |
| QuantitativeFrequencyPrecision | §8.3.1 | "exact" \| "approximate" | SCHEMA | enum | — | Not Confidence. |
| FrequencyPeriod | §8.3.2 | closed {value: integer>=1, unit: day\|week\|month\|year} | SCHEMA | object/properties/required/type:integer/minimum:1/enum; closure | — | Do not convert month/year to days. |
| Weekday | §8.3.5 | mon\|tue\|wed\|thu\|fri\|sat\|sun | SCHEMA | enum | — | Token order is not semantic. |
| DayPart | §8.3.5 | morning\|afternoon\|evening\|night | SCHEMA | enum | — | No clock-hour thresholds. |
| QualitativeFrequencyToken | §8.3.6 | nine frozen qualitative tokens | SCHEMA | enum | — | No numeric ordering/threshold semantics. |
| ObservedCountFrequency | §8.3.3; §22.4 | kind observed_count; required count integer>=0, precision; optional Interval window; optional provenance[1..*] | PARTIAL | const/required/integer/minimum/$ref/minItems:1 local provenance | semantic validator; canonicalizer | Window meaning, semantic equality, and local provenance inheritance are non-Schema. |
| RateFrequency | §8.3.4; §22.4 | kind rate; required value number>=0, period, precision; optional provenance[1..*] | PARTIAL | const/required/type:number/minimum:0/$ref/minItems:1 | canonicalizer | Schema does not interpret rate semantics or provenance inheritance. |
| RecurrenceFrequency | §8.3.5; §22.4 | kind recurrence; required period,precision; optional positive times_per_period, days_of_week[1..*], day_part, provenance[1..*]; days_of_week implies period=1 week and no times_per_period | PARTIAL | const/required/minimum; if days_of_week then minItems:1 + uniqueItems:true + period const/object constraint + not required times_per_period | semantic validator; canonicalizer | uniqueItems is safe only for Weekday tokens because duplicate token is structurally invalid; recurrence meaning remains semantic. |
| QualitativeFrequency | §8.3.6; §22.4 | kind qualitative; required token value; optional provenance[1..*] | PARTIAL | const/required/enum/minItems:1 local provenance | semantic validator; canonicalizer | Scope and provenance inheritance are non-Schema. |
| BehaviorFrequency | §8.3; §22.4 | four-way kind-discriminated union | PARTIAL | oneOf closed variants with const kind | semantic validator; canonicalizer | Do not collapse variants or encode semantic equality. |
| CodedPreferenceValue | §8.4.1; §22.4 | kind coded; required Coding value | PARTIAL | const/required/$ref; closure | terminology layer / semantic validator | Reliable terminology mapping is semantic, not Schema. |
| TextPreferenceValue | §8.4.2; §22.12 | kind text; required Text value; fidelity fallback only | PARTIAL | const/required/$ref; closure | semantic validator / canonicalizer | Schema cannot decide whether text fallback is legitimate or hides structured semantics. |
| BooleanPreferenceValue | §8.4.3 | kind boolean; required boolean value | PARTIAL | const/required/type:boolean; closure | semantic validator | Whether category semantics permit boolean is not Schema. |
| NumericPreferenceValue | §8.4.4; §22.13 | kind number; required operator enum and finite number value; optional Coding unit; source/category may require unit | PARTIAL | const/required/enum/type:number/$ref | semantic validator; terminology layer | Schema cannot know source/category requires unit; do not force unit universally. |
| PreferenceValue | §8.4; §22.4 | four-way kind-discriminated union | PARTIAL | oneOf closed variants | semantic validator; terminology layer | Union shape is Schema; category/value compatibility and fallback legitimacy are not. |
| CodedContextValue | §8.5.1; §22.4 | kind coded; required Coding value | PARTIAL | const/required/$ref; closure | terminology layer / semantic validator | Reliable context coding and Context-vs-Factor meaning are non-Schema. |
| TextContextValue | §8.5.1; §22.12 | kind text; required Text value; contextual fidelity fallback | PARTIAL | const/required/$ref; closure | semantic validator / canonicalizer | Schema cannot determine cross-dimension leakage. |
| ContextValue | §8.5.1; §22.4 | coded\|text tagged union | PARTIAL | oneOf closed variants | semantic validator; terminology layer | Do not reuse PreferenceValue or add new variants. |
| Context | §8.5; §17.10 | closed embedded qualifier; required value; optional provenance[1..*] | PARTIAL | object/required/$ref/minItems:1 if provenance present; closure | semantic validator; canonicalizer | Context classification, local provenance inheritance/equality, duplicate normalization are non-Schema. |
| FactorRole | §8.6.1 | reported_reason\|observed_association\|antecedent\|explanatory | SCHEMA | enum | — | No causal role added. |
| FactorDirection | §8.6.2 | factor_to_behavior\|behavior_to_factor\|unspecified | SCHEMA | enum | — | Direction is not causality. |
| CodedFactorValue | §8.6.3; §22.4 | kind coded; required Coding value | PARTIAL | const/required/$ref; closure | terminology layer / semantic validator | Reliable terminology mapping is non-Schema. |
| TextFactorValue | §8.6.3; §22.12 | kind text; required Text value | PARTIAL | const/required/$ref; closure | semantic validator / canonicalizer | Text must not hide existing Core entity relationship. |
| FactorValue | §8.6.3; §22.4 | coded\|text tagged union | PARTIAL | oneOf closed variants | semantic validator; terminology layer | No CoreEntityRef variant. |
| BehaviorFactor | §8.6; §22.13 | closed qualifier; required role,factor,direction; optional provenance[1..*]; antecedent/reported_reason require factor_to_behavior | PARTIAL | object/required/$ref; if role in {antecedent,reported_reason} then direction const factor_to_behavior; minItems:1 local provenance | semantic validator; canonicalizer | Explanatory inferred semantics, causality boundary, entity-vs-factor classification and provenance inheritance are non-Schema. |

## 4. Field-level mechanical projection inventory

This section makes the frozen field inventory directly implementable without re-deciding field ownership or token sets. It contains **124 field/constraint projection entries**.

Field-level counts:

- SCHEMA: **59**
- PARTIAL: **65**
- NOT_SCHEMA: **0**

| Type / field | Normative source | Frozen rule | Status | Draft 2020-12 mechanism | Non-Schema owner | Notes / traps |
|---|---|---|---|---|---|---|
| PBDLDocument.pbdl_version | §17.1 | required VersionToken; exactly "1.0" | SCHEMA | required + $ref VersionToken | — | No build/schema/model version here. |
| PBDLDocument.subjects | §17.1–17.2 | required Subject[1..*] | PARTIAL | required; array/items $ref; minItems:1 | resolver / semantic equality | Order-insensitivity and shared-id uniqueness are outside Schema. |
| PBDLDocument.behaviors | §17.1–17.2 | required Behavior[0..*], [] valid | PARTIAL | required; array/items $ref; no minItems:1 | resolver / canonicalizer | No uniqueItems; root order is not semantic. |
| PBDLDocument.preferences | §17.1–17.2 | required Preference[0..*], [] valid | PARTIAL | required; array/items $ref; no minItems:1 | resolver / canonicalizer | No uniqueItems. |
| PBDLDocument.relations | §17.1–17.2; §22.9.3 | required Relation[0..*], [] valid | PARTIAL | required; array/items $ref; no minItems:1 | Relation Vocabulary / canonicalizer | No uniqueItems; Relation equality is vocabulary-aware. |
| Subject.id | §17.3 | required EntityId | PARTIAL | required + $ref EntityId | resolver / semantic validator | Shared namespace uniqueness is document-wide. |
| Behavior.id | §17.4 | required EntityId | PARTIAL | required + $ref EntityId | resolver / semantic validator | Shared namespace uniqueness outside Schema. |
| Behavior.subject | §17.4; §17.7.1 | required SubjectRef | PARTIAL | required + $ref SubjectRef | resolver | Must resolve exactly one Subject. |
| Behavior.type | §17.4.1; §15 | required Coding | PARTIAL | required + $ref Coding | terminology layer | Schema does not validate concrete terminology membership. |
| Behavior.executor | §17.4.2 | optional ActorRef | PARTIAL | $ref ActorRef; omit from required | resolver | null invalid. |
| Behavior.temporal | §17.4.3 | optional TemporalExtent | PARTIAL | $ref TemporalExtent; omit from required | semantic validator / canonicalizer | null invalid. |
| Behavior.frequencies | §17.4.4; §22.3.3 | optional BehaviorFrequency[0..*]; [] noncanonical but valid | PARTIAL | array/items $ref; no minItems:1 | canonicalizer | Empty field must remain structurally valid. |
| Behavior.contexts | §17.4.5; §22.3.3 | optional Context[0..*] | PARTIAL | array/items $ref; no minItems:1 | semantic validator / canonicalizer | No uniqueItems. |
| Behavior.factors | §17.4.6; §22.3.3 | optional BehaviorFactor[0..*] | PARTIAL | array/items $ref; no minItems:1 | semantic validator / canonicalizer | No uniqueItems. |
| Behavior.provenance | §17.4; §17.8 | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | semantic validator / canonicalizer | No uniqueItems; equality not structural. |
| Behavior.annotations | §17.4; §22.3.3 | optional Annotation[0..*] | PARTIAL | array/items $ref; no minItems:1 | canonicalizer | Full-equal duplicate removal is normalization. |
| Preference.id | §17.5 | required EntityId | PARTIAL | required + $ref EntityId | resolver / semantic validator | Shared namespace uniqueness outside Schema. |
| Preference.subject | §17.5; §17.7.1 | required SubjectRef | PARTIAL | required + $ref SubjectRef | resolver | Must resolve exactly one Subject. |
| Preference.category | §17.5; §15 | required Coding | PARTIAL | required + $ref Coding | terminology layer | Category vocabulary not frozen here. |
| Preference.value | §17.5; §8.4 | required PreferenceValue | PARTIAL | required + $ref PreferenceValue | semantic validator / terminology layer | Category/value compatibility is non-Schema. |
| Preference.temporal | §17.5 | optional TemporalExtent | PARTIAL | $ref TemporalExtent | semantic validator / canonicalizer | Omission means absent semantic time. |
| Preference.contexts | §17.5; §22.3.3 | optional Context[0..*] | PARTIAL | array/items $ref; no minItems:1 | semantic validator / canonicalizer | [] valid-but-noncanonical. |
| Preference.provenance | §17.5; §17.8 | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | semantic validator / canonicalizer | No uniqueItems. |
| Preference.annotations | §17.5 | optional Annotation[0..*] | PARTIAL | array/items $ref; no minItems:1 | canonicalizer | No uniqueItems. |
| Relation.source | §17.6–17.7; §22.14 | required CoreEntityRef | PARTIAL | required + $ref CoreEntityRef | resolver / Relation Vocabulary | Endpoint role/kind contract is non-Schema. |
| Relation.target | §17.6–17.7; §22.14 | required CoreEntityRef | PARTIAL | required + $ref CoreEntityRef | resolver / Relation Vocabulary | Endpoint role/kind contract is non-Schema. |
| Relation.type | §17.6; §14.6; §22.14 | required Coding | PARTIAL | required + $ref Coding | Relation Vocabulary / terminology layer | Directionality/inverse/causal status not Schema. |
| Relation.temporal | §17.6 | optional TemporalExtent | PARTIAL | $ref TemporalExtent | semantic validator / canonicalizer | Independent of endpoint ordering. |
| Relation.provenance | §17.6; §17.8 | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | semantic validator / canonicalizer | Endpoint provenance does not substitute. |
| Relation.annotations | §17.6; §17.9 | optional Annotation[0..*] | PARTIAL | array/items $ref; no minItems:1 | canonicalizer | Annotation difference is not identity. |
| Annotation.text | §17.9; §8.1 | required Text | SCHEMA | required + $ref Text | — | Structured semantics cannot be hidden here. |
| Annotation.provenance | §17.9 | required Provenance[1..*] | PARTIAL | required; array/items $ref; minItems:1 | semantic validator / canonicalizer | Own provenance; owner provenance cannot replace it. |
| Coding.system | §15; §22.6 | required nonblank semantic string | SCHEMA | required; type:string + nonblank pattern | terminology layer | Not required to be URI. |
| Coding.code | §15; §22.6 | required nonblank semantic string | SCHEMA | required; type:string + nonblank pattern | terminology layer | No invented code enum. |
| Coding.display | §15 | optional Text | SCHEMA | $ref Text | — | Does not change basic machine identity. |
| Coding.version | §15; §22.6 | optional nonblank semantic string | SCHEMA | type:string + nonblank pattern | terminology layer | Version is canonical information. |
| Confidence.value | §17.8.6 | required number | PARTIAL | required; type:number | semantic validator | If scale exists, sibling-dependent range check remains non-Schema. |
| Confidence.metric | §17.8.6; §22.6 | required nonblank semantic string | SCHEMA | required; type:string + nonblank pattern | — | No implicit probability meaning. |
| Confidence.scale | §17.8.6 | optional closed {min:number,max:number} | PARTIAL | object; required min,max; closure | semantic validator | min<max and value∈[min,max] are non-Schema. |
| SubjectRef.ref | §17.7.1 | required EntityId; exactly one Subject resolution | PARTIAL | required + $ref EntityId | resolver | Do not encode existence with pattern. |
| CoreEntityRef.ref | §17.7.2 | required EntityId; exactly one Behavior/Preference resolution | PARTIAL | required + $ref EntityId | resolver / Relation Vocabulary | Endpoint compatibility non-Schema. |
| ExternalActorRef.kind | §17.4.2 | required person\|device\|software\|other | SCHEMA | required + enum | — | Exact tokens. |
| ExternalActorRef.external_id | §17.4.2 | optional closed object with required system,value | SCHEMA | object/properties/required/closure | — | External namespace, not EntityId namespace. |
| ExternalActorRef.external_id.system | §17.4.2; §22.6 | required nonblank string | SCHEMA | type:string + nonblank pattern | — | No URI assumption. |
| ExternalActorRef.external_id.value | §17.4.2; §22.6 | required nonblank string | SCHEMA | type:string + nonblank pattern | — | External stable identifier. |
| ExternalActorRef.display | §17.4.2 | optional Text | SCHEMA | $ref Text | — | Text sameness does not establish actor identity. |
| ExternalActorRef.role | §17.4.2 | optional Text | SCHEMA | $ref Text | — | Role is descriptive. |
| Provenance.derivation | §17.8.1 | required direct\|inferred\|undetermined | SCHEMA | required + enum | semantic validator | Whether producer legitimately uses undetermined is semantic. |
| Provenance.source | §17.8.2 | optional SourceDescriptor, conditionally required for direct/undetermined | PARTIAL | $ref + if/then required | semantic validator | Undetermined traceability adds structural alternative plus semantic quality rule. |
| Provenance.generator | §17.8.2 | optional GeneratorDescriptor, required for inferred | PARTIAL | $ref + if/then required | semantic validator | Presence alone does not imply inferred. |
| Provenance.evidence | §17.8; §22.3.3 | optional Evidence[0..*]; [] noncanonical | PARTIAL | array/items $ref; no minItems by default | canonicalizer | Undetermined branch may require nonempty evidence as one traceability alternative. |
| Provenance.confidence | §17.8 | optional Confidence | PARTIAL | $ref Confidence | semantic validator | Not truth field. |
| SourceDescriptor.kind | §17.8.3 | required patient_self_report\|questionnaire\|clinician_documentation\|ehr_record\|device_observation\|legacy_record\|other | SCHEMA | required + enum | — | Exact frozen tokens. |
| SourceDescriptor.locator | §17.8.3; §22.6 | optional nonblank string | SCHEMA | type:string + nonblank pattern | — | Not Core reference. |
| SourceDescriptor.display | §17.8.3 | optional Text | SCHEMA | $ref Text | — | Human-readable only. |
| SourceDescriptor.times | §17.8.3; §22.3.3 | optional SourceTimeEvent[0..*] | PARTIAL | array/items $ref; no minItems:1 | canonicalizer | Order-insensitive semantics and duplicate normalization non-Schema. |
| SourceTimeEvent.role | §17.8.3 | required reported\|recorded\|observed | SCHEMA | required + enum | — | No generic time role. |
| SourceTimeEvent.at | §17.8.3 | required TemporalValue | PARTIAL | required + $ref TemporalValue | semantic validator | TemporalValue partial projection. |
| GeneratorDescriptor.kind | §17.8.4 | required human\|llm\|rule_engine\|analytic_model\|migration_process\|other | SCHEMA | required + enum | — | Generator presence does not imply inferred. |
| GeneratorDescriptor.identifier | §17.8.4; §22.6 | optional nonblank string | SCHEMA | type:string + nonblank pattern | — | Not EntityId. |
| GeneratorDescriptor.version | §17.8.4; §22.6 | optional nonblank string | SCHEMA | type:string + nonblank pattern | — | No product-version semantics added. |
| GeneratorDescriptor.display | §17.8.4 | optional Text | SCHEMA | $ref Text | — | Human-readable. |
| GeneratorDescriptor.times | §17.8.4; §22.3.3 | optional GeneratorTimeEvent[0..*] | PARTIAL | array/items $ref; no minItems:1 | canonicalizer | Order/equality non-Schema. |
| GeneratorTimeEvent.role | §17.8.4 | required extracted\|generated\|transformed\|migrated | SCHEMA | required + enum | — | Exact frozen tokens. |
| GeneratorTimeEvent.at | §17.8.4 | required TemporalValue | PARTIAL | required + $ref TemporalValue | semantic validator | TemporalValue partial projection. |
| Evidence.kind | §17.8.5 | required text_excerpt\|document_reference\|questionnaire_response\|device_observation\|legacy_material\|other | SCHEMA | required + enum | — | Exact frozen tokens. |
| Evidence.content | §17.8.5 | optional Text | SCHEMA | $ref Text | — | At least content or locator handled by object conditional. |
| Evidence.locator | §17.8.5; §22.6 | optional nonblank string | SCHEMA | type:string + nonblank pattern | — | At least content or locator. |
| Evidence.times | §17.8.5; §22.3.3 | optional SourceTimeEvent[0..*] | PARTIAL | array/items $ref; no minItems:1 | canonicalizer | [] valid-but-noncanonical. |
| Evidence.(content\|locator) | §17.8.5 | at least one present; both allowed | SCHEMA | anyOf required content / required locator | — | Use anyOf, not oneOf. |
| Instant.kind | §17.4.3; §22.4 | required const instant | SCHEMA | required + const | — | Mechanical discriminator. |
| Instant.at | §17.4.3 | required TemporalValue | PARTIAL | required + $ref TemporalValue | semantic validator | Calendar validity partial. |
| Instant.provenance | §17.4.3; §17.10 | optional Provenance[1..*] | PARTIAL | array/items $ref + minItems:1 if present | canonicalizer / semantic validator | Omission means inheritance. |
| Interval.kind | §17.4.3; §22.4 | required const interval | SCHEMA | required + const | — | Mechanical discriminator. |
| Interval.start | §17.4.3 | optional TemporalValue | PARTIAL | $ref TemporalValue | semantic validator | At least start/end separately enforced. |
| Interval.end | §17.4.3 | optional TemporalValue | PARTIAL | $ref TemporalValue | semantic validator | Conservative ordering non-Schema. |
| Interval.(start\|end) | §17.4.3 | at least one boundary present | SCHEMA | anyOf required start / required end | — | Both allowed. |
| Interval.provenance | §17.4.3; §17.10 | optional Provenance[1..*] | PARTIAL | array/items $ref + minItems:1 if present | canonicalizer / semantic validator | Omission means inheritance. |
| FrequencyPeriod.value | §8.3.2 | required positive integer >=1 | SCHEMA | required; type:integer; minimum:1 | — | No non-integer periods. |
| FrequencyPeriod.unit | §8.3.2 | required day\|week\|month\|year | SCHEMA | required + enum | — | No hour token. |
| ObservedCountFrequency.kind | §8.3.3 | required const observed_count | SCHEMA | required + const | — | — |
| ObservedCountFrequency.count | §8.3.3 | required integer >=0 | SCHEMA | required; type:integer; minimum:0 | — | 0 is valid. |
| ObservedCountFrequency.precision | §8.3.1, §8.3.3 | required exact\|approximate | SCHEMA | required + enum | — | Not confidence. |
| ObservedCountFrequency.window | §8.3.3 | optional Interval | PARTIAL | $ref Interval | semantic validator / canonicalizer | Not a rate denominator. |
| ObservedCountFrequency.provenance | §8.3; §17.10 | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | canonicalizer / semantic validator | Omission inherits. |
| RateFrequency.kind | §8.3.4 | required const rate | SCHEMA | required + const | — | — |
| RateFrequency.value | §8.3.4 | required number >=0 | SCHEMA | required; type:number; minimum:0 | — | JSON number, no fuzzy tolerance. |
| RateFrequency.period | §8.3.4 | required FrequencyPeriod | SCHEMA | required + $ref FrequencyPeriod | — | Must be explicit. |
| RateFrequency.precision | §8.3.1, §8.3.4 | required exact\|approximate | SCHEMA | required + enum | — | — |
| RateFrequency.provenance | §8.3; §17.10 | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | canonicalizer / semantic validator | Omission inherits. |
| RecurrenceFrequency.kind | §8.3.5 | required const recurrence | SCHEMA | required + const | — | — |
| RecurrenceFrequency.period | §8.3.5 | required FrequencyPeriod | SCHEMA | required + $ref FrequencyPeriod | — | Conditional exact 1 week when days_of_week present. |
| RecurrenceFrequency.precision | §8.3.1, §8.3.5 | required exact\|approximate | SCHEMA | required + enum | — | — |
| RecurrenceFrequency.times_per_period | §8.3.5 | optional integer >=1 | SCHEMA | type:integer; minimum:1 | — | Must be absent when days_of_week present. |
| RecurrenceFrequency.days_of_week | §8.3.5 | optional Weekday[1..*], duplicate token invalid | SCHEMA | array/items Weekday; minItems:1; uniqueItems:true | — | Safe uniqueItems case. |
| RecurrenceFrequency.day_part | §8.3.5 | optional morning\|afternoon\|evening\|night | SCHEMA | enum | — | No clock thresholds. |
| RecurrenceFrequency.provenance | §8.3; §17.10 | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | canonicalizer / semantic validator | Omission inherits. |
| QualitativeFrequency.kind | §8.3.6 | required const qualitative | SCHEMA | required + const | — | — |
| QualitativeFrequency.value | §8.3.6 | required never\|rarely\|occasionally\|sometimes\|often\|frequently\|usually\|intermittently\|always | SCHEMA | required + enum | — | No numeric ordering. |
| QualitativeFrequency.provenance | §8.3; §17.10 | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | canonicalizer / semantic validator | Scope semantics non-Schema. |
| CodedPreferenceValue.kind | §8.4.1 | required const coded | SCHEMA | required + const | — | — |
| CodedPreferenceValue.value | §8.4.1 | required Coding | PARTIAL | required + $ref Coding | terminology layer / semantic validator | Reliable binding non-Schema. |
| TextPreferenceValue.kind | §8.4.2 | required const text | SCHEMA | required + const | — | — |
| TextPreferenceValue.value | §8.4.2; §22.12 | required Text | PARTIAL | required + $ref Text | semantic validator / canonicalizer | Legitimate fallback cannot be decided structurally. |
| BooleanPreferenceValue.kind | §8.4.3 | required const boolean | SCHEMA | required + const | — | — |
| BooleanPreferenceValue.value | §8.4.3 | required boolean | PARTIAL | required; type:boolean | semantic validator | Category must actually support binary semantics. |
| NumericPreferenceValue.kind | §8.4.4 | required const number | SCHEMA | required + const | — | — |
| NumericPreferenceValue.operator | §8.4.4 | required eq\|lt\|lte\|gt\|gte | SCHEMA | required + enum | — | Preserves comparator. |
| NumericPreferenceValue.value | §8.4.4 | required number | SCHEMA | required; type:number | — | NaN/Infinity are not JSON numeric instances. |
| NumericPreferenceValue.unit | §8.4.4 | optional Coding; may be semantically required by source/category | PARTIAL | $ref Coding | semantic validator / terminology layer | Do not require universally or guess unit. |
| CodedContextValue.kind | §8.5.1 | required const coded | SCHEMA | required + const | — | — |
| CodedContextValue.value | §8.5.1 | required Coding | PARTIAL | required + $ref Coding | terminology layer / semantic validator | Reliable contextual coding non-Schema. |
| TextContextValue.kind | §8.5.1 | required const text | SCHEMA | required + const | — | — |
| TextContextValue.value | §8.5.1; §22.12 | required Text | PARTIAL | required + $ref Text | semantic validator / canonicalizer | Cannot hide frequency/temporal/factor/workflow semantics. |
| Context.value | §8.5 | required ContextValue | PARTIAL | required + $ref ContextValue | semantic validator / terminology layer | Context-vs-Factor classification non-Schema. |
| Context.provenance | §8.5; §17.10 | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | canonicalizer / semantic validator | Omission inherits. |
| CodedFactorValue.kind | §8.6.3 | required const coded | SCHEMA | required + const | — | — |
| CodedFactorValue.value | §8.6.3 | required Coding | PARTIAL | required + $ref Coding | terminology layer / semantic validator | Reliable factor coding non-Schema. |
| TextFactorValue.kind | §8.6.3 | required const text | SCHEMA | required + const | — | — |
| TextFactorValue.value | §8.6.3; §22.12 | required Text | PARTIAL | required + $ref Text | semantic validator / canonicalizer | Must not hide existing Core entity relationship. |
| BehaviorFactor.role | §8.6.1 | required reported_reason\|observed_association\|antecedent\|explanatory | SCHEMA | required + enum | — | Role is not derivation. |
| BehaviorFactor.factor | §8.6.3 | required FactorValue | PARTIAL | required + $ref FactorValue | semantic validator / terminology layer | Entity relationship may require Relation instead. |
| BehaviorFactor.direction | §8.6.2 | required factor_to_behavior\|behavior_to_factor\|unspecified; conditional role rule | SCHEMA | required + enum + if/then const for reported_reason/antecedent | — | Direction is not causality. |
| BehaviorFactor.provenance | §8.6; §17.10 | optional Provenance[1..*] | PARTIAL | minItems:1 if present + $ref | canonicalizer / semantic validator | Explanatory source-exceeding inference needs inferred effective provenance. |

## 5. Cardinality projection contract

| Frozen cardinality | Field presence | Empty collection | Schema projection | Canonical-normalization consequence |
|---|---|---|---|---|
| required scalar / object | REQUIRED | n/a | property in `required` | none |
| optional scalar / object | OPTIONAL | n/a | omit from `required`; property schema excludes null | omission means absent |
| required `0..*` | REQUIRED | valid | `required` + array/items; **no** `minItems:1` | root field remains present |
| optional `0..*` | OPTIONAL | semantic-valid but noncanonical | array/items; **no** `minItems:1` | canonicalizer omits empty field |
| required `1..*` | REQUIRED | invalid | `required` + `minItems:1` | none |
| optional `1..*` | OPTIONAL | invalid when present | if present array + `minItems:1` | omission may carry separate semantics (e.g. provenance inheritance) |

Important consequence: JSON Schema validation alone cannot label optional `0..*` `[]` as “valid but normalization-required.” It must accept it structurally; the canonicalizer owns the normal-form omission.

### 5.1 Root collections

- `subjects`: required, `minItems:1`.
- `behaviors`: required, may be `[]`.
- `preferences`: required, may be `[]`.
- `relations`: required, may be `[]`.

R2C **MUST NOT** add `minItems:1` to behaviors/preferences/relations.

## 6. Mechanical union projection

| Union | Variants | Projection |
|---|---|---|
| ActorRef | SubjectRef / ExternalActorRef | `oneOf`; concrete branches closed; `ref` vs `kind` required-property discrimination |
| TemporalExtent | Instant / Interval | `oneOf`; `kind:"instant"` / `kind:"interval"` via `const` |
| BehaviorFrequency | observed_count / rate / recurrence / qualitative | `oneOf`; `kind` const per branch |
| PreferenceValue | coded / text / boolean / number | `oneOf`; `kind` const per branch |
| ContextValue | coded / text | `oneOf`; `kind` const per branch |
| FactorValue | coded / text | `oneOf`; `kind` const per branch |

No new discriminator may be introduced for convenience.

## 7. Cross-cutting invariant projection matrix

This matrix contains **40 projection entries**.

Invariant counts:

- SCHEMA: **17**
- PARTIAL: **3**
- NOT_SCHEMA: **20**

| Invariant | Normative source | Frozen rule | Status | Schema mechanism | Non-Schema owner | Trap |
|---|---|---|---|---|---|---|
| Optional scalar/object absence | §22.3.1 | absence by omission; null invalid | SCHEMA | required controls presence; property schema excludes null | — | Never include null in type union. |
| Closed Core field sets | §22.2 | unknown fields invalid | SCHEMA | unevaluatedProperties:false at concrete object boundary; additionalProperties:false only when all allowed properties are declared in that same non-composed object schema | — | Composition via $ref/allOf/oneOf requires evaluation-aware closure. |
| Required 1 / optional 0..1 | §17 inventories | cardinality of scalar/object fields | SCHEMA | required + single property schema | — | Omitted optional is valid; null is not. |
| Required 0..* | §17.1 | behaviors/preferences/relations required but [] valid | SCHEMA | required + type:array + items; no minItems:1 | — | Do not upgrade [] to invalid. |
| Required 1..* | §17.1; §17.4–17.9 | subjects and assertion provenance collections non-empty | SCHEMA | required + array + minItems:1 | — | subjects/provenance differ from required 0..* roots. |
| Optional 0..* empty | §22.3.3; §22.10 | [] may be semantic-valid but normalization-required; normal form omits field | PARTIAL | Schema must accept [] (no minItems:1) | canonicalizer | Schema cannot distinguish valid-but-noncanonical from canonical-normal solely without changing validity. |
| Optional 1..* empty | §22.3.3 | present [] invalid | SCHEMA | minItems:1 when property present | — | Applies local provenance and days_of_week. |
| Root subjects non-empty | §17.1; §22.13 | subjects >=1 | SCHEMA | minItems:1 | — | Independent of shared-ID uniqueness. |
| Mechanical tagged unions | §22.4 | variant must be mechanically unique | SCHEMA | oneOf + const discriminator; ActorRef oneOf by required ref vs kind | — | Prefer oneOf because variants must be exclusive. |
| Text / semantic-string nonblank | §8.1; §22.6 | must contain at least one non-White_Space code point | SCHEMA | pattern with explicit Unicode White_Space exclusion | — | minLength alone is insufficient. |
| Temporal lexical + calendar validity | §8.2 | exact lexical families plus real Gregorian date | PARTIAL | oneOf/pattern for lexical profiles/component ranges | semantic validator | Do not claim format gives normative validation; default Draft 2020-12 format is annotation. |
| Collection semantic order-insensitivity | §17.2; §22.8; §22.11 | array position does not affect semantic equality | NOT_SCHEMA | none | canonicalizer / equality semantics | Schema validates sequences, not PBDL order-insensitive equality. |
| Full-equal duplicate normalization | §22.8; §22.10 | full canonical-information duplicate is normalization redundancy | NOT_SCHEMA | none globally | canonicalizer | uniqueItems uses JSON structural equality and would also turn normalization-required inputs into invalid inputs. |
| days_of_week duplicate token | §8.3.5 | duplicate weekday invalid | SCHEMA | uniqueItems:true because items are exact enum strings | — | This is a narrow safe use of uniqueItems. |
| Shared EntityId uniqueness | §5.3; §17.3; §22.13 | Subject/Behavior/Preference share one document-local namespace | NOT_SCHEMA | none in ordinary Draft 2020-12 | resolver / semantic validator | uniqueItems cannot enforce uniqueness by one property across heterogeneous arrays. |
| SubjectRef resolution | §17.7.1 | ref resolves exactly one Subject | NOT_SCHEMA | none | resolver | EntityId pattern is not existence/type validation. |
| CoreEntityRef resolution | §17.7.2 | ref resolves exactly one Behavior or Preference | NOT_SCHEMA | none | resolver | Relation endpoint type contracts add vocabulary semantics. |
| Identity vs canonical-information equality | §22.9.6 | same entity id != same canonical state | NOT_SCHEMA | none | semantic equality layer | Schema is not the PBDL equality engine. |
| PBDLDocument equality | §22.9.7 | order-insensitive full entity/Relation matching | NOT_SCHEMA | none | canonicalizer / equality semantics | Do not invent array sorting in Schema. |
| Text fallback dimension locality | §22.12 | text fallback cannot hide structured semantics from another dimension | NOT_SCHEMA | none | semantic validator / canonicalizer | No discriminator or regex can infer source meaning safely. |
| Relation object shape | §17.6; §22.14 | source,target,type shapes structurally fixed | SCHEMA | properties/required/$ref/closure | — | Shape validation is separate from relation vocabulary semantics. |
| Relation directionality | §14.6; §22.9.3 | directional vs symmetric comes from applicable type contract | NOT_SCHEMA | none | Relation Vocabulary + semantic validator | Never hard-code guessed directionality in generic Relation schema. |
| Symmetric swapped-endpoint equality | §22.9.3; §22.14 | A-B equals B-A for symmetric/non-directional type | NOT_SCHEMA | none | Relation Vocabulary + semantic validator | Schema cannot establish type-governed semantic equality. |
| Symmetric swapped-endpoint dedup | §22.8; §22.14 | dedup only after symmetry contract known and full equality holds | NOT_SCHEMA | none | Relation Vocabulary + canonicalizer | No lexicographic endpoint sorting. |
| Relation inverse conventions | §22.14 | inverse semantics belong to vocabulary | NOT_SCHEMA | none | Relation Vocabulary | No concrete inverse codes in R2C. |
| Concrete terminology validation | §15; §22.14 | Core Coding shape does not freeze concrete code membership | NOT_SCHEMA | none | terminology layer | Do not enum terminology codes absent a frozen profile. |
| Context vs BehaviorFactor classification | §8.5.2; §8.6; §22.13 | classification follows source-supported meaning | NOT_SCHEMA | none | semantic validator / canonicalizer | Do not add a new discriminator field. |
| Nested provenance present/non-empty | §17.10 | local provenance optional; if present 1..* | SCHEMA | array + minItems:1 | — | Structural presence is expressible. |
| Nested provenance inheritance/equality | §17.10.1–17.10.4 | omission inherits complete owner set; explicit equivalent set normalizes away | NOT_SCHEMA | none | canonicalizer / semantic validator | Schema cannot compare local set with owner set semantically. |
| Provenance derivation conditions | §17.8.1–17.8.2; §22.13 | direct=>source; inferred=>generator; undetermined=>source + locator or nonempty Evidence | PARTIAL | if/then/required + anyOf for structural traceability | semantic validator | Producer misuse of undetermined and provenance-quality warning are semantic, not Schema. |
| Evidence content-or-locator | §17.8.5 | at least one present | SCHEMA | anyOf required content\|required locator | — | Both may coexist. |
| Interval boundary presence | §17.4.3 | start or end at least one | SCHEMA | anyOf required start\|required end | — | Both may coexist. |
| Interval temporal ordering | §8.2.6; §22.13 | reject only when start definitely later than end under conservative comparability | NOT_SCHEMA | none | semantic validator | Do not approximate with lexical string ordering. |
| Confidence scale comparisons | §17.8.6; §22.13 | min<max and value in [min,max] | NOT_SCHEMA | no standard data-reference comparison | semantic validator | Do not hard-code a universal score range. |
| Recurrence weekday conditional | §8.3.5; §22.13 | days_of_week=>period exactly 1 week and times_per_period absent | SCHEMA | if required days_of_week then period const-shaped constraint + not(required times_per_period) | — | Keep days_of_week minItems:1 and uniqueItems:true. |
| BehaviorFactor role-direction conditional | §8.6.2; §22.13 | antecedent/reported_reason=>factor_to_behavior | SCHEMA | if role enum[...] then direction const | — | Does not assert causality. |
| Explanatory factor derivation | §8.6.1; §17.4.6; §22.13 | source-exceeding explanation must have effective inferred provenance | NOT_SCHEMA | none | semantic validator | Requires source/owner provenance semantics. |
| Dimensioned NumericPreference unit preservation | §8.4.4; §22.13 | if source/category requires dimension and source supplied unit, preserve unit | NOT_SCHEMA | none | semantic validator + terminology layer | Do not universally require unit or guess one. |
| Canonical field aliases | §17.12; §22.2 | legacy aliases cannot coexist in canonical Core | SCHEMA | closed object field sets | — | No special alias properties. |
| Deterministic byte-level JSON ordering | §22.11 | not frozen; future profile owns key/array ordering, number spelling, whitespace | NOT_SCHEMA | none | serialization profile | R2C must not design sorting/pretty-print rules. |

## 8. Non-Schema Responsibilities

| Responsibility | Owner | Required R2C behavior |
|---|---|---|
| reference resolution | resolver | Schema validates reference object shape only |
| shared EntityId namespace uniqueness | resolver / semantic validator | do not approximate with `uniqueItems` |
| semantic source-support interpretation | semantic validator / canonicalizer | no structural guessing |
| Context vs BehaviorFactor semantic classification | semantic validator / canonicalizer | no new discriminator |
| provenance semantic equality | semantic validator / canonicalizer | do not use JSON structural equality as substitute |
| provenance inheritance / override / redundant-local omission | canonicalizer | Schema only enforces present local provenance is non-empty |
| Relation directionality semantics | Relation Vocabulary + semantic validator | no generic direction hard-code |
| Relation concrete vocabulary | Relation Vocabulary | no invented enum of relation codes |
| Relation inverse rules | Relation Vocabulary | no inverse design in R2C |
| symmetric swapped-endpoint equality | Relation Vocabulary + semantic validator | no endpoint sorting |
| symmetric swapped-endpoint dedup | Relation Vocabulary + canonicalizer | no `uniqueItems` substitute |
| terminology validation / binding | terminology layer | Coding shape is not vocabulary membership |
| canonical duplicate removal | canonicalizer | keep normalization-required inputs structurally valid where frozen |
| canonical-information equality | semantic equality / canonicalizer | Schema is not an equality engine |
| Text fallback dimension interpretation | semantic validator / canonicalizer | no NLP-like inference in Schema |
| interval conservative temporal comparison | semantic validator | no lexical date ordering approximation |
| Confidence sibling numeric comparisons | semantic validator | no hard-coded scale |
| deterministic byte-level JSON ordering | future serialization profile | no key/array sorting or whitespace profile in R2C |

No new subsystem architecture is introduced by these owner labels; they reuse frozen architectural responsibilities.

## 9. Explicit no-approximation rules

The following are prohibited:

1. semantic duplicate prohibition → **do not** set all arrays to `uniqueItems:true`;
2. reference existence → **do not** pretend EntityId `pattern` proves resolution;
3. symmetric Relation → **do not** lexicographically sort source/target;
4. canonical omission of optional `0..*` empty arrays → **do not** make empty arrays structurally invalid;
5. terminology validation → **do not** invent enums for unfrozen codes;
6. Context vs BehaviorFactor → **do not** add a discriminator;
7. Relation directionality → **do not** hard-code guessed type behavior in generic Relation Schema;
8. order-insensitive PBDL equality → **do not** encode a sorting profile;
9. Confidence range semantics → **do not** assume all metrics use 0..1;
10. TemporalValue validity → **do not** rely on `format` alone or fabricate timezone / precision.

## 10. R2C1–R2C4 construction partition

The partition is dependency-driven and preserves the requested four-round architecture.

### R2C1 — Primitive + Reference Schema

- VersionToken
- EntityId
- Text
- TemporalValue
- Coding
- Confidence
- SubjectRef
- CoreEntityRef
- ExternalActorRef
- ActorRef

Rationale: these are leaf or near-leaf reusable definitions required by all later objects. SubjectRef/CoreEntityRef remain structurally projectable even though resolution stays outside Schema.

### R2C2 — Shared Structured Value Schema

- DerivationKind
- SourceKind
- SourceDescriptor
- SourceTimeEvent
- GeneratorKind
- GeneratorDescriptor
- GeneratorTimeEvent
- EvidenceKind
- Evidence
- Provenance
- Instant
- Interval
- TemporalExtent
- QuantitativeFrequencyPrecision
- FrequencyPeriod
- Weekday
- DayPart
- QualitativeFrequencyToken
- ObservedCountFrequency
- RateFrequency
- RecurrenceFrequency
- QualitativeFrequency
- BehaviorFrequency
- CodedPreferenceValue
- TextPreferenceValue
- BooleanPreferenceValue
- NumericPreferenceValue
- PreferenceValue
- CodedContextValue
- TextContextValue
- ContextValue
- Context
- FactorRole
- FactorDirection
- CodedFactorValue
- TextFactorValue
- FactorValue
- BehaviorFactor

Rationale: this round builds shared descriptors, provenance, temporal/frequency/value unions, Context and BehaviorFactor after R2C1 leaf/reference definitions exist.

### R2C3 — Core Entity Schema

- Subject
- Behavior
- Preference
- Relation
- Annotation

Rationale: core entity objects depend on R2C1 references/primitives and R2C2 shared structured values.

### R2C4 — PBDLDocument Root + Schema Conformance Corpus

- PBDLDocument

Rationale: root validation depends on all entity schemas. The conformance corpus belongs here so root cardinality, closure, valid/noncanonical boundaries and invalid structural cases can be tested without redesigning lower-level types.

## 11. Projection counts and acceptance summary

Named-type inventory: **54**
Field/constraint projection entries: **124**
Cross-cutting invariant entries: **40**
Total projection entries in this contract: **218**

Overall status counts:

- SCHEMA: **91**
- PARTIAL: **107**
- NOT_SCHEMA: **20**

Construction sets:

- R2C1: **10 types**
- R2C2: **38 types**
- R2C3: **5 types**
- R2C4: **1 type**

Audit conclusion:

- Normative contradiction found: **NO**
- Core semantics changed by this contract: **NO**
- Formal Schema modified by R2C0: **NO**
- Schema approximation of non-Schema semantics permitted: **NO**

## 12. R2C0 closure condition

This contract is sufficient for R2C1–R2C4 to implement Draft 2020-12 structure without making new PBDL language-design decisions. If a later Schema implementation appears to require a stronger rule than this contract permits, that is not permission to approximate; it must be routed to the frozen non-Schema owner or controller review.

**R2C0 SCHEMA PROJECTION CONTRACT → CLOSED → R2C1 READY**

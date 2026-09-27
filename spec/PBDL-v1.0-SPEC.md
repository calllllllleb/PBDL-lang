# PBDL 1.0 规范

**状态：** 草案
**目标版本：** PBDL 1.0
**当前设计阶段：** v0.1 语言基础

本文档是 PBDL 的唯一规范性来源。当本规范与示例、历史研究报告、设计理由文档或实现行为发生冲突时，以本规范为准。

## 1. 引言

PBDL（Patient Behavior Description Language，患者行为描述语言）是一门声明式领域专用语言，用于描述患者行为与偏好，以及解释这些行为与偏好所需的上下文、证据和关系信息。

PBDL 的职责是在上游信息产生系统与下游应用之间提供稳定、结构化的语义契约。PBDL 不用于替代自然语言理解，也不试图把完整的临床推理系统嵌入语言核心。

## 2. 范围

PBDL-Core 只负责描述与表示。

当前 PBDL-Core 的候选核心概念包括：

- Patient / Subject（患者 / 主体）
- Behavior（行为）
- Preference（偏好）
- Context（上下文）
- Provenance（来源追踪）
- Evidence（证据）
- Relation（关系）

在本轮重新设计中，Behavior 与 Preference 是主要研究对象。

Treatment Pathway（治疗路径）**不属于**初始重新设计中的 PBDL-Core。未来它可以作为扩展或上层应用概念进行讨论。

以下能力不属于 PBDL-Core：

- 临床诊断
- 临床推荐
- 风险预测
- 因果推断
- 知识库推理
- LLM 推理
- 治疗路径推荐
- 工作流执行

## 3. 术语与一致性关键词

本规范使用 **MUST**、**MUST NOT**、**SHOULD**、**SHOULD NOT** 和 **MAY** 作为规范性一致性关键词。

- **MUST**：绝对要求，符合规范的实现或文档必须满足。
- **MUST NOT**：绝对禁止，符合规范的实现或文档不得违反。
- **SHOULD**：强烈建议，仅在存在充分理由时可以偏离。
- **SHOULD NOT**：强烈不建议，仅在存在充分理由时可以采用。
- **MAY**：可选能力，可以实现，也可以不实现。

只有在相关语言构造已经被正式定义时，这些规范性要求才具有确定含义。任何标记为 `TODO` 的未决语法或字段名，都不得因为示例、占位文件或实现习惯而被视为已经标准化。

## 4. 设计原则

### 4.1 声明式表示

PBDL-Core **MUST** 用于描述信息，而不是规定执行行为。

### 4.2 来源陈述与派生结果分离

PBDL-Core **MUST** 区分来源直接描述的信息与外部系统推断、分析或计算得到的信息。

PBDL 表示“某个来源怎样描述、记录、观测或推断了某项 Behavior / Preference 信息”，但 PBDL-Core 本身 **MUST NOT** 因为信息被写入 PBDL 就宣称该信息在现实世界中已经被认证为绝对真实。

例如，患者自述“每天都按时服药”与设备或记录显示“过去一周存在漏服”可以同时被表示；PBDL-Core 不自动裁决哪一个来源正确。

除非被明确表示为外部派生工件或推断结果，否则 PBDL-Core **MUST NOT** 将以下内容伪装成来源直接描述的信息：

- 风险评分
- 推荐结果
- 冲突分析结果
- 模型生成的诊断
- 因果权重
- 推断得到的治疗决策

推理、推荐、预测与决策属于外部系统。

### 4.3 明确语义与可验证性

PBDL 的设计目标包括明确语义、机器可验证结构、持久化，以及上游抽取系统与下游应用之间的互操作。

### 4.4 保守的临床语义

PBDL-Core **MUST NOT** 仅通过字段命名或默认语言构造暗示未经验证的因果关系、治疗效果或临床结论。

## 5. PBDL 核心模型

R1B 冻结以下四类核心语义对象的最小边界：

- Subject：Behavior 与 Preference 所描述的主体，以及文档内主体引用的稳定锚点。
- Behavior：对某个 Subject 已描述或已断言的行为、未发生行为或行为状态的表示。
- Preference：对某个 Subject 已表达或已推断的倾向、选择、优先级、厌恶或偏好的表示。
- Relation：在允许的端点类型之间显式表达语义联系的 Core 构造。

Context 的最小语义职责已由 R1F 冻结：它用于对 Behavior / Preference 的语义解释提供情境性限定，但当前不作为具有独立 identity 的可引用一级 Core entity。R2A 冻结 Context 的 canonical ownership 为 Behavior / Preference 下的 embedded qualifier；其 concrete internal fields、cardinality details、JSON Schema 与 syntax 仍留待 R2B / 后续工作。Provenance 与 Evidence 的最小语义边界已由 R1C 冻结；R2A 在 §17 冻结 Provenance 的 field inventory、attachment pattern 与 Evidence 的 embedded ownership，具体 SourceDescriptor / Evidence leaf structure 仍留待 R2B。

### 5.1 文档与 Subject 绑定

一个 PBDL document **MUST** 至少包含一个 Subject。

一个 PBDL document **MAY** 包含多个 Subject。

每个 Behavior **MUST** 绑定到且仅绑定到一个 Subject。

每个 Preference **MUST** 绑定到且仅绑定到一个 Subject。

R1B 在此只冻结上述语义要求；R2A 已在 §17 冻结 canonical document / object field ownership，R2B1 进一步冻结 EntityId lexical contract 与 canonical reference object shape。DSL surface syntax 仍未冻结。即使未来 surface syntax 在单 Subject 文档中允许省略显式主体引用，canonical semantics 仍 **MUST** 能够确定该 Behavior 或 Preference 唯一对应的 Subject。

### 5.2 Core identity requirements

R1B 冻结以下最小 identity 要求：

| Core construct | v1 Core identity requirement | Reason |
|---|---|---|
| Subject | **MUST have identity** | Behavior 与 Preference 需要稳定绑定到明确主体 |
| Behavior | **MUST have identity** | Relation 以及历史 `associated_behavior` 兼容方向需要稳定引用 Behavior instance |
| Preference | **MUST have identity** | Relation 需要稳定引用 Preference instance |
| Relation | **No required identity in the v1 Core minimum** | R1B 不允许 Relation 作为 Relation endpoint，也没有已冻结的 Core 构造需要引用 Relation 本身 |

Relation 不要求 identity 并不禁止未来扩展为 Relation 提供标识符；这类能力不属于 R1B 的最小 Core requirement。

### 5.3 Identifier scope and stability

Subject、Behavior 与 Preference 的 entity identifier **MUST** 在其所属 PBDL document 内唯一。三类实体共享同一个 document-local identity namespace；同一个 identifier **MUST NOT** 在同一文档中被另一个 Subject、Behavior 或 Preference 重复使用。

v1 Core **MUST NOT** 强制要求全局 UUID、URI 或其他跨系统全局标识符。

在同一 PBDL document 的生命周期内，用于内部引用的 identifier **MUST** 保持足够稳定，以保证已建立的内部引用不会因为对象重排而改变指向。

数组位置、列表序号或其他仅由容器位置推导出的值 **MUST NOT** 作为规范性 entity identity。

跨文档 identity 与 cross-document reference protocol 不在 R1B 冻结，保留为未来工作。

### 5.4 Label is not identity

显示标签、类型名称、类别名称或术语代码本身 **MUST NOT** 自动充当 entity instance identity。

例如，`medication_nonadherence` 如果表示一个 Behavior type，则它描述的是“该 Behavior 属于什么类型”，而不是“这是哪个 Behavior instance”。

同样，`behavior_type`、`preference_category` 与 Relation type concept 都不是相应实体实例的 identity。

### 5.5 Reference model

Core reference **MUST** 在其声明的 reference scope 内解析到恰好一个实体。

在 v1 Core 最小模型中，内部 reference scope 为当前 PBDL document。

无法解析到任何实体的 reference 是无效的。

能够解析到多个实体的 ambiguous reference 是无效的。

Behavior 与 Preference 对 Subject 的绑定 **MUST** 使用可解析到明确 Subject identity 的引用语义，不得依赖模糊显示标签。

Relation 的 source endpoint 与 target endpoint **MUST** 使用 entity reference，不得使用未解析的自由文本标签作为规范性引用。

### 5.6 Relation endpoint matrix

R1B 对 PBDL-Core Relation 冻结以下最小端点集合：

| Source | Target | Core v1 |
|---|---|---|
| Behavior | Behavior | Allowed |
| Behavior | Preference | Allowed |
| Preference | Behavior | Allowed |
| Preference | Preference | Allowed |
| Subject | Behavior / Preference / Subject | Not allowed as a Core Relation endpoint in R1B |
| Relation | Any Core entity | Not allowed |
| Any Core entity | Relation | Not allowed |

Subject 的角色是 Behavior / Preference 的稳定归属锚点，而不是 R1B 中的通用关系图节点。若未来出现必须直接表达 Subject-level relation 的明确使用场景，可在后续设计轮次重新审议。

R1B 不允许 Relation→Relation，是为了避免在没有明确使用场景时提前引入高阶关系、关系注释图或 reification 语义。

R2B1 已在 §17 冻结 EntityId lexical profile 与 SubjectRef / CoreEntityRef / ActorRef 的 canonical reference representation。DSL syntax 与 JSON Schema 仍为 **TODO**。

### 5.7 Temporal semantics foundation

R1D 冻结 PBDL-Core 的最小 temporal semantics，用于回答：

- Behavior 在什么时候发生、持续或适用；
- Preference 在什么时候适用；
- Relation 在什么时候成立或适用。

R1D 区分两类不同的时间语义：

- **Semantic time**：描述 Behavior / Preference / Relation 本身发生、成立或适用的时间；
- **Provenance time**：描述相关信息何时被报告、记录、抽取、观测或生成。

Semantic time 与 Provenance time **MUST NOT** 被视为同一个时间概念。记录时间 **MUST NOT** 自动替代 Behavior / Preference / Relation 的 semantic time。

例如，患者在 9 月 20 日报告“上周漏服了三次药”时：

- “上周”属于 Behavior semantic time；
- “9 月 20 日”属于 provenance / reporting time。

Behavior、Preference 与 Relation **SHOULD** 基于同一套 Core temporal abstraction 表达 semantic temporal extent，但三者使用该 abstraction 的语义角色不同。

#### 5.7.1 Instant

Instant 表示一个时间点。

Instant 可以具有不同的来源精度，例如只精确到年、月、日，或更高精度的具体时刻。R1D 不冻结具体日期时间序列化格式。

#### 5.7.2 Interval

Interval 表示一个时间区间。

Interval 可以具有：

- start 与 end；
- 已知 start、未提供 end；
- 未提供 start、已知 end。

一个 Interval **MUST** 至少具有一个有效边界。两个边界都不存在时，该结构 **MUST NOT** 被解释为有意义的 temporal extent。

单边界 Interval 中缺失的 opposite boundary 只表示该边界 unspecified / not provided。

缺失的 boundary **MUST NOT** 自动解释为：

- 永久持续；
- 一直持续到现在；
- 一直持续到未来；
- 从无限过去开始；
- 数学意义上的 unbounded interval。

如果未来需要显式表达 ongoing、unbounded 或 known-open-ended temporal semantics，应由后续 temporal design 单独定义；R1D 不冻结这些语义。

如果 start 与 end 同时存在且能够比较，则 start **MUST NOT** 晚于 end。

#### 5.7.3 Unspecified semantic time

Behavior、Preference 或 Relation **MAY** 没有 semantic temporal information。

R1D 不要求引入显式的 UNKNOWN token；缺少 temporal information 可以表示 semantic time 未提供。

缺少 semantic temporal information **MUST NOT** 被解释为：

- 永久成立；
- 从出生至今；
- 当前仍成立；
- 始终如此；
- 反复发生；
- 时间不重要。

它只表示 canonical semantics 当前没有提供该项时间信息。

#### 5.7.4 Temporal precision preservation

对时间信息进行 canonicalization 或其他规范化转换时，转换结果 **MUST** 保留来源实际支持的时间精度，并 **MUST NOT** 发明来源未提供的精度。

例如，来源只有“2026-09”时，canonicalization **MUST NOT** 仅为了获得完整 timestamp 而将其伪造成“2026-09-01T00:00:00”。

同样，“2026 年” **MUST NOT** 被自动伪造成某一个具体日期。

具体 partial-date representation 与 ISO 8601 serialization 仍为 **TODO**。

#### 5.7.5 Timezone preservation

如果来源未提供 timezone / offset，canonicalization **MUST NOT** 凭空声明一个具体 timezone / offset。

如果来源已经提供 timezone / offset，canonical representation **MUST** 能够保留该来源提供的信息。

R1D 不冻结 timezone / offset 的具体 serialization。

#### 5.7.6 Relative time

Relative temporal expression 可以出现在来源中，例如：

- 昨天；
- 上周；
- 治疗后三天；
- 出院后一个月。

如果 relative temporal expression 保留在 canonical semantic representation 中，它 **MUST** 具有足以解释其含义的明确 anchor。

或者，在形成 canonical PBDL semantics 之前，上游转换已经将其解析为足够明确的 absolute / anchored temporal expression。

无法确定 anchor 的裸相对时间 **MUST NOT** 被假装成唯一确定的 absolute temporal extent。

R1D 不冻结 relative-time DSL syntax。

#### 5.7.7 Frequency / recurrence 与 temporal extent 是不同维度

R1G 冻结 Behavior frequency / recurrence 的最小语义边界。

Semantic temporal extent 回答“Behavior 在什么时候发生、持续或适用”；frequency / recurrence 回答“某类 Behavior occurrence 以什么重复模式或频度发生”。

二者 **MUST** 保持可区分，并 **MAY** 同时存在。

例如，“2026 年 1 月至 3 月，每周漏服两次”中：

- “2026 年 1 月至 3 月”属于 R1D semantic temporal extent；
- “每周漏服两次”属于 R1G Behavior frequency / recurrence information。

“持续三个月” **MUST NOT** 被解释为“每三个月一次”；“每天”也 **MUST NOT** 被当作一个 Interval。

R1G 不把 recurrence semantics 扩张到 Preference 或 Relation，也不冻结 RRULE、cron-like language、calendar engine 或具体 temporal / recurrence serialization。

### 5.8 Annotation semantics

R1I 冻结 lightweight human-readable Annotation semantics。

Annotation 用于为某个 canonical semantic object / assertion 提供人类可读的补充说明、澄清或解释性文本。它是 auxiliary human-readable information，而不是 canonical machine semantics 的唯一载体。

Annotation **MAY** 用于保留：

- 对 Behavior 的额外说明；
- 对 Preference 的人类可读补充；
- 来源中无法完全结构化、但值得保留的说明；
- 人工或外部系统产生的解释性备注。

R1I 当时不冻结 Annotation representation；R2A 已在 §17 冻结 Annotation 的最小 canonical field inventory、attachment ownership 与 cardinality。Text lexical constraints、author / generator representation、JSON Schema、serialization 与 DSL syntax 仍留待后续。

#### 5.8.1 Annotation is not a machine-semantics backdoor

如果某项信息对 identity、reference、Behavior type、Preference value、temporal semantics、frequency、Context、Relation type、relation direction、Provenance、DIRECT / INFERRED 或 causal / non-causal distinction 等 canonical machine semantics 具有规范性意义，conforming canonical representation **MUST NOT** 只把它藏在自由文本 Annotation 中。

如果某项语义已有 structured canonical mechanism，Annotation **MAY** 补充解释，但 **MUST NOT** 替代该 structured mechanism。

Conforming consumer **MUST NOT** 被迫通过自然语言理解 note / Annotation 才能确定对象的核心 machine semantics。

#### 5.8.2 Annotation does not create semantic assertions by itself

Annotation 文本自身 **MUST NOT** 自动创建新的 Behavior、Preference、Relation、Context、causal claim、risk result、recommendation 或其他 derived / application result。

例如 Behavior 已结构化为“患者漏服药物”，而 Annotation 写“可能因为工作压力较大”，该文本本身 **MUST NOT** 自动使 canonical semantics 获得 source-attributed reason、causal Relation、Context 或 derived clinical conclusion。

若 Annotation 中的内容需要成为 machine-consumable semantics，它必须通过已有适用的 structured semantic mechanism 表达，并遵守相应 provenance / derivation rules。

#### 5.8.3 Annotation derivation / provenance categories

R1I 至少区分以下 provenance / derivation 情况，但不冻结 surface enum：

1. **Source-described / source-carried text**：来源本身已经包含该说明；忠实保留或轻度规范化时，Annotation **MAY** 具有 DIRECT provenance semantics。
2. **Human-authored explanatory annotation**：人工标注者或审阅者额外增加的解释；它 **MUST** 与 source-described content 保持来源可区分，**MUST NOT** 冒充患者、临床人员或原始来源直接说过的话。
3. **Model / analytic explanatory annotation**：模型、规则或 analytic process 在来源未表达的基础上生成的新解释；该新增内容 **MUST** 保持 INFERRED derivation semantics，并 **MUST NOT** 标成 DIRECT source text。

是否使用 LLM / NLP 本身不决定 DIRECT / INFERRED。

如果来源明确写“因为恶心，患者停止服药”，LLM 仅忠实改写为“患者将恶心描述为停药原因”，且没有新增来源不存在的解释，该 Annotation **MAY** 继续属于 DIRECT / source-faithful representation。

如果 LLM 新增“可能因为患者对药物存在恐惧”，而来源未表达该解释，则新增部分属于 INFERRED。

#### 5.8.4 Annotation is not Provenance or Evidence

Annotation **MUST NOT** 替代 Behavior、Preference 或 Relation assertion 的 mandatory Provenance requirement。

“来源是谁”“如何产生”“DIRECT / INFERRED” **MUST NOT** 仅通过 note 文本表达并要求下游 NLP 猜测。

Annotation 与 Evidence 也不是同一概念：

- Evidence 回答“有什么材料支持 / 承载这项信息”；
- Annotation 回答“有什么人类可读的补充说明”。

将 source text 复制到 Annotation 中 **MUST NOT** 自动使该 Annotation 成为 normative Evidence object；Evidence material 也不自动成为 Annotation。

R1I 不设计 quote、source span、document offset 或 evidence excerpt schema。

#### 5.8.5 Annotation does not establish causality or Relation

Annotation 中出现 `because`、`due to`、因、导致、所以、可能因为等语言 **MUST NOT** 仅凭自由文本内容自动建立 canonical causal semantics。

Source-attributed reason 继续使用 R1E semantics；model-generated explanation 继续保持 INFERRED derivation when applicable。

同样，Annotation 文本 **MUST NOT** 自动创建 canonical Relation。

如果 Preference–Behavior association、Relation type、directionality 或 endpoints 需要 machine semantics，必须显式使用 R1H Relation mechanism，而不是只隐藏在 Annotation 中。

#### 5.8.6 Annotation does not replace temporal, frequency, or Context semantics

如果 Annotation 中的“最近”“上周”“经常”“每天”“工作时”等信息需要成为 canonical machine semantics，它们必须分别遵守 R1D temporal、R1G frequency / recurrence 与 R1F Context semantics。

Annotation **MUST NOT** 作为这些 structured semantics 的唯一规范性表达。

#### 5.8.7 Annotation does not create derived analysis or validator state

Annotation 中的“严重不依从”“未来风险很高”等文本 **MUST NOT** 自动使 PBDL-Core 获得 risk tag、clinical severity、adherence score、prediction 或 recommendation。

这些仍属于 source-described semantics 或 Core 外部 derived / application layer，具体取决于实际来源与结构化建模。

Annotation **MUST NOT** 用于重新引入 legacy `Behavior.validity_flag`，也 **MUST NOT** 替代 validation error、warning、schema violation 或其他 validator / report output。

#### 5.8.8 Annotation identity and graph boundary

Annotation 不要求独立 identity，不加入 Subject / Behavior / Preference document-local identity namespace，也不是 Relation endpoint。

R1I 不新增 Annotation→Annotation、Annotation→Relation、Relation→Annotation 或其他 Annotation graph edge。

Annotation 是附着于现有 canonical semantic object / assertion 的 lightweight auxiliary information，而不是新的 identity-bearing Core graph entity。

#### 5.8.9 Hidden chain-of-thought exclusion

PBDL-Core **MUST NOT** 要求模型暴露、存储或交换 hidden chain-of-thought、private reasoning trace、token-level reasoning、internal scratchpad 或 hidden model deliberation 作为规范性 Annotation 内容。

外部系统 **MAY** 提供 concise explanation、rationale summary 或 result-oriented annotation，但其 source / generator / derivation **MUST** 能与 source-carried text 保持可区分。

Legacy `reasoning_note` 中的 “reasoning” **MUST NOT** 被解释为 PBDL-Core 要求保存模型私有推理过程。

#### 5.8.10 Missing Annotation and structured-semantics precedence

Behavior / Preference **MAY** 没有 Annotation。

缺少 Annotation **MUST NOT** 被解释为没有 Context、没有 Provenance、没有 Evidence、没有解释、assertion 已完全理解或 assertion 不需要 provenance。

它只表示没有提供额外 human-readable annotation。

如果 Annotation 与 structured canonical semantics 冲突，conforming consumer **MUST NOT** 仅根据 Annotation 静默覆盖 structured semantics。

此类冲突需要由上游修正、validation / review 或其他明确机制处理；R1I 不设计 conflict resolver。

## 6. 词法结构

词法结构尚未冻结。

**TODO：**

- 字符集要求
- 空白符规则
- 注释规则
- 标识符
- 字面量
- 转义规则
- 保留字

除非在后续设计轮次中被明确冻结，否则任何 token、keyword、delimiter 或 literal 语法都不具有规范性。

## 7. 语法

R0 阶段的语法仍有意保持不完整。

当前语法占位文件位于 [`grammar/pbdl.ebnf`](grammar/pbdl.ebnf)。

**TODO：** 定义 Patient / Subject、Behavior、Preference、Context、Evidence / Provenance 与 Relation 的具体语法。

## 8. 类型系统

R2A 冻结 canonical object model 层面的最小结构类型、required / optional、cardinality、typed reference ownership 与 named nested semantic types。

R2B1 已冻结 VersionToken、EntityId、SubjectRef、CoreEntityRef、ActorRef、ExternalActorRef、DerivationKind、SourceDescriptor、GeneratorDescriptor、Evidence 与 reference representation 的 concrete canonical form。

仍为 **TODO** 的主要是：

- TemporalValue representation；
- PreferenceValue leaf type system；
- Context / BehaviorFrequency / BehaviorFactor concrete internal fields；
- Confidence concrete structure / metric model；
- Coding concrete JSON serialization；
- Text lexical constraints；
- 类型兼容与转换规则；
- JSON Schema 与 DSL syntax。

## 9. Patient / Subject

Subject 表示 Behavior 与 Preference 所描述的主体，并作为文档内主体引用的稳定锚点。

Subject **MUST NOT** 被设计成完整电子病历 Patient resource 的替代物。PBDL-Core 不负责保存完整：

- 姓名
- 地址
- 电话
- 完整人口学资料
- 完整医疗档案

这些信息若在某个外部系统中存在，可以由外部系统管理；PBDL Subject 的最小职责是为行为与偏好提供明确、稳定且可引用的主体身份。

每个 PBDL document **MUST** 至少包含一个 Subject，并 **MAY** 包含多个 Subject。

每个 Subject **MUST** 具有 document-local identity。

每个 Behavior 与 Preference **MUST** 能够解析到恰好一个 Subject。

R2A 在 §17 冻结 canonical Subject 仅包含 required id 字段；R2B1 在 §17.3 冻结 EntityId lexical contract。Subject 隐私表示、外部标识符绑定方式与 DSL surface syntax 仍为 **TODO**。

## 10. Behavior

Behavior 表示对某个 Subject 已描述或已断言的行为、未发生行为或行为状态。

它用于回答类似以下问题：

> 这个主体做了什么、没有做什么，或表现出了什么行为状态？

Behavior **MUST** 绑定到恰好一个 Subject，并 **MUST** 具有稳定的 document-local identity。

Behavior 本身不等价于：

- diagnosis
- risk result
- recommendation
- causal explanation
- Preference
- Pathway step

Behavior 的 identity 表示一个具体 Behavior instance，而不是其类型或显示标签。因此 Behavior type **MUST NOT** 自动充当 Behavior identity。

### 10.1 Legacy `executor` compatibility

历史 `Behavior.executor` 概念继续保留兼容价值。

Subject 与 Behavior executor / actor 不是同一个概念：

- Subject 表示“这条 Behavior / Preference 描述围绕谁”；
- executor / actor 表示“谁执行了该行为或参与了该动作”。

在最常见情况下，两者可以是同一人；但历史设计也可能需要表达 caregiver 等其他 actor。

R1B 不引入完整 Participant model，也不冻结 `executor` 的最终字段类型。后续设计 **MUST NOT** 仅因为 Behavior 已绑定 Subject 就无条件删除历史 executor 语义。

每个 canonical Behavior instance **MUST** 实际具有至少一条 provenance linkage，使其来源能够被追踪。仅仅“语言理论上支持 provenance”不足以满足该要求。

### 10.2 Behavior temporal semantics

Behavior **MAY** 具有 semantic temporal extent，用于描述该 Behavior semantic content 发生、持续或适用的时间范围。

历史 `Behavior.temporal_scope` 的时间表达能力继续保留，其规范方向是映射到共享 Core temporal abstraction，而不是冻结旧 string 表达。

Behavior 缺少 semantic time **MUST NOT** 被解释为永久行为、当前行为或反复行为；它只表示该 Behavior 的 semantic time 未指定。

### 10.3 Trigger / Symptom association semantics

R1E 保留历史 `Behavior.behavior_trigger` 与 `Behavior.symptom_triggered` 所表达的“原因 / 诱因 / 症状关联”能力，但不继承 legacy 名称中 `trigger` / `triggered` 的默认因果含义。

Legacy trigger / triggered naming **MUST NOT** 单独建立以下任一语义：

- A caused B；
- A clinically caused B；
- A is a verified causal factor of B。

字段名称本身 **MUST NOT** 被视为因果证据。

R1E 至少区分以下三类非等价语义情况。

#### 10.3.1 Source-attributed reason

当来源明确把某因素描述为 Behavior 的原因、理由或诱因时，canonical semantics **MAY** 保留“该来源把 X 归因为 / 描述为 Y 的原因或理由”这一 source-attributed reason。

例如患者明确说“因为头晕，我停药了”，可以表示“患者报告头晕是其停药理由”。

source-attributed reason **MUST NOT** 被 canonical semantics 自动等价为 verified causal relation。

如果来源本身明确表达该原因，而 LLM / NLP 只进行忠实 extraction、parsing、normalization 或 terminology mapping，没有新增来源未表达的解释，该结构化结果仍 **MAY** 具有 DIRECT provenance semantics。

Source attribution 的来源身份 **MUST** 能够通过 R1C Provenance 保持可追踪。

#### 10.3.2 Observed / recorded association or antecedent

如果来源只记录某因素与 Behavior 共现、在其之前出现、在相近 Context 中出现，或存在记录上的关联，但来源没有明确声称“这是 Behavior 的原因”，canonical semantics **MUST NOT** 自动把该信息升级为 source-attributed reason。

Observed / recorded association or antecedent **MUST NOT** 自动成为 causal claim。

特别地，temporal precedence 只说明时间顺序。A precedes B **MUST NOT** 自动推出 A caused B。

#### 10.3.3 Inferred explanation

如果来源本身没有明确表达原因，但 LLM、ML model、rule engine、analytic process 或其他推导过程根据输入生成“X 可能解释 / 导致 Y”之类的解释，该信息属于 INFERRED explanatory information。

INFERRED explanation **MUST NOT** 静默表示为 DIRECT source-attributed reason，也 **MUST NOT** 被伪装成 verified causal relation。

DIRECT / INFERRED 的判断继续遵守 R1C：依据 semantic content 是否相对于来源内容经过推导，而不是处理链路中是否出现 LLM / NLP / model / tool。

#### 10.3.4 Legacy `behavior_trigger` compatibility

历史 `Behavior.behavior_trigger` 的表达能力继续保留。

Canonical transformation **MUST NOT** 仅因为 legacy 字段名为 `behavior_trigger` 就赋予 causal semantics。

只有来源语义足够明确时，legacy value 才可以被解释为更具体的 source-attributed reason、observed antecedent、contextual association 或 inferred explanation 等语义类别。

如果 legacy value 的真实含义不清楚，canonical transformation **MUST NOT** 擅自升级为 reported / source-attributed reason 或 causal explanation。

R1E 不冻结这些未来类别的 surface names、具体字段或 enum。

#### 10.3.5 Legacy `symptom_triggered` compatibility and direction

历史 `Behavior.symptom_triggered` 的表达能力继续保留，但该 legacy 字段名本身存在方向歧义，例如：

- symptom → behavior；
- behavior → symptom；
- symptom 与 behavior 仅有关联而来源没有明确方向。

`symptom_triggered` 字段名 **MUST NOT** 单独决定 semantic direction。

如果 canonical semantics 表达 symptom-related direction，该 direction **MUST** 有来源内容支持。

如果来源不支持方向，canonicalization **MUST NOT** 发明方向。

Direction 与 causality 是两个不同维度：

- symptom precedes behavior **MUST NOT** 自动推出 symptom caused behavior；
- symptom follows behavior **MUST NOT** 自动推出 behavior caused symptom。

R1E 不新增 Symptom 一级 PBDL-Core entity，也不修改 R1B Relation endpoint matrix。Symptom-related information 的最终结构归属仍未冻结；它未来可以由 Behavior-local structured information、Context、external coded concept、extension 或其他结构承担。

R1E 不冻结新的 normative Relation vocabulary。`related_to`、`associated_with`、`reported_reason_for`、`precedes`、`follows` 等仍保持此前的非规范性候选状态，除非后续规范另行冻结。

R2A 在 §17 将 Behavior-local、非 Core-entity 的 trigger / symptom / reason association ownership 冻结到 Behavior.factors；若两端均为允许的 Core entities 且表达 explicit typed entity relationship，仍使用 Relation。BehaviorFactor concrete fields、symptom terminology、Relation type vocabulary 与 JSON / DSL syntax 仍为 **TODO**。

### 10.4 Legacy `communication_status` compatibility

历史 `Behavior.communication_status` 的表达能力继续保留，但单一 legacy 字段混合了多种不同语义。Canonical transformation **MUST NOT** 仅凭 `communication_status` 字段名决定其 canonical semantic category，也 **MUST NOT** 默认把这些语义继续压成一个通用 Behavior status。

R1F 至少区分以下四类情况。

#### 10.4.1 Actual communication Behavior

如果来源描述 Subject / actor 实际实施或没有实施某个沟通行为，例如：

- 患者告诉医生自己漏服了药；
- 患者给护士打电话报告副作用；
- 患者没有告诉医生自己已经停药；

这首先属于 observed / reported communication behavior，而不是单纯 workflow status。

只要该信息满足 Behavior 的既有语义边界，它 **MAY** 作为 Behavior semantic content 表达。

“患者告诉医生 X”与“X 被医生记录进 EHR”不是同一个概念；前者描述沟通行为，后者在表达信息来源、记录过程或进入系统的路径时属于 Provenance semantics。

R1F 不冻结 communication behavior 的具体 behavior type、actor、recipient 或 channel 字段。已有 `Behavior.executor` 继续遵守 R1B 的兼容边界；R1F 不新增 Participant 一级 Core entity。

#### 10.4.2 Contextual communication metadata

如果 legacy `communication_status` 的真实语义是限定另一个 Behavior / Preference 如何处于某种沟通情境，例如“该漏服行为已经向临床人员披露”或“该偏好尚未向家属沟通”，这类信息可以保留为 candidate contextual / communication qualification。

该类语义 **MUST** 与 actual communication Behavior、Provenance information、workflow / application state 保持可区分。

R1F 当时未冻结其最终 representation。R2A 在 §17 明确 canonical Behavior 不保留 communication_status 字段，并继续按 actual communication Behavior / Context / Provenance / workflow-application state 四路分流；Context / communication concrete vocabulary 仍未冻结。

#### 10.4.3 Communication-related Provenance

如果 legacy `communication_status` 实际想表达：

- 谁报告或记录了这条信息；
- 信息从哪个来源或渠道进入系统；
- 谁抽取、生成或记录了该信息；
- 信息何时被记录、抽取或生成；

这些语义属于 R1C Provenance，而不是 generic Context。

Canonical transformation **MUST NOT** 为了保留 legacy `communication_status` 而复制、覆盖或混淆已经属于 Provenance 的语义。

#### 10.4.4 Workflow / application state

如果 legacy `communication_status` 实际表示 `pending review`、`reviewed`、`acknowledged`、`escalated`、`assigned`、`notified`、`message sent`、`task completed`、`closed` 等软件或业务流程状态，这些信息默认属于 workflow / application layer。

PBDL-Core **MUST NOT** 默认把此类 workflow / application state 当作患者自身 Behavior 的 intrinsic semantic state。

历史能力可以由 future extension、application metadata 或外部 workflow system 继续承载；R1F 不设计该 extension。

#### 10.4.5 Communication does not certify truth

Information communicated **MUST NOT** 自动等价为 information verified。

同样，`acknowledged` **MUST NOT** 自动等价为 `agreed`、`verified` 或 `true`。

例如患者已经告诉医生“我每天都按时服药”，只说明发生过报告 / 沟通，不表示该内容已经被认证为现实真值。该边界继续遵守 R1C “PBDL records sourced information, not certified truth”。

如果来源同时包含沟通行为、其他 Behavior 和 source-attributed reason，canonical transformation **MUST NOT** 仅压缩成一个 `communication_status` 而丢失其余可区分语义；legacy migration **MUST** 以实际来源含义为准。

### 10.5 Behavior frequency / recurrence semantics

Behavior semantic content **MAY** 描述：

- 一个具体 occurrence；
- 一个 behavior state；
- 来源明确描述的 summarized / recurring behavior pattern。

Canonical semantics **MUST** 保留来源描述的是具体 occurrence、已观察 occurrence 汇总，还是 recurring / qualitative pattern。

Canonicalization **MUST NOT** 仅因为来源描述了 pattern，就自动展开出来源没有提供的 concrete observed occurrence timestamps；也 **MUST NOT** 仅因为存在若干独立 occurrence records，就自动把它们压缩为 recurring pattern。

#### 10.5.1 Observed / reported count within a reference window

来源可以描述一个 reference window 中实际观察或报告的 occurrence count，例如“过去 7 天漏服 3 次”。

这表示在该 reference window 中存在 count information。

Observed / reported count within a reference window **MUST NOT** 仅通过 canonicalization 自动变成 recurrence rule 或稳定 frequency pattern。

例如：

- “过去 7 天漏服 3 次” **MUST NOT** 自动等价为“每周固定漏服 3 次”；
- “漏服 3 次”在没有 reference period 时 **MUST NOT** 被转换为 `3/week`、`3/month` 或其他 rate。

Count、rate 与 recurrence pattern 是不同语义。R1G 不冻结具体 rate field。

#### 10.5.2 Recurring / periodic pattern

如果来源明确描述某项 Behavior 具有重复模式，例如“每天吸烟”“每周运动三次”“每天早晨测血压”，canonical semantics **MAY** 保留 recurring / periodic pattern。

Recurring pattern **MUST NOT** 被强制展开成未来或过去的 concrete observed occurrence timestamps。

“每天”描述的是 pattern，不表示来源已经观察或确认每一天都存在一个具体 occurrence。

如果多个独立 occurrence records 被外部 model / analytic process 总结为 recurring pattern，而来源本身没有表达该 pattern，则该 pattern 属于 INFERRED provenance semantics。

#### 10.5.3 Qualitative frequency

来源可以使用 `often`、`sometimes`、`rarely`、`frequently`、`occasionally`、`intermittently` 等 qualitative frequency / pattern information。

Canonicalization **MUST NOT** 仅为了数值化或规范化方便，把 qualitative frequency 擅自映射到来源未提供的具体阈值、概率、rate 或 recurrence interval。

例如：

- `often` **MUST NOT** 无来源依据地变成 `>= 5 times/week`、`70%` 或 `daily`；
- `intermittent` **MUST NOT** 自动变成 `every N hours` 或固定的 `N times/week`。

#### 10.5.4 Exact, approximate, and qualitative precision

Canonicalization **MUST** 在语义层面保留 frequency information 是 exact、approximate 还是 qualitative。

例如：

- “每周大约 3 次” **MUST NOT** 被转换为“exactly 3 times/week”；
- “几乎每天” **MUST NOT** 被转换为“exactly daily”；
- “偶尔” **MUST NOT** 被转换为来源未提供的固定 rate。

R1G 不冻结具体 approximation field。

#### 10.5.5 Expected / prescribed schedule is not actual Behavior frequency

Expected / prescribed schedule 与 actual patient Behavior frequency **MUST** 保持可区分。

例如，“医生要求每天服药两次”描述 prescribed / expected regimen，不表示患者实际每天服药两次。

Canonical semantics **MUST NOT** 仅根据 expected / prescribed schedule 自动生成 actual Behavior frequency。

反过来，actual Behavior frequency **MUST NOT** 自动被解释成 prescribed schedule。

即使同时知道 prescribed schedule 与 actual Behavior frequency，PBDL-Core **MUST NOT** 因此自动生成 adherence percentage、poor adherence、noncompliant 或其他 derived adherence judgment。

R1G 不设计 Prescription、Regimen 或 adherence analysis model。

#### 10.5.6 Denominator and rate boundary

当来源只提供 occurrence count 而没有 reference period 时，canonicalization **MUST NOT** 发明 frequency rate。

当来源缺少 expected opportunities / doses 或其他 denominator 时，canonicalization **MUST NOT** 发明 adherence ratio、adherence percentage、nonadherence rate 或其他比例。

例如“过去 7 天漏服 3 次”只直接支持 missed count 与 reference window；它本身不提供该期间应服药的总次数。

#### 10.5.7 Occurrence records do not automatically establish a pattern

若来源只提供多个 concrete occurrence records，canonical transformation **MUST NOT** 自动宣称存在 recurring pattern。

例如 Monday、Tuesday、Wednesday 各记录一次 exercise，不自动等价为“patient exercises daily”。

如果来源明确总结为 daily，则可以保留 source-described pattern；如果 pattern 是 model / rule / analytic process 根据 occurrences 推断所得，则该 pattern **MUST** 保留 INFERRED provenance semantics，并 **MUST NOT** 静默表示为 DIRECT source-described frequency。

如果 LLM / NLP 只忠实抽取来源已经明确表达的 frequency / recurrence，例如“我基本每天都会测血压”，结果仍 **MAY** 属于 DIRECT provenance semantics。

#### 10.5.8 Missing frequency and scope

Behavior **MAY** 没有 frequency / recurrence information。

缺少 frequency / recurrence information **MUST NOT** 被解释为：

- once；
- only once；
- non-recurring；
- irregular；
- continuous；
- daily；
- unknown but frequent。

它只表示 canonical semantics 没有提供 repetition / frequency information。

Frequency / recurrence **MUST NOT** 成为所有 Behavior 的强制属性。

`never`、`always` 等具有强 scope 含义的 frequency expressions **MUST NOT** 在缺少来源支持的 temporal / contextual scope 时被自动解释为 lifetime scope、从出生至今或未来永久成立。

#### 10.5.9 Duration, Context, reason, and Provenance boundaries

Duration / temporal extent 与 frequency **MUST** 保持可区分。

“持续 3 小时”描述 duration / temporal extent；“每 3 小时一次”描述 recurring interval / pattern。R1G 不设计完整 duration arithmetic。

Frequency / recurrence information 属于 Behavior semantic content 的限定，但它与 Context、source-attributed reason 和 Provenance 是不同维度。

例如“工作日经常忘记服药”可以同时包含 qualitative frequency 与 workday Context；若来源另说“因为工作忙所以忘记”，还包含 R1E source-attributed reason。Canonical semantics **MUST NOT** 把这些语义压成一个 frequency 字符串。

Frequency assertion 继续继承该 Behavior 的 R1C source traceability；“谁报告该 frequency”或“谁根据日志推断该 pattern”属于 Provenance，而不是 frequency value 本身。

R1G 不把 recurrence semantic contract 扩张到 Preference 或 Relation。若未来出现明确需求，应另行审议。

R2A 在 §17 冻结 Behavior.frequencies : BehaviorFrequency[0..*] 作为独立 structured qualifier ownership，并允许必要时具有 local provenance。BehaviorFrequency concrete fields、period representation、day-of-week / time-of-day structure、rate model、duration arithmetic、recurrence serialization、JSON Schema 与 DSL syntax 仍为 **TODO**。

### 10.6 Legacy `reasoning_note` compatibility

历史 `Behavior.reasoning_note` 的人类可读说明能力继续保留，但其 canonical semantic ownership 收敛到 R1I Annotation semantics。

Legacy `reasoning_note` **MUST NOT** 因字段名中的 “reasoning” 被解释为 PBDL-Core 自己执行并认证了正确推理、clinical reasoning、verified explanation 或 causal reasoning。

如果 legacy `reasoning_note` 忠实承载来源已经明确表达的说明，其 Annotation **MAY** 具有 DIRECT provenance semantics。

如果人工标注者、model、rule engine 或 analytic process 新增了来源未表达的解释，canonical representation **MUST** 保持其实际 human-authored 或 INFERRED derivation distinction；model-generated new explanation **MUST NOT** 冒充 DIRECT source text。

Legacy `reasoning_note` **MUST NOT** 替代 structured Behavior semantics、mandatory Provenance、Evidence、R1E reason / causality boundary 或 derived-result boundary。

R1I **MUST NOT** 被解释为要求保存模型 hidden chain-of-thought / private reasoning trace。

R1I 当时未冻结最终 representation。R2A 在 §17 冻结 legacy reasoning_note → Behavior.annotations，且 Annotation 采用 embedded lightweight structure；其更细的 serialization / author-generator representation 仍留待后续。

## 11. Preference

Preference 表示某个 Subject 对选项、属性、治疗特征或结果所表达或推断出的倾向、选择、优先级、厌恶或偏好。

Preference **MUST** 绑定到恰好一个 Subject，并 **MUST** 具有稳定的 document-local identity。

Preference 本身不等价于：

- observed Behavior
- clinical recommendation
- risk result
- conflict result
- objective constraint or barrier

现实信息中可能存在客观 constraint / barrier，但 R1B 不新增 Constraint 一级 Core entity。相关语义边界保留为未来设计问题。

Preference category 或显示标签 **MUST NOT** 自动充当 Preference identity。

### 11.1 Legacy `associated_behavior` compatibility

历史 `Preference.associated_behavior` 所表达的“偏好与行为之间存在关联”继续保留兼容价值，但 R1H 冻结其 canonical ownership。

在 canonical PBDL semantics 中，`Preference.associated_behavior` **MUST NOT** 继续作为与 Core Relation 平行的第二套 first-class association mechanism。

Legacy `Preference.associated_behavior` **MUST** canonicalize 为显式的 Preference–Behavior Relation。

因此，历史字段继续作为 legacy compatibility input concept 保留，但 canonical Preference 不再同时维护：

- dedicated `associated_behavior` link；
- 与其表达同一语义的 Relation。

如果旧输入使用自由文本 Behavior label 表达 `associated_behavior`，canonical transformation **MUST** 先将其解析到恰好一个 Behavior identity。

- 0 个匹配：unresolved / invalid；
- 多个匹配：ambiguous / invalid。

Canonical transformation **MUST NOT** 通过数组位置、最近文本、第一个匹配或 LLM 猜测静默选择一个 Behavior。

Legacy `associated_behavior` 本身只证明来源声明 Preference 与某个 Behavior 存在某种 association。它 **MUST NOT** 自动意味着 Preference caused Behavior、Behavior caused Preference、Preference resulted from Behavior、Preference conflicts with Behavior 或 Preference explains Behavior。

如果 legacy/source material 支持更具体的 relation meaning，canonical semantics **SHOULD** 保留来源支持的最具体语义；但 canonicalization **MUST NOT** 生成来源没有支持的更强 relation type。

R1H 不冻结该 Relation 的具体 normative type code 或 vocabulary token。

每个 canonical Preference instance **MUST** 实际具有至少一条 provenance linkage，使下游能够判断该 Preference 是直接表达还是外部推断所得。

直接表达与推断出的 Preference 可以具有相同的 preference category 与 preference value，但其 provenance semantics **MUST** 保持可区分，不得仅依赖自然语言 note 来判断。

### 11.2 Preference temporal semantics

Preference **MAY** 具有 semantic temporal extent，用于描述该 Preference 的适用时间范围。

Preference 的表达时间、记录时间、抽取时间或生成时间属于 Provenance time；这些时间 **MUST NOT** 自动替代 Preference 的 applicability time。

Preference 缺少 semantic temporal information **MUST NOT** 被解释为永久偏好。

不同时期的不同 Preference 信息可以作为不同 Preference instances 共存，例如某一时期拒绝注射、另一时期接受注射。

历史 Preference 正式字段表虽然没有独立 temporal 字段，但 v1 Core **MAY** 表达 Preference temporal applicability，以避免把可随时间变化的偏好误解为永久状态。

### 11.3 Legacy `note` compatibility

R1A 对 `Preference.note` 的 **KEEP_CORE** 结论保持不变。

其历史 human-readable descriptive annotation 能力继续保留，并在 canonical semantic ownership 上统一解释为 R1I Annotation semantics。

`Preference.note` **MUST NOT** 承担 `preference_category`、`preference_value` 或其他 structured Preference machine semantics 的唯一表达。

例如，仅有 `note = "不喜欢打针"` **MUST NOT** 被视为 canonical structured Preference semantic content 的替代品。

Preference Annotation **MUST NOT** 自动成为 Evidence 或 Provenance，也 **MUST NOT** 仅凭文本内容创建新的 Behavior、Preference、Relation、Context、causal claim 或 derived result。

R2A 在 §17 冻结 legacy Preference.note → Preference.annotations，并冻结 Annotation 的最小 text + provenance field inventory；更细的 serialization / author-generator representation 仍留待后续。

R2A 在 §17 冻结 Preference 的 canonical field inventory；R2B1 已冻结 SourceDescriptor / Evidence concrete structure。PreferenceValue leaf type system、偏好类型词表、Confidence concrete representation、Preference recurrence model 与语法仍为 **TODO**。

## 12. Context

R1F 冻结 Context 的最小语义职责。

Context 用于表达解释某个 Behavior / Preference 时，与其发生、成立或被理解相关的情境性背景或条件限定。它的职责是 **qualify semantic interpretation**，而不是证明原因、执行推理、记录来源或承载软件工作流。

概念上，Context 可以帮助表达类似“旅行期间发生漏服”“工作场景中避免用药”“存在家庭支持时愿意接受某方案”等情境，但这些只是说明性例子；R1F 不冻结具体 Context 类别、字段或 vocabulary。

### 12.1 Context is not a catch-all container

Context **MUST NOT** 被当作“无法分类的信息都放进 Context”的默认 catch-all container。

已经具有明确语义职责的信息 **MUST NOT** 仅为了结构便利而被重新解释为 generic Context：

- 信息从哪里来、如何产生，属于 R1C Provenance；
- Behavior / Preference / Relation 何时发生、成立或适用，属于 R1D semantic temporal semantics；
- source-attributed reason、observed antecedent 与 inferred explanation 继续遵守 R1E trigger / reason boundary；
- risk、conflict、recommendation、score、causal inference 等 derived analysis 属于 Core 外部的 derived / application result；
- `pending review`、`assigned`、`escalated`、`resolved`、system acknowledgment、notification state 等默认属于 workflow / application layer。

Context **MUST NOT** 作为绕过既有 Provenance、temporal、trigger / reason 或 derived-analysis 边界的替代容器。

### 12.2 Context does not establish causality

某因素被表示为 Context **MUST NOT** 自动表示该因素 caused Behavior、caused Preference 或 clinically explains an outcome。

例如，Behavior 发生在 traveling context 中，只说明该 Behavior 具有 traveling contextual qualification；它 **MUST NOT** 自动推出 traveling caused the Behavior。

如果来源明确表达“因为旅行忘记服药”，该 reason attribution 继续遵守 R1E，而不是仅靠 Context 获得 reason / causal semantics。

同样，Context **MUST NOT** 仅因为某因素影响或限制行为，就自动把它定义为 objective Constraint / Barrier。Constraint / Barrier model 仍为 future work。

### 12.3 Missing Context

Behavior / Preference **MAY** 没有显式 Context information。

缺少 Context **MUST NOT** 被解释为：

- context-free；
- universally applicable；
- unconditional；
- 在任何环境都成立。

它只表示 canonical semantics 当前没有提供额外 contextual qualification。

### 12.4 Context identity and reference boundary

R1F 不要求 Context 具有独立 identity。

Context 不加入 Subject / Behavior / Preference 的 document-local identity namespace，也不成为当前 Relation endpoint。

R1B identity / reference rules 与 Relation endpoint matrix 保持不变。

如果未来出现 shared context、context reuse 或稳定 context reference 等真实需求，可以在后续设计轮次重新审议 identity / reference model；R1F 不冻结这些机制。

Context 的 concrete fields、cardinality、nesting、identity / reuse mechanics、JSON Schema 与 DSL syntax 仍为 **TODO**。

## 13. Evidence 与 Provenance

R1C 冻结 Provenance 与 Evidence 的最小语义边界。

### 13.1 Provenance

Provenance 回答：

> “这条 Behavior / Preference / Relation assertion 是怎么来的？”

Provenance 描述信息或 semantic assertion 的来源与产生路径。其语义 **MUST** 足以让下游判断该信息来自什么来源或产生方式，并能够区分来源直接描述的信息与外部推断得到的信息。

概念上，Provenance 可以涉及：

- 来源类型；
- 来源身份或外部引用；
- 产生方式；
- 记录、抽取或生成该信息的主体 / 系统；
- 在必要时用于来源解释的时间信息；
- 该信息是否经过推断。

以上是语义职责，不是 R1C 冻结的字段列表或 Schema。

每个 canonical Behavior **MUST** 至少具有一条 provenance linkage。

每个 canonical Preference **MUST** 至少具有一条 provenance linkage。

每个 canonical Relation assertion **MUST** 至少具有一条 provenance linkage 或等价的可追踪 provenance semantics。

Relation assertion 的 provenance **MUST NOT** 被 source endpoint 或 target endpoint 的 provenance 自动替代。Relation provenance 的详细规则见 §14.7。

同一个 Behavior、Preference 或 Relation assertion **MAY** 具有多条 provenance linkage。

多条 provenance **MUST NOT** 被解释为该信息自动“更真实”或自动具有更高可信度。PBDL-Core 不负责 evidence weighting、source ranking 或真值裁决。

### 13.2 Evidence

Evidence 回答：

> “有什么材料支持、承载或记录了这条信息？”

Evidence 可以是支撑某项 Behavior / Preference 表示的材料或外部引用，例如：

- EHR 文本片段；
- 问卷回答；
- 访谈记录；
- 设备观测；
- 外部文档引用。

Evidence 与 Provenance 相关但不同。

Provenance 说明“信息如何产生以及从哪里来”；Evidence 说明“有哪些材料支持或承载该信息”。

Evidence **MAY** 作为 Provenance 指向或关联的支持材料，但二者 **MUST NOT** 被视为完全同义的概念。

R2A 在 §17 冻结 Evidence 为 optional Provenance.evidence embedded collection，且不要求 Evidence identity；R2B1 在 §17.8.5 冻结 Evidence concrete fields 与 locator/content representation。

### 13.2.1 Provenance time boundary

Provenance-related time 可以涉及报告、记录、观测、抽取或生成等不同 event roles。

这类 Provenance time **MUST NOT** 自动承担 Behavior / Preference / Relation 的 semantic temporal extent。

同一条信息的 semantic time 与 provenance time 可以不同，也可以只提供其中之一。

R2A canonical Provenance **不提供** 无角色的 generic top-level `time` field，因为单一 TemporalValue 无法在 source 与 generator 共存时无歧义地区分 reporting / recording / observation time 与 extraction / generation time。

R2B1 在 §17.8.3 / §17.8.5 冻结 source / reporting / recording / observation related time 的 concrete ownership：使用 role-explicit SourceTimeEvent，并由 SourceDescriptor 或具体 Evidence item 承载。

R2B1 在 §17.8.4 冻结 extraction / generation related time 的 concrete ownership：使用 GeneratorDescriptor 下的 role-explicit GeneratorTimeEvent。

如果未来需要 provenance-level event timeline，应采用具有 explicit role semantics 的结构，而 **MUST NOT** 重新引入无角色 generic provenance time。

### 13.3 DIRECT 与 INFERRED

R1C 冻结至少两类必须可区分的 provenance semantics。具体 surface enum 名称本轮不冻结。

DIRECT / INFERRED 判断的是**结构化 semantic content 相对于来源内容的产生方式**，而不是处理链路中是否使用了某种模型或工具。

使用 LLM、NLP 或其他工具进行 extraction、parsing、normalization、terminology mapping 或 serialization transformation，本身 **MUST NOT** 自动使该信息成为 INFERRED。

如果结构化语义忠实表示来源中已经明确报告、记录或观测到的内容，即使抽取或标准化过程由 LLM / NLP 完成，该信息仍 **MAY** 属于 DIRECT。

只有当结构化 semantic content 超出来源直接表达、记录或观测的内容，并由模型、规则、分析过程或其他推导过程生成时，该信息才属于 INFERRED provenance semantics。

#### DIRECT

DIRECT 表示信息直接来自某个来源的报告、记录或观测，例如概念上的：

- patient self-report；
- survey response；
- clinician documentation；
- device observation；
- manual entry。

DIRECT **MUST NOT** 被解释为“已经证明绝对真实”。它只表示 PBDL 没有把该项语义标记为由外部推理过程生成的结论。

#### INFERRED

INFERRED 表示信息由 LLM、ML model、rule engine、analytic process 或其他 inference process 根据其他输入推断产生。

INFERRED information **MUST NOT** 静默表示成 DIRECT 或来源直接描述的信息。

canonical semantic representation **MUST** 使下游能够区分 DIRECT 与 INFERRED provenance semantics，而不能仅通过自由文本 note 猜测。

对于 Preference：

- 来源明确表达“我不想每天打针”，LLM 仅将其结构化抽取为 injection aversion 时，仍可属于 DIRECT / expressed Preference；
- 来源没有明确表达该偏好，而模型根据多项行为记录推断“患者可能偏好低治疗负担方案”时，属于 INFERRED Preference。

即使两者最终具有相同的 preference category 或 preference value，其 provenance semantics 仍 **MUST** 可区分。

### 13.4 冲突来源与多来源

如果多个来源支持的是同一项结构化语义，一个 Behavior / Preference **MAY** 关联多条 provenance。

如果不同来源表达的 semantic content 实质不同或相互冲突，canonical representation **MUST NOT** 通过 provenance 合并、对象折叠或其他方式丢失、掩盖或使这些冲突语义不可区分。

默认情况下，这些冲突内容 **SHOULD** 保持为不同的 Behavior / Preference instances；未来若采用其他表示方式，也必须保持各项冲突语义可区分。

例如：

- 患者自述规律服药；
- 设备或记录显示存在漏服；

二者可以并存，但不应因为主体相同就被静默压缩成一个单一 Behavior 并仅附加两个 provenance source。

PBDL-Core 不负责自动裁决冲突，不在 R1C 设计 ConflictAnalysis。

### 13.5 Legacy source compatibility

历史 `Behavior.evidence_source` 的来源追踪能力继续保留，但其规范性方向是映射到统一的 Provenance / Source 语义，而不是把单一 string 字段冻结为最终模型。

历史 `Preference.source_type` 同样收敛到统一的 Provenance / Source 语义。

Behavior 与 Preference **SHOULD NOT** 长期维护两套彼此独立、语义重复的来源机制。

R1C 不删除 `evidence_source` 或 `source_type` 的历史兼容意义。R2A 在 §17 冻结其 canonical ownership 统一进入 Provenance，而不继续保留 legacy surface fields。

### 13.6 Confidence boundary

confidence **MUST NOT** 成为所有 Preference 的强制属性。

DIRECT self-report **MUST NOT** 被迫赋予模型式 confidence。

如果未来 confidence 用于 INFERRED information，其语义 **MUST** 能够说明：

- confidence 由谁或什么系统生成；
- confidence 衡量什么；
- confidence 对应哪个 inference process / model / analytic process。

R2A 在 §17 冻结 canonical confidence ownership 为 optional Provenance.confidence；Confidence 的数值范围、metric、算法、校准方式、serialization 与 validation 仍未冻结。

历史 `Preference.confidence_score` 因此继续保留为待细化概念，但不得被解释为所有 Preference 的必需 Core 属性。

### 13.7 Provenance identity

Provenance 自身仍 **不要求** 独立的 document-local identity。

当前 mandatory provenance-bearing canonical semantic assertions 至少包括：

- Behavior；
- Preference；
- Relation assertion。

R1H 新增 Relation assertion provenance requirement **MUST NOT** 被解释为 Provenance 因此必须具有 identity，也 **MUST NOT** 被解释为 Relation 因此必须具有 identity。

当前仍没有 Core 场景要求其他实体通过稳定 Core reference 指向某个 Provenance instance。

R2A 在 §17 冻结 Provenance 的最小 field inventory 与 embedded attachment pattern；R2B1 已冻结 SourceDescriptor / GeneratorDescriptor / Evidence 与 nested provenance equality/inheritance 的 concrete representation。Shared provenance identity、provenance chaining、Confidence concrete semantics、JSON Schema 与 DSL serialization 仍为 **TODO**。

## 14. Relations

Relation 用于在两个允许作为 Relation endpoint 的 PBDL semantic entities 之间显式表达语义联系。

R1B 冻结 Relation 的最小语义组成：

- source endpoint
- target endpoint
- relation type concept

R1H 在此冻结抽象语义要求；R2A 在 §17 进一步冻结 canonical Relation field names source / target / type / temporal / provenance / annotations；R2B1 已冻结 CoreEntityRef concrete reference shape。JSON Schema 与 DSL syntax 仍未冻结。

Relation source 与 target **MUST** 是 entity references，并 **MUST** 分别解析到恰好一个允许的 endpoint entity。

未定义 reference 是无效的。

ambiguous reference 是无效的。

自由文本 label **MUST NOT** 直接充当规范性 Relation endpoint reference。历史 string label 可以作为 legacy input，但在形成规范化语义前 **MUST** 被解析到明确 entity identity。

### 14.1 Allowed Core endpoints

PBDL-Core Relation 在 R1B 中允许：

- Behavior → Behavior
- Behavior → Preference
- Preference → Behavior
- Preference → Preference

R1B 不允许 Subject 作为 Core Relation endpoint。

R1B 不允许 Relation 作为 source 或 target，因此不支持 Relation→Relation 或 entity→Relation。

### 14.2 Relation temporal semantics

Relation **MAY** 具有 semantic temporal extent，用于描述该 Relation 本身成立或适用的时间范围。

历史 `Relation.temporal` 的时间能力继续保留，其规范方向是映射到共享 Core temporal abstraction，而不是冻结旧 string 表达。

Relation temporal metadata 与 Relation type semantics 是不同维度。

Relation temporal metadata **MUST NOT** 自动被解释为 `precedes`、`follows`、before、after 或其他 ordering relation。

如果未来 Relation vocabulary 定义 `precedes`、`follows` 等类型，其先后语义属于 Relation type 本身，而不是 temporal metadata 的隐式解释。

对于历史 `Relation.temporal` 中混合了“适用时间”和“关系先后类型”的数据，canonical transformation **MUST NOT** 在未区分真实含义时直接把旧值视为单一 temporal extent。

### 14.3 Relation identity

Relation 在 v1 Core 最小模型中**不要求自身具有 identity**。

这是因为当前没有已冻结的 Core reference 需要指向 Relation 本身，且 Relation 也不是允许的 Relation endpoint。

未来若 Evidence / Provenance、extension 或其他明确使用场景需要稳定引用 Relation，可在后续设计轮次增加 relation identity requirement；R1B 不提前冻结。

### 14.4 Relation type is not causality by default

Relation type concept 用于说明 source 与 target 之间“是什么关系”，但 Relation type **MUST NOT** 因其名称或存在本身就被解释为因果关系。

PBDL-Core 当前不将 `causal_effect` 定义为默认关系，也不把未经证据支持的因果权重作为 Core 的默认能力。

Relation semantic temporal extent 与 Relation type ordering semantics 相互独立的边界已由 R1D 冻结。

仍为 **TODO** 的是：

- TemporalValue lexical / precision / timezone details 与 temporal serialization；
- normative relation vocabulary 与 concrete relation type codes；
- inverse relation conventions；
- derived relation-strength artifact structure；
- relation vocabulary serialization；
- syntax。

### 14.5 Explicit Relation boundary

Relation 表示两个允许 endpoint 之间由 canonical semantics **显式声明**的 typed semantic link。

仅仅因为两个实体：

- 属于同一 Subject；
- 同时出现或时间相近；
- 具有相同 Context；
- 出现在同一 Evidence / source material；
- 出现在同一句话或相邻字段；
- 使用相同 terminology code / category；

canonicalization **MUST NOT** 自动创建 Relation。

如果上游 model、rule engine 或 analytic process 基于这些信息推断存在 Relation，该 Relation 是 INFERRED relation assertion，并继续遵守 R1C provenance / derivation boundary。

### 14.6 Relation type semantic contract and directionality

每个 canonical Relation **MUST** 使用具有稳定、机器可解释语义定义的 relation type。

Relation type 定义 source / target 在该关系中的 semantic roles，并 **MUST** 使 conforming implementation 能够判断该关系的 directionality semantics，例如 directional 或 symmetric / non-directional。

每个 normative relation type definition **MUST** 明确其允许的 endpoint semantic roles / endpoint kinds。具体 relation type 可以比 R1B global endpoint matrix 更严格，但 **MUST NOT** 扩大 R1B global endpoint matrix 所允许的 Core endpoint combinations。

每个 normative relation type definition **MUST** 明确其 causal semantic status：它要么明确承载 causal semantics，要么明确属于 non-causal semantics。

如果 relation type definition 没有明确赋予 causal semantics，canonical consumer **MUST NOT** 根据 type name、directionality、endpoint order 或其他隐式线索把它解释为 causal relation。

Relation type **MUST NOT** 只是一段自由文本说明、显示标签或 UI 文案。

A conforming canonical Relation **MUST** 使用其语义由适用 PBDL vocabulary / terminology binding 定义的 relation type。Undefined 或 free-text-only relation type semantics **MUST NOT** 被当作规范性 machine semantics。

R1H 不冻结 complete relation vocabulary、concrete code、serialization 或 open-vs-closed vocabulary policy，也不新增任何 concrete causal relation type。R2A 在 §17 冻结 Relation 的 canonical structural field names，但不冻结 normative relation vocabulary。

对于 directional relation type，交换 source / target 会改变或破坏该 relation type 所定义的语义。

对于 symmetric / non-directional relation type，交换 endpoint ordering **MUST NOT** 被解释为一个不同的 semantic relation meaning。

Canonicalization **MUST NOT** 在不知道 relation type directionality semantics 时自行猜测、反转或重排 endpoint。

Source → target 的 endpoint ordering 本身 **MUST NOT** 自动建立 causality、temporal precedence、influence、priority、evidence-for 或 parent/child semantics；这些只能由 relation type definition 明确规定。

Directional Relation **MUST NOT** 因其 directionality 自动等价为 causal Relation。

### 14.7 Relation assertion Provenance

每个 canonical Relation assertion **MUST** 具有至少一条 provenance linkage 或等价的可追踪 provenance semantics。

Relation assertion 的 provenance **MUST NOT** 被 source endpoint 或 target endpoint 的 provenance 自动替代。

Endpoint assertions 与 relation assertion 是不同语义陈述。例如：

- Behavior A 可以来自 device observation；
- Preference B 可以来自 patient self-report；
- A 与 B 之间的 relation 可以由 model 推断。

此时两个 endpoint 可以分别具有 DIRECT provenance，而 Relation assertion 本身仍属于 INFERRED。

Relation assertion 的 DIRECT / INFERRED 判定继续遵守 R1C：依据 relation semantic content 是否相对于来源内容经过推导，而不是处理链路中是否使用了 LLM / NLP / tool。

如果来源明确表达某 Relation，而 LLM / NLP 只忠实抽取该关系且没有新增语义推断，该 Relation assertion **MAY** 是 DIRECT / source-described。

如果 Relation 来自 model、rule engine、statistical process 或其他 analytic inference，它 **MUST** 保持 INFERRED provenance semantics，并 **MUST NOT** 静默表示为 DIRECT source-described Relation。

如果 Relation 表达 source-attributed reason，它仍继续遵守 R1E：source-attributed reason 不等价于 verified causality。

同一个 Relation semantic assertion **MAY** 具有多条 provenance linkage，但更多 provenance **MUST NOT** 自动意味着 Relation 更真实、更强或更 causal。

### 14.8 Distinct Relation assertions and deduplication

相同 endpoint pair 不代表相同 Relation assertion。

不同的：

- relation type；
- direction；
- temporal applicability；
- DIRECT / INFERRED derivation semantics；
- provenance-supported meaning；

都可以使 Relation assertions 在语义上不同。

Semantically distinct Relation assertions **MUST** 保持可区分，canonicalization **MUST NOT** 仅因为 source / target 相同就静默合并。

Canonicalization **MAY** 合并真正语义等价、endpoint 相同、type 相同、direction 相同、temporal applicability 相同，且合并不会丢失 provenance distinction 或 derivation distinction 的重复 Relation assertion。

R1H 不冻结具体 deduplication algorithm。

### 14.9 Relation identity remains unchanged

R1H 不改变 R1B identity decision：Relation 在当前 v1 Core minimum 中仍然 **不要求自身具有 identity**。

新增 Relation provenance requirement **MUST NOT** 被解释为 Relation 因此获得 required identity。

Relation 继续 **MUST NOT** 作为 Relation endpoint，R1B endpoint matrix 保持不变。

### 14.10 Relation temporal independence

Relation semantic temporal extent 继续表示 Relation 本身何时成立或适用。

Temporal extent、relation type 与 directionality 是三个不同维度。

存在 temporal metadata **MUST NOT** 自动把 relation type 推断为 `precedes` / `follows`；relation type 是 directional 也 **MUST NOT** 自动生成 temporal ordering semantics。

### 14.11 Relation weight remains derived

历史 `Relation.weight` 的 R1A disposition 保持为 **MOVE_DERIVED**。

`Relation.weight` **MUST NOT** 重新成为默认 PBDL-Core Relation intrinsic semantic strength。

旧 `weight` 可能代表 correlation coefficient、model score、ranking weight、confidence-like value、association strength、causal effect estimate 等彼此不同的语义，不能被 Core 当成一个统一概念。

如果外部分析提供 relation strength、statistic、score 或 effect estimate，该结果属于 derived / analytic artifact。其 metric semantics、derivation method、model / algorithm、provenance、version 与 applicable endpoints / relation 需要由未来 derived-result design 明确；R1H 不设计该 Schema。

Source-described qualitative strength 与 derived numeric relation strength **MUST** 保持可区分。

例如来源中的“患者强烈偏好口服药”不能仅因为出现“强烈”就被转换成 `Relation.weight = 0.9`；文本中的“二者高度相关”也不能在没有统计定义时被伪造成 numeric relation weight。

## 15. 术语绑定

PBDL 当前采用以下概念层面的术语绑定模型：

```text
Coding {
    code
    display
    system
    optional version
}
```

在该概念模型中：

- `code + system` 承担机器语义身份。
- `display` 主要用于人类可读展示。
- `version` 为可选信息。

`Coding` 的具体 PBDL 语法和规范化序列化字段仍为 **TODO**。

R0 阶段不冻结任何具体 SNOMED CT、LOINC、ICD 或其他医学术语编码。

## 16. 语义约束

当前已冻结的语义约束如下：

1. PBDL-Core **MUST** 区分来源直接描述的信息与外部推断、分析或计算得到的信息。
2. PBDL-Core **MUST NOT** 因信息被写入 PBDL 就宣称该信息在现实世界中已经被认证为绝对真实。
3. 一个 PBDL document **MUST** 至少包含一个 Subject，并 **MAY** 包含多个 Subject。
4. Subject、Behavior 与 Preference **MUST** 具有 document-local identity。
5. Subject、Behavior 与 Preference 共享同一个 document-local identity namespace，其 identifier **MUST** 在所属 PBDL document 内唯一。
6. identifier **MUST NOT** 由数组位置或列表顺序充当规范性 identity。
7. Behavior 与 Preference **MUST** 各自绑定到恰好一个 Subject。
8. 每个 canonical Behavior **MUST** 实际具有至少一条 provenance linkage。
9. 每个 canonical Preference **MUST** 实际具有至少一条 provenance linkage。
10. canonical semantic representation **MUST** 能区分 DIRECT 与 INFERRED provenance semantics。该判断依据是结构化 semantic content 相对于来源内容是否经过推导，而不是处理链路中是否使用了 LLM、NLP、model 或其他工具。
11. 仅使用工具进行 extraction、parsing、normalization、terminology mapping 或 serialization transformation **MUST NOT** 自动使信息成为 INFERRED。
12. INFERRED information **MUST NOT** 静默表示成 DIRECT / source-described information。
13. 同一个 Behavior / Preference **MAY** 具有多条 provenance linkage，但多来源 **MUST NOT** 自动表示更高真值或可信度。
14. 如果不同来源表达的 semantic content 实质不同或冲突，canonical representation **MUST NOT** 通过 provenance/source 合并、对象折叠或其他方式丢失、掩盖或使这些冲突语义不可区分。默认情况下，separate Behavior / Preference instances **SHOULD** be used。
15. Provenance 与 Evidence **MUST NOT** 被当作完全同义概念。
16. confidence **MUST NOT** 成为所有 Preference 的强制属性，DIRECT self-report **MUST NOT** 被迫赋予模型式 confidence。
17. Provenance 在 R1C 中不要求独立 identity。
18. Semantic time 与 Provenance time **MUST NOT** 被视为同一个时间概念，Provenance / reporting time **MUST NOT** 自动替代 Behavior / Preference / Relation 的 semantic time。
19. Behavior、Preference 与 Relation **SHOULD** 使用共享 Core temporal abstraction 表达 semantic temporal extent。
20. Core temporal abstraction 至少支持 Instant、Interval 与未提供 semantic time 三种最小语义情况。
21. Interval **MUST** 至少具有一个有效边界；若 start 与 end 同时存在且可比较，start **MUST NOT** 晚于 end。
22. 单边界 Interval 中未提供的 opposite boundary 只表示 boundary unspecified / not provided，**MUST NOT** 自动解释为永久、ongoing、一直延伸到现在或未来、从无限过去开始，或数学意义上的 unbounded interval。
23. 缺少 semantic temporal information **MUST NOT** 被解释为永久、当前、始终、反复或“时间不重要”。
24. Canonicalization **MUST** 保留来源实际支持的 temporal precision，并 **MUST NOT** 发明来源未提供的时间精度。
25. 来源未提供 timezone / offset 时，canonicalization **MUST NOT** 凭空补充；来源已提供时，canonical representation **MUST** 能够保留。
26. canonical semantics 中保留的 relative temporal expression **MUST** 具有明确 anchor；无明确 anchor 的裸相对时间 **MUST NOT** 被假装成唯一确定的 absolute temporal extent。
27. Relation temporal metadata **MUST NOT** 自动承担 `precedes` / `follows` 等 Relation type ordering semantics。
28. Behavior type、Preference category、显示标签与 Relation type **MUST NOT** 自动充当 entity instance identity。
29. Core reference **MUST** 在当前文档 reference scope 内解析到恰好一个实体。
30. undefined reference 与 ambiguous reference 均无效。
31. Relation source / target **MUST** 使用明确 entity reference，不能使用未解析的自由文本标签。
32. Core Relation endpoint 仅允许 Behavior 与 Preference；Subject 与 Relation 均不是 R1B 中的 Relation endpoint。
33. Relation 在 v1 Core 最小模型中不要求 identity，且 Relation **MUST NOT** 作为 Relation endpoint。
34. PBDL-Core **MUST NOT** 将未经证据支持的因果权重作为来源直接描述的信息或默认 Core 语义。
35. Treatment Pathway 不属于初始重新设计中的 PBDL-Core。
36. Legacy `trigger` / `triggered` naming **MUST NOT** 单独建立 causal semantics；字段名称本身 **MUST NOT** 被视为因果证据。
37. Source-attributed reason **MUST** 与 verified causal semantics 保持可区分，canonical semantics **MUST NOT** 自动把“某来源声称 X 是 Y 的原因 / 理由”升级为 verified causal relation。
38. Observed / recorded association、co-occurrence 或 temporal antecedence **MUST NOT** 自动升级为 source-attributed reason 或 causal claim；temporal precedence **MUST NOT** 自动推出 causality。
39. INFERRED explanation **MUST NOT** 静默表示为 DIRECT source-attributed reason，并继续遵守 R1C 关于 semantic derivation 的 DIRECT / INFERRED 判定规则。
40. 如果来源不支持 symptom-related direction，canonicalization **MUST NOT** 从 `symptom_triggered` 字段名或时间顺序中发明 direction；已知 direction **MUST NOT** 自动等价为 causality。
41. Context **MUST NOT** 自动建立 causality；Contextual qualification **MUST NOT** 自动等价为 reason、causal explanation 或 verified causal effect。
42. Behavior / Preference 缺少显式 Context **MUST NOT** 被解释为 context-free、universally applicable 或 unconditional；它只表示未提供额外 contextual qualification。
43. Context **MUST NOT** 被用作 Provenance、semantic time、trigger / reason semantics、derived analysis 或 workflow / application state 的默认替代容器。
44. Legacy `communication_status` **MUST NOT** 仅凭字段名决定 canonical semantic category，也 **MUST NOT** 默认冻结为单一通用 Behavior status。
45. Actual communication Behavior、contextual communication metadata、Provenance information 与 workflow / application state **MUST** 保持语义可区分。
46. `communicated` / `reported` / `acknowledged` **MUST NOT** 自动等价为 `verified`、`true`、`agreed` 或来源内容已得到事实认证。
47. Behavior frequency / recurrence **MUST** 与 R1D semantic temporal extent 保持可区分；duration / applicability interval **MUST NOT** 自动等价为 recurrence pattern。
48. Observed / reported occurrence count within a reference window **MUST NOT** 自动等价为 recurring pattern 或稳定 recurrence rule。
49. Qualitative 或 approximate frequency **MUST NOT** 被 canonicalization 擅自数值化、阈值化或提高到来源未提供的精确度。
50. Expected / prescribed schedule **MUST NOT** 自动表示 actual patient Behavior frequency；actual Behavior frequency **MUST NOT** 自动表示 prescribed schedule。
51. Recurring pattern **MUST NOT** 被 canonicalization 自动展开成来源没有提供的 fabricated concrete observed occurrences。
52. 多个 observed occurrence records **MUST NOT** 自动被总结为 recurring pattern；若 pattern 来自外部推断，该 pattern **MUST** 保留 INFERRED provenance semantics，并 **MUST NOT** 静默表示为 DIRECT source-described frequency。
53. 缺少 frequency / recurrence information **MUST NOT** 被解释为 once、only once、non-recurring、irregular、continuous 或任何具体 repetition pattern。
54. Canonicalization **MUST NOT** 在缺少 reference period 时发明 frequency rate，也 **MUST NOT** 在缺少 denominator / expected opportunities 时发明 adherence ratio、adherence percentage 或其他比例。
55. Frequency / recurrence semantics **MUST NOT** 成为所有 Behavior 的强制属性。
56. Relation **MUST NOT** 仅因为实体共现、属于同一 Subject、时间相近、Context 相同或共享来源材料而被隐式创建。
57. Relation type **MUST** 具有定义明确的机器语义并决定 endpoint roles / directionality semantics；source / target ordering 本身 **MUST NOT** 建立 causality、temporal precedence、importance 或其他未由 relation type 定义的语义。
58. Directional Relation **MUST NOT** 自动等价为 causal Relation；对于 symmetric / non-directional relation type，交换 endpoint ordering **MUST NOT** 被解释为不同 semantic relation meaning。
59. Legacy `Preference.associated_behavior` 在 canonical semantics 中 **MUST** 统一表示为 explicit Preference–Behavior Relation，**MUST NOT** 继续形成与 Relation 平行的 canonical link mechanism。
60. Legacy `associated_behavior` reference **MUST** 解析到恰好一个 Behavior identity；undefined / unresolved 或 ambiguous mapping 无效，canonical transformation **MUST NOT** 静默猜测目标。
61. Canonical transformation **MUST NOT** 仅凭 legacy `associated_behavior` 发明比来源支持更强的 relation semantics。
62. 每个 canonical Relation assertion **MUST** 具有至少一条 provenance linkage 或等价可追踪 provenance semantics；endpoint provenance **MUST NOT** 自动替代 Relation assertion provenance。
63. INFERRED Relation assertion **MUST NOT** 静默表示为 DIRECT source-described Relation，即使其 endpoints 分别具有 DIRECT provenance。
64. Semantically distinct Relation assertions **MUST NOT** 仅因为 endpoints 相同而被静默合并；relation type、direction、temporal applicability 与 derivation / provenance distinction 必须得到保留。
65. `Relation.weight` **MUST NOT** 作为默认 Core Relation intrinsic semantic strength；derived numeric strength / statistic **MUST** 与 source-described relation semantics 保持可区分。
66. Undefined 或 free-text-only relation type semantics **MUST NOT** 被当作 canonical machine semantics。
67. Annotation **MUST NOT** 作为已有 structured canonical machine semantics 的唯一替代载体；conforming consumer **MUST NOT** 被迫解析自由文本 Annotation 才能确定核心机器语义。
68. Annotation text **MUST NOT** 自动创建新的 Behavior、Preference、Relation、Context、causal claim、risk result、recommendation 或其他 derived analysis result。
69. Annotation **MUST NOT** 替代 mandatory Provenance；source / generator / DIRECT / INFERRED derivation **MUST NOT** 仅通过自由文本 note 表达并要求下游猜测。
70. Legacy `Behavior.reasoning_note` 与 `Preference.note` 在 canonical semantic ownership 上统一收敛到 Annotation semantics，但 Annotation **MUST NOT** 因此获得 required identity 或 Relation endpoint status。
71. Model / analytic process 在来源未表达的基础上生成的 explanatory Annotation **MUST** 保持 INFERRED derivation semantics，并 **MUST NOT** 伪装为 DIRECT source text；faithful extraction / normalization 本身 **MUST NOT** 自动使 Annotation 成为 INFERRED。
72. Annotation **MUST NOT** 自动等价于 Evidence，也 **MUST NOT** 仅凭文本内容建立 causality 或 Relation。
73. Annotation 与 structured canonical semantics 冲突时，conforming consumer **MUST NOT** 仅根据 Annotation 静默覆盖 structured semantics。
74. PBDL-Core **MUST NOT** 要求 hidden chain-of-thought、private model reasoning trace、internal scratchpad 或 hidden model deliberation 作为规范性 Annotation 内容。

跨文档 identity / reference protocol、exact TemporalValue lexical profile、BehaviorFrequency / Context / BehaviorFactor internals、PreferenceValue leaf type system、Confidence concrete structure / metric model、Coding final serialization、communication vocabulary、Constraint / Barrier model、normative relation vocabulary / codes / inverse conventions、derived relation-strength artifact Schema、JSON Schema、DSL syntax 与术语词表仍为 **TODO**。

## 17. Canonical Object Model

R2A 冻结 PBDL-Core 的 field-level canonical object model。

本节冻结 canonical object graph、field ownership、required / optional、cardinality、nested qualifier ownership、typed reference ownership、mandatory provenance attachment pattern 与 legacy-to-canonical representation ownership。

本节 **不是** JSON serialization freeze、JSON Schema freeze、DSL syntax freeze 或 implementation specification。

[schema/pbdl-v1.schema.json](schema/pbdl-v1.schema.json) 仍只是 JSON Schema Draft 2020-12 占位文件，R2A **MUST NOT** 被解释为已经修改或冻结该 Schema 文件。

### 17.1 Canonical root: PBDLDocument

Canonical root object 名称冻结为 PBDLDocument。

| Field | Type | Cardinality | Requirement |
|---|---|---:|---|
| pbdl_version | VersionToken | 1 | REQUIRED |
| subjects | Subject | 1..* | REQUIRED collection |
| behaviors | Behavior | 0..* | REQUIRED collection, MAY be empty |
| preferences | Preference | 0..* | REQUIRED collection, MAY be empty |
| relations | Relation | 0..* | REQUIRED collection, MAY be empty |

Canonical document **MUST** carry an explicit PBDL version declaration through pbdl_version。

R2B1 冻结 VersionToken 为 constrained string lexical token。

当前 PBDL 1.0 canonical document 的 `pbdl_version` **MUST** 精确为：

    "1.0"

VersionToken 只表示 PBDL language / canonical-model version，**MUST NOT** 携带 implementation build number、git SHA、model version、schema URI 或产品版本。

当前规范不允许任意 implementation-defined version token 冒充 PBDL version。未来 PBDL 版本应由对应规范显式定义新的 canonical token。

PBDLDocument **MUST NOT** 增加 document-level risk、recommendation、Pathway、workflow state、global annotation bag 或 global arbitrary metadata bag 作为 R2A Core fields。

### 17.2 Root collection ordering

subjects、behaviors、preferences、relations 的 collection position **MUST NOT** 承担 entity identity。

除非未来某个 nested type 另行冻结 order semantics，canonical collection ordering **MUST NOT** 被下游解释为：

- priority；
- causality；
- temporal order；
- ranking；
- semantic identity。

Canonical serialization sorting 规则仍未冻结。

### 17.3 Subject

Canonical Subject field inventory：

| Field | Type | Cardinality | Requirement |
|---|---|---:|---|
| id | EntityId | 1 | REQUIRED |

R2A 不给 Subject 增加 name、age、sex、address、phone、完整 demographics、完整 EHR record、annotations、provenance、context 或 workflow metadata。

Subject / Behavior / Preference 继续共享 R1B document-local identity namespace。

R2B1 冻结 EntityId 为 non-empty、case-sensitive ASCII lexical token：

    [A-Za-z_][A-Za-z0-9._-]*

EntityId **MUST** 满足该 lexical profile。

EntityId 不要求 UUID，不承载全局 identity，也 **MUST NOT** 由 display、type、Coding.code 或 collection position 派生。

Subject / Behavior / Preference 继续共享同一个 document-local EntityId namespace。

### 17.4 Behavior

Canonical Behavior field inventory：

| Field | Type | Cardinality | Requirement |
|---|---|---:|---|
| id | EntityId | 1 | REQUIRED |
| subject | SubjectRef | 1 | REQUIRED |
| type | Coding | 1 | REQUIRED |
| executor | ActorRef | 0..1 | OPTIONAL |
| temporal | TemporalExtent | 0..1 | OPTIONAL |
| frequencies | BehaviorFrequency | 0..* | OPTIONAL collection |
| contexts | Context | 0..* | OPTIONAL collection |
| factors | BehaviorFactor | 0..* | OPTIONAL collection |
| provenance | Provenance | 1..* | REQUIRED |
| annotations | Annotation | 0..* | OPTIONAL collection |

Canonical field name type 正式承担 legacy behavior_type 的 structured machine meaning：

- legacy Behavior.behavior_type → Behavior.type。

Canonical model **MUST NOT** 同时保留 type 与 behavior_type 两套平行 fields。

#### 17.4.1 Behavior.type

Behavior.type 使用 §15 已定义的 Coding semantic type。

Coding 的概念职责保持：

- code + system 承担机器语义 identity；
- display 为人类可读展示；
- version 为可选信息。

Coding 的 concrete JSON serialization 仍未冻结。

Behavior.type **MUST** 承担 structured machine semantics，**MUST NOT** 由 Annotation 替代。

#### 17.4.2 Behavior.executor

executor 保留 R1B legacy executor semantic capability，并为 OPTIONAL ActorRef。

executor 表示谁执行或参与 Behavior；它 **MUST NOT** 被等价为 Subject ownership。

R2B1 冻结 ActorRef canonical union：

    ActorRef = SubjectRef | ExternalActorRef

SubjectRef variant 使用 §17.7 冻结的 canonical reference object：

    { "ref": EntityId }

ExternalActorRef variant 使用与 SubjectRef 结构互斥的 object：

    {
        "kind": "person" | "device" | "software" | "other",
        "external_id"?: {
            "system": string,
            "value": string
        },
        "display"?: Text,
        "role"?: Text
    }

ExternalActorRef.kind 为 REQUIRED。

external_id、display、role 均 OPTIONAL。

若 external_id 存在，其 system 与 value **MUST** 为 non-empty string。external_id 表示外部命名空间中的稳定 identifier，**不属于** PBDL Core EntityId namespace。

display / role 仅为 human-readable description，**MUST NOT** 单独建立 stable actor identity。

Caregiver / clinician 通常可使用 kind = "person" 并通过 role / display 描述；device 使用 kind = "device"；external software / system 使用 kind = "software"。

ActorRef union 采用 structural discrimination：

- 含 REQUIRED `ref` 且不含 ExternalActorRef fields 的 object → SubjectRef；
- 含 REQUIRED `kind` 且不含 `ref` 的 object → ExternalActorRef。

同时含 `ref` 与 `kind` 的 ActorRef **MUST** 被视为无效 canonical representation。

ExternalActorRef 是 non-identity-bearing embedded descriptor，不进入 Subject / Behavior / Preference document-local identity namespace，也不成为 Relation endpoint。

如果来源提供稳定 external_id，该 external identity **MAY** 用于表达多个 Behavior 中的同一 external actor。

如果只有 display / role 而无 external_id，canonical consumer **MUST NOT** 因文本相同就断言多个 Behavior 描述的是同一个 stable actor instance。

R2B1 不新增 Actor / Participant entity、Participant identity namespace 或 Participant Relation endpoint。

#### 17.4.3 Behavior.temporal and TemporalExtent

Behavior.temporal 为 OPTIONAL single TemporalExtent。

R2A 冻结 TemporalExtent 的两种 canonical structured shape：

    TemporalExtent = Instant | Interval

    Instant {
        kind : "instant"
        at   : TemporalValue
    }

    Interval {
        kind   : "interval"
        start? : TemporalValue
        end?   : TemporalValue
    }

Interval 的 start / end 至少一个存在。

TemporalValue 的 lexical format、precision encoding 与 timezone serialization 留待 R2B。

R1D 允许 relative time 带 anchor 保留或在 canonicalization 前解析。R2A 选择更严格的 canonical representation：TemporalExtent 当前只冻结 Instant / Interval。

如果上游可基于明确 anchor 将 relative expression 可靠解析为 Instant / Interval，则 **MAY** canonicalize。

如果不能可靠解析，canonicalization **MUST NOT** 发明 absolute time 或把 unresolved relative expression 伪装成 absolute TemporalExtent。

原始 relative phrase **MAY** 通过 Evidence / Annotation 保真保存，但 **MUST NOT** 被当作 structured TemporalExtent。

#### 17.4.4 Behavior.frequencies

Behavior.frequencies 为 OPTIONAL BehaviorFrequency[0..*]。

BehaviorFrequency 是独立 structured qualifier type，用于承载 R1G 已区分的 observed / reported count、recurrence pattern、qualitative frequency 等 frequency semantics。

BehaviorFrequency 的 exact fields、period structure、recurrence representation、qualitative vocabulary 与 serialization 留待 R2B。

Canonical representation **MUST NOT** 使用 frequency : arbitrary string 作为最终机器语义替代。

BehaviorFrequency **MAY** carry local Provenance。

如果某个 frequency assertion 与 owner Behavior 具有不同 source、generator 或 DIRECT / INFERRED derivation，或者该 frequency assertion 只由 owner provenance 的真子集支持，则该 BehaviorFrequency **MUST** 携带自己的 local provenance。

BehaviorFrequency 只有在其 provenance semantics 与 owner 对该 qualifier 的**完整 applicable provenance set**一致时，才 **MAY** 省略 local provenance 并继承 owner provenance。

省略 local provenance **MUST NOT** 表示“任选 owner provenance 中的一条”或允许实现自行猜测支持该 qualifier 的 provenance。

Concrete provenance inheritance serialization 与 validation 留待 R2B，但 canonical model **MUST NOT** 丢失 DIRECT Behavior + INFERRED frequency，或 owner 多 provenance + qualifier subset support 的区别。

#### 17.4.5 Behavior.contexts

Behavior.contexts 为 OPTIONAL Context[0..*]。

Context 不是 identity-bearing entity，不进入 document root collection。

R2A 冻结 Context canonical ownership 至少包括：

- Behavior.contexts；
- Preference.contexts。

Context concrete internal fields、cardinality / nesting details 留待 R2B。

Context **MUST NOT** 成为 arbitrary metadata bag。

Context **MAY** carry local provenance。

如果 Context 的 source、generator、derivation 与 owner assertion 不同，或者该 Context 只由 owner provenance 的真子集支持，则 Context **MUST** 携带自己的 local provenance。

只有当 Context 的 provenance semantics 与 owner 对该 Context 的完整 applicable provenance set 一致时，才 **MAY** 省略 local provenance 并继承 owner provenance。

#### 17.4.6 Behavior.factors

Behavior.factors 为 OPTIONAL BehaviorFactor[0..*]。

BehaviorFactor 承载 R1E 中 Behavior-local、不能自然表示成两个 Core entities 之间 Relation 的 structured factor semantics，例如：

- source-attributed reason；
- observed / recorded association or antecedent；
- inferred explanation；
- symptom-related association / direction；
- non-Core semantic factor。

BehaviorFactor **MUST NOT** 成为 generic Relation replacement。

如果 source 与 target 都是允许的 Core entities，且语义是 explicit typed entity relationship，则 canonical model 仍 **MUST** 使用 Relation。

R2A 不冻结 BehaviorFactor concrete leaf fields、factor vocabulary 或 symptom terminology；这些留待 R2B。

BehaviorFactor **MUST** 是 structured qualifier，而不是 arbitrary reasoning string。

BehaviorFactor representation **MUST** 支持 local provenance。

当 BehaviorFactor 的 source、generator、derivation 与 owner Behavior 不同，或者该 factor 只由 owner provenance 的真子集支持时，local provenance **MUST** 被保留。

只有当 BehaviorFactor 的 provenance semantics 与 owner 对该 factor 的完整 applicable provenance set 一致时，才 **MAY** 省略 local provenance 并继承 owner provenance。

这既防止 inferred explanation 因 owner Behavior 为 DIRECT 而伪装成 DIRECT，也防止 owner 的无关 provenance 被错误解释为共同支持该 factor。

#### 17.4.7 Legacy Behavior ownership

Canonical Behavior **MUST NOT** 保留 communication_status 字段。

Legacy communication_status 按 R1F canonicalize：

- actual communication behavior → Behavior；
- contextual communication qualification → Context；
- source / reporting information → Provenance；
- workflow / application state → Core 外。

Canonical Behavior **MUST NOT** 保留 risk_tag、validity_flag 或 reasoning_note：

- risk_tag → derived / application result；
- validity_flag → validator / report output；
- reasoning_note → annotations。

其他主要 legacy mapping：

| Legacy | Canonical ownership |
|---|---|
| behavior_type | Behavior.type |
| executor | Behavior.executor |
| temporal_scope | Behavior.temporal |
| evidence_source | Behavior.provenance |
| behavior_trigger / symptom_triggered | Behavior.factors when Behavior-local non-Core factor; Relation when both endpoints are Core entities and semantics are explicit typed relation |

### 17.5 Preference

Canonical Preference field inventory：

| Field | Type | Cardinality | Requirement |
|---|---|---:|---|
| id | EntityId | 1 | REQUIRED |
| subject | SubjectRef | 1 | REQUIRED |
| category | Coding | 1 | REQUIRED |
| value | PreferenceValue | 1 | REQUIRED |
| temporal | TemporalExtent | 0..1 | OPTIONAL |
| contexts | Context | 0..* | OPTIONAL collection |
| provenance | Provenance | 1..* | REQUIRED |
| annotations | Annotation | 0..* | OPTIONAL collection |

PreferenceValue 是 named structured semantic type；其 complete leaf type system 留待 R2B。

Legacy ownership：

| Legacy | Canonical ownership |
|---|---|
| preference_category | Preference.category |
| preference_value | Preference.value |
| source_type | Preference.provenance |
| confidence_score | Provenance.confidence when semantics / generator are supportable |
| associated_behavior | Relation |
| note | Preference.annotations |
| preference_conflict_flag | derived ConflictAnalysis / application result |

Canonical Preference **MUST NOT** 继续保留 source_type、confidence_score、associated_behavior、note、preference_conflict_flag、preference_category 或 preference_value 作为与新 ownership 平行的 legacy fields。

Legacy confidence_score **MUST NOT** 被无条件搬入 Provenance.confidence；只有在其 metric meaning 与 generator / inference process 可说明时才可保留。

### 17.6 Relation

Canonical Relation field inventory：

| Field | Type | Cardinality | Requirement |
|---|---|---:|---|
| source | CoreEntityRef | 1 | REQUIRED |
| target | CoreEntityRef | 1 | REQUIRED |
| type | Coding | 1 | REQUIRED |
| temporal | TemporalExtent | 0..1 | OPTIONAL |
| provenance | Provenance | 1..* | REQUIRED |
| annotations | Annotation | 0..* | OPTIONAL collection |

Relation 继续 **不要求 id field**。

R2B0 relation-identity stress test 维持该决定：Core Relation 表达 semantic assertion，而不承诺跨文档版本的 stable lifecycle handle。

同一 endpoint pair 上 type、temporal applicability 或 provenance semantics 不同的 Relation assertions 继续依其 canonical semantic content 保持可区分。

仅 Annotation 发生变化 **MUST NOT** 被解释为 Relation 因此获得新的 Core identity；temporal / type / provenance semantic content 的变化则可以表示一个不同的 Relation assertion。

Cross-version lifecycle tracking、audit handles 与 Core 外 derived artifacts 对特定 Relation assertion 的稳定定位属于 application / extension responsibility，**MUST NOT** 通过 collection position 冒充 Core identity。

Canonical Relation **MUST NOT** 具有 weight field、nested Relation endpoint 或独立 inferred direction field。

Relation directionality 继续由 Relation.type semantic contract 决定。

Legacy Relation.weight 继续属于 derived / analytic artifact，不进入 canonical Core Relation。

### 17.7 Typed references

R2B1 冻结唯一 canonical internal reference shape：

    {
        "ref": EntityId
    }

SubjectRef 与 CoreEntityRef 使用同一 object shape，但具有不同 typed resolution contract。

#### 17.7.1 SubjectRef

    SubjectRef {
        ref : EntityId
    }

SubjectRef.ref **MUST** 解析到当前 PBDLDocument 中恰好一个 Subject。

#### 17.7.2 CoreEntityRef

    CoreEntityRef {
        ref : EntityId
    }

CoreEntityRef.ref **MUST** 解析到当前 PBDLDocument 中恰好一个 Behavior 或 Preference，并继续受 R1B global Relation endpoint matrix 与具体 Relation.type allowed endpoint roles 共同约束。

Bare EntityId string **MUST NOT** 作为 canonical reference representation。

Reference object **MUST NOT** 使用 display label、array index、Coding.code 或 type label 代替 ref。

R2B1 选择 object wrapper 而不是 bare string，以减少 display-string ambiguity，并为 future versioned reference extension 保留明确结构边界；当前 canonical reference object 不增加 display 或 type 字段。

### 17.8 Provenance

Canonical Provenance 最小 field inventory：

| Field | Type | Cardinality | Requirement |
|---|---|---:|---|
| derivation | DerivationKind | 1 | REQUIRED |
| source | SourceDescriptor | 0..1 | OPTIONAL, conditionally required |
| generator | GeneratorDescriptor | 0..1 | OPTIONAL, conditionally required |
| evidence | Evidence | 0..* | OPTIONAL collection |
| confidence | Confidence | 0..1 | OPTIONAL |

Provenance 不要求 identity，也不进入 document-level pool。

Provenance 默认 embedded / attached to the assertion it traces：

- Behavior.provenance : Provenance[1..*]；
- Preference.provenance : Provenance[1..*]；
- Relation.provenance : Provenance[1..*]；
- Annotation.provenance : Provenance[1..*]。

#### 17.8.1 Provenance.derivation

R2B0 stress test 冻结 DerivationKind 的三种 semantic states：

- DIRECT；
- INFERRED；
- UNDETERMINED。

R2A/R1C 已冻结的 DIRECT / INFERRED distinction 保持不变。

DIRECT 表示 structured semantic content 忠实来自 source-described / recorded / observed information。

INFERRED 表示 semantic content 超出来源直接表达，由 human、model、rule 或 analytic process 产生推导。

UNDETERMINED 仅表示：derivation metadata 对 canonicalizer / migration pipeline **真实不可用或无法可靠判定**。

UNDETERMINED **MUST NOT** 被解释为：

- partly direct / partly inferred；
- consumer may treat as direct；
- producer 可以在 derivation 已知时跳过分类；
- 一种 confidence level。

新生成 canonical PBDL 的 producer 如果拥有足够信息判定 DIRECT 或 INFERRED，**MUST NOT** 使用 UNDETERMINED 逃避分类。

Legacy migration 在历史 metadata 不足、无法可靠重建 derivation 时 **MAY** 使用 UNDETERMINED，而 **MUST NOT** 猜测 DIRECT 或 INFERRED。

UNDETERMINED provenance **MUST** 保持至少一条可追踪 source path；通常 source 可以是被迁移的 legacy record / source material。已知的 source、generator、Evidence information **MUST** 被保留，缺失 metadata **MUST NOT** 被发明。

如果连最小可追踪 source path 都不存在，则 canonicalization **MUST** 报告 provenance requirement 无法满足，而 **MUST NOT** 仅靠 UNDETERMINED token 伪造 provenance completeness。

UNDETERMINED 是 canonical-valid migration semantics，但 conforming validator **SHOULD** 产生 provenance-quality warning，以提示 derivation classification 未能恢复。

Tool / generator 的存在本身 **MUST NOT** 决定 derivation。

R2B1 冻结 DerivationKind canonical lexical tokens 为且仅为：

- `"direct"`
- `"inferred"`
- `"undetermined"`

Canonical representation **MUST NOT** 使用 `DIRECT`、`INFERRED`、`UNDETERMINED`、`unknown`、`unspecified`、`mixed` 或其他平行 synonym 作为 serialized token。

#### 17.8.2 Provenance.source and generator

source 表示原始 information source / source descriptor。

generator 表示产生、抽取、转换或推导 semantic result 的 human / model / rule / analytic agent or process descriptor。

Conditional invariants：

- DIRECT provenance **MUST** have source；
- INFERRED provenance **MUST** have generator；
- UNDETERMINED provenance **MUST** have source，以保留最小 traceable source path；generator **MAY** 存在，例如 migration / transformation process。

一个 Provenance **MAY** 同时具有 source 与 generator。

例如 LLM 从 EHR 文本忠实抽取 DIRECT semantics 时，可以是：

- source = EHR source；
- generator = extraction system；
- derivation = "direct"。

因此 generator 的存在 **MUST NOT** 自动意味着 inferred。

R2B1 **MUST NOT** 在 Provenance 顶层重新引入无角色 generic `time : TemporalValue`。

#### 17.8.3 SourceDescriptor

Canonical SourceDescriptor：

    SourceDescriptor {
        kind         : SourceKind
        locator?     : string
        display?     : Text
        times?       : SourceTimeEvent[0..*]
    }

SourceDescriptor.kind 为 REQUIRED，并使用以下 canonical lowercase tokens：

- `"patient_self_report"`
- `"questionnaire"`
- `"clinician_documentation"`
- `"ehr_record"`
- `"device_observation"`
- `"legacy_record"`
- `"other"`

locator 为 OPTIONAL non-empty string，用于保存 source-system external identifier / locator。它不是 PBDL Core reference，也不加入 EntityId namespace。

display 为 OPTIONAL human-readable source description。

SourceTimeEvent：

    SourceTimeEvent {
        role : "reported" | "recorded" | "observed"
        at   : TemporalValue
    }

role 与 at 均 REQUIRED。

SourceDescriptor.times 的 collection ordering **MUST NOT** 具有 semantic meaning。

Source / reporting / recording / observation related time **MUST** 使用 role-explicit SourceTimeEvent；**MUST NOT** 被压回一个 ambiguous generic provenance time。

如果某个时间属于具体 Evidence material 而不是 source descriptor 整体，应由该 Evidence item 的 times 承载。

#### 17.8.4 GeneratorDescriptor

Canonical GeneratorDescriptor：

    GeneratorDescriptor {
        kind        : GeneratorKind
        identifier? : string
        version?    : string
        display?    : Text
        times?      : GeneratorTimeEvent[0..*]
    }

GeneratorDescriptor.kind 为 REQUIRED，并使用以下 canonical lowercase tokens：

- `"human"`
- `"llm"`
- `"rule_engine"`
- `"analytic_model"`
- `"migration_process"`
- `"other"`

identifier、version、display 均 OPTIONAL；若 identifier / version 存在，值 **MUST** 为 non-empty string。

GeneratorDescriptor identifier 不是 PBDL Core EntityId，也不建立 Participant identity。

GeneratorTimeEvent：

    GeneratorTimeEvent {
        role : "extracted" | "generated" | "transformed" | "migrated"
        at   : TemporalValue
    }

role 与 at 均 REQUIRED。

GeneratorDescriptor.times 的 collection ordering **MUST NOT** 具有 semantic meaning。

Extraction / generation / transformation / migration related time **MUST** 使用 role-explicit GeneratorTimeEvent。

GeneratorDescriptor 的存在 **MUST NOT** 自动把 derivation 判为 `"inferred"`。

#### 17.8.5 Evidence

Canonical Evidence：

    Evidence {
        kind      : EvidenceKind
        content?  : Text
        locator?  : string
        times?    : SourceTimeEvent[0..*]
    }

Evidence.kind 为 REQUIRED，并使用以下 canonical lowercase tokens：

- `"text_excerpt"`
- `"document_reference"`
- `"questionnaire_response"`
- `"device_observation"`
- `"legacy_material"`
- `"other"`

content 与 locator 均 OPTIONAL，但一个 Evidence **MUST** 至少提供二者之一。

content 用于 inline human-readable excerpt / response；locator 用于 external material locator。二者 **MAY** 同时存在。

Evidence.times **MAY** 使用 SourceTimeEvent 保存只属于该 evidence item 的 reported / recorded / observed time。

如果同一个 source-related time 已由更具体 Evidence item 承载，canonical representation **SHOULD NOT** 为了方便而无语义区别地同时复制到 SourceDescriptor.times。

Evidence 继续：

- no required identity；
- embedded under Provenance；
- **MUST NOT** 与 Annotation 合并；
- **MUST NOT** 要求复制完整 EHR / source document 进入 PBDL Core。

#### 17.8.4 Provenance.confidence

如果 canonical Core 需要保留 inference confidence，其 canonical ownership 为 optional Provenance.confidence。

Confidence **MUST NOT** 成为 Behavior / Preference / Relation intrinsic truth field。

DIRECT self-report **MUST NOT** 被迫填写 Confidence。

Confidence 的 scale、range、metric、calibration、numeric representation 与 validation 留待 R2B / 后续工作。

### 17.9 Annotation

Canonical Annotation 最小 field inventory：

| Field | Type | Cardinality | Requirement |
|---|---|---:|---|
| text | Text | 1 | REQUIRED |
| provenance | Provenance | 1..* | REQUIRED |

Annotation：

- 不要求 id；
- 不是 Relation endpoint；
- 不进入独立 document-level collection；
- 作为 lightweight embedded structure 附着于当前允许的 canonical assertion/object。

R2A 允许：

- Behavior.annotations；
- Preference.annotations；
- Relation.annotations。

R2A 不增加 Subject.annotations。

每个 Annotation **MUST** 具有自己的 provenance[1..*]，从而区分 source-carried、human-authored 与 model-generated annotation。

Annotation owner 的 provenance **MUST NOT** 在 source / generator / derivation 不同时自动替代 Annotation provenance。

Text lexical constraints 留待 R2B。

### 17.10 Nested qualifier provenance inheritance and equality

Owner-level provenance 描述 owner assertion。

R2B1 冻结 BehaviorFrequency / BehaviorFactor / Context 共用的 local provenance field contract：

    provenance? : Provenance[1..*]

该 field 整体 OPTIONAL；一旦存在，collection **MUST** 至少包含一个 Provenance。显式空 collection `provenance: []` **MUST NOT** 用来表示 inheritance。

#### 17.10.1 Omitted local provenance

Nested semantic qualifier **MAY** 省略 local provenance，**仅当**该 qualifier 的 provenance semantics 与 owner 对该 qualifier 的完整 applicable provenance set 一致。

省略 local provenance 表示 structural dynamic inheritance of the complete current applicable owner provenance set。

Canonical serialized document **MUST NOT** 依赖不可见历史 snapshot 来解释省略的 local provenance。

因此，如果 owner provenance 从 {P1,P2} 修改为 {P1,P2,P3}，而 qualifier 继续省略 local provenance，则新 document 中该 qualifier 的 inherited provenance semantics 也变为 {P1,P2,P3}。

如果 transformation 需要 qualifier 继续只由旧集合 {P1,P2} 支持，则在 owner 增加 P3 时 qualifier **MUST** materialize explicit local provenance。

#### 17.10.2 Explicit local provenance

如果 qualifier：

- source 不同；
- generator 不同；
- derivation 不同；
- 或仅由 owner provenance 的真子集支持；

则该 qualifier **MUST** 携带 explicit local provenance。

当 local provenance 存在时，它表示 qualifier 的 complete provenance set，并完全覆盖 inheritance。

Canonical model **MUST NOT** 支持 “inherit owner provenance + add local provenance” 的 additive hybrid merge semantics。

#### 17.10.3 Provenance semantic equality

两个 Provenance 只有在以下 concrete dimensions 均 semantic-equivalent 时，R2B1 才允许把它们视为 semantic-equivalent：

1. derivation token 相同；
2. source 都缺失，或 SourceDescriptor semantic-equivalent；
3. generator 都缺失，或 GeneratorDescriptor semantic-equivalent；
4. evidence collections 按 order-insensitive comparison semantic-equivalent；
5. confidence 都缺失；若任一 Provenance 具有 confidence，在 Confidence concrete semantics 冻结前，R2B1 **MUST NOT** 假定两者 confidence-equivalent。

SourceDescriptor / GeneratorDescriptor / Evidence 的 semantic equality 基于其 R2B1 concrete fields：

- scalar / token fields 值相同；
- optional field 同时缺失或值相同；
- times collections 采用 order-insensitive comparison；
- Evidence collections 采用 order-insensitive comparison。

Collection comparison 使用 one-to-one semantic matching；collection order **MUST NOT** 产生 semantic difference。R2B1 不冻结 duplicate elimination semantics。

#### 17.10.4 Canonical normalization

Qualifier 省略 local provenance并继承 owner set {P1...Pn}，与 qualifier 显式 local provenance 为同一个 complete semantic set {P1...Pn} 时，两者 **MUST** 被视为 semantic-equivalent。

Canonical normalization **MUST** 省略与 inherited complete owner set semantic-equivalent 的 redundant explicit local provenance。

因此：

- owner {P1}, child omitted；
- owner {P1}, child explicit {P1}；

semantic-equivalent，且 canonical form 为 child omitted provenance。

同理，owner {P1,P2}, child explicit {P1,P2} 必须 canonicalize 为 omitted local provenance。

Provenance collection ordering **MUST NOT** 产生 semantic difference。

由于 TemporalValue、Text lexical constraints 与 Confidence concrete representation 尚未全部冻结，R2B1 **不冻结** canonical provenance sorting key。Deterministic serialization ordering 留待 final serialization round，但 semantic equality **MUST** 已按上述 order-insensitive rules 判断。

#### 17.10.5 Scope

上述 inheritance / override / equality / normalization semantics 至少统一适用于：

- BehaviorFrequency；
- BehaviorFactor；
- Context。

Temporal local provenance 是否采用相同机制留待 R2B 后续。

Canonical model **MUST NOT** 用单一 owner-level DIRECT / INFERRED / UNDETERMINED label 粗暴覆盖内部 derivation 实际不同的 nested qualifier，也 **MUST NOT** 把 owner 中不支持该 qualifier 的 provenance 错误继承给 qualifier。

### 17.11 Identity-bearing entities vs embedded structures

R2A 保持 R1B identity boundary：

- Subject：required identity；
- Behavior：required identity；
- Preference：required identity；
- Relation：no required identity。

以下 R2A named structures 不获得 required identity，不加入 Subject / Behavior / Preference document-local identity namespace，也不是 Relation endpoint：

- TemporalExtent；
- BehaviorFrequency；
- Context；
- BehaviorFactor；
- Annotation；
- Provenance；
- Evidence。

PBDLDocument 是 canonical root container，不因本节获得 entity identity semantics。

### 17.12 Canonical ownership replaces legacy parallel fields

Canonical model **MUST NOT** 同时保留以下平行 mechanisms：

| Canonical ownership | Legacy parallel field that MUST NOT coexist canonically |
|---|---|
| Behavior.type | Behavior.behavior_type |
| Preference.category | Preference.preference_category |
| Preference.value | Preference.preference_value |
| Behavior.annotations | Behavior.reasoning_note |
| Preference.annotations | Preference.note |
| Relation | Preference.associated_behavior |
| Provenance | Behavior.evidence_source |
| Provenance | Preference.source_type |
| Context / Behavior / Provenance / application layer according to semantics | Behavior.communication_status |

Legacy input **MAY** 被迁移，但 canonical output **MUST** 只使用 R2A ownership。

### 17.13 Fields explicitly outside canonical Core

以下 legacy fields **MUST NOT** 进入 PBDL-Core canonical object model：

- Behavior.risk_tag → derived / application result；
- Behavior.validity_flag → validator / report output；
- Preference.preference_conflict_flag → derived ConflictAnalysis / application result；
- Relation.weight → derived / analytic artifact；
- 所有 Treatment Path / Pathway fields → extension / application layer。

这些 fields **MUST NOT** 为了历史兼容被重新塞回 canonical Core。

### 17.14 Remaining deferred named types after R2B1

R2B1 已 concretize：

- VersionToken；
- EntityId；
- SubjectRef；
- CoreEntityRef；
- ActorRef union representation；
- ExternalActorRef；
- DerivationKind lexical tokens；
- SourceDescriptor；
- GeneratorDescriptor；
- Evidence；
- canonical reference representation；
- nested provenance field/cardinality；
- minimum provenance equality / ordering semantics。

仍需后续 R2B concretize：

- TemporalValue；
- BehaviorFrequency non-provenance fields；
- Context non-provenance fields；
- BehaviorFactor non-provenance fields；
- PreferenceValue；
- Confidence；
- Text lexical constraints；
- Coding concrete JSON serialization；
- canonical sorting key where final leaf serialization is required。

R2B1 不设计 JSON Schema、EBNF、DSL syntax、parser、validator implementation 或 runtime。

## 18. 校验模型

完整校验架构尚未冻结。

未来的校验模型预计至少需要区分结构合法性与语义合法性，但具体分层、严重级别模型、错误码与实现仍为 **TODO**。

R2B0 只冻结一个与 DerivationKind 直接相关的 validation consequence：

- legacy migration 因历史 metadata 真实不足而使用 `"undetermined"`，可以形成 canonical-valid provenance；
- conforming validator **SHOULD** 对 `"undetermined"` 产生 provenance-quality warning；
- producer 已掌握足够 derivation information 却使用 `"undetermined"`，属于 semantic non-conformance；
- 缺少最小 traceable source path 时，`"undetermined"` **MUST NOT** 使 provenance requirement 自动变为 satisfied。

R2B0 不定义 Validator implementation。

## 19. 扩展机制

扩展机制尚未设计。

Treatment Pathway **MAY** 在未来作为扩展或上层应用进行设计，但当前不属于 PBDL-Core。

**TODO：** 定义扩展命名空间或标识方式、兼容规则、扩展发现机制，以及扩展如何参与 Core 校验且不得静默改写 Core 语义。

## 20. 示例

当前尚未编写规范性或非规范性示例。

示例目录已预留：

- `examples/valid/`
- `examples/invalid/`

**TODO：** 仅在相应语法和语义被冻结之后添加示例。

## 21. 版本与兼容性

目标规范版本为 PBDL 1.0，当前设计阶段为 v0.1 语言基础。

兼容性模型尚未冻结。

**TODO：** 定义语言版本声明、向后 / 向前兼容预期、弃用策略和扩展兼容规则。

## 附录 A：语法

当前语法占位文件位于 [`grammar/pbdl.ebnf`](grammar/pbdl.ebnf)。

R0 阶段的语法有意保持不完整。

## 附录 B：校验错误码

**TODO：** 在校验语义冻结后定义错误码体系。

R0 阶段不存在规范性错误码。

## 附录 C：保留关键字

**TODO：** 在词法结构与具体语法冻结后定义保留关键字。

R0 阶段不存在规范性的 DSL 关键字。

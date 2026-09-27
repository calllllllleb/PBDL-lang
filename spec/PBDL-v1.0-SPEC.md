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

Context 仍属于 PBDL-Core 的候选概念。Provenance 与 Evidence 的最小语义边界已由 R1C 冻结为两个相关但不等价的概念；其具体字段、Schema、identity / reference 细节仍未完全冻结。

### 5.1 文档与 Subject 绑定

一个 PBDL document **MUST** 至少包含一个 Subject。

一个 PBDL document **MAY** 包含多个 Subject。

每个 Behavior **MUST** 绑定到且仅绑定到一个 Subject。

每个 Preference **MUST** 绑定到且仅绑定到一个 Subject。

本轮只冻结上述语义要求，不冻结具体字段名、文本语法或序列化形式。即使未来 surface syntax 在单 Subject 文档中允许省略显式主体引用，规范化语义仍 **MUST** 能够确定该 Behavior 或 Preference 唯一对应的 Subject。

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

精确的引用字段名、序列化结构与 DSL syntax 仍为 **TODO**。

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

#### 5.7.7 Frequency / recurrence 留待后续

`daily`、`weekly`、`often`、`sometimes`、`three_times_per_week`、`every_morning`、`intermittent` 等表达涉及 frequency / recurrence / pattern，而不仅仅是 temporal extent。

Frequency / recurrence semantics 在 R1D 中保持为未来工作，**MUST NOT** 因为了复用 Interval 而被隐式压缩成 Interval 语义。

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

PBDL 类型系统尚未冻结。

**TODO：**

- 基本类型
- 结构化类型
- 可选性
- 多重性
- 引用类型
- 术语绑定值
- 类型兼容规则
- 是否存在类型转换以及相应规则

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

Subject 的具体字段、隐私表示、外部标识符绑定方式与 surface syntax 仍为 **TODO**。

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

Behavior 的具体字段、行为类型词表、trigger / symptom 模型、Provenance / Evidence 的 surface 结构、frequency / recurrence 模型和语法仍为 **TODO**。

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

历史 `Preference.associated_behavior` 所表达的“偏好与行为之间存在关联”继续保留兼容价值。

规范性方向是显式 entity reference 或 Relation，而不是依赖自由文本字符串标签。

如果旧输入使用字符串标签表达 `associated_behavior`，在进入规范化语义之前，该标签 **MUST** 被解析到恰好一个 Behavior identity；无法解析或存在歧义时，该引用无效。

R1B 不冻结 `associated_behavior` 最终采用专用引用字段还是统一 Relation，也不冻结具体 Relation type。

每个 canonical Preference instance **MUST** 实际具有至少一条 provenance linkage，使下游能够判断该 Preference 是直接表达还是外部推断所得。

直接表达与推断出的 Preference 可以具有相同的 preference category 与 preference value，但其 provenance semantics **MUST** 保持可区分，不得仅依赖自然语言 note 来判断。

### 11.2 Preference temporal semantics

Preference **MAY** 具有 semantic temporal extent，用于描述该 Preference 的适用时间范围。

Preference 的表达时间、记录时间、抽取时间或生成时间属于 Provenance time；这些时间 **MUST NOT** 自动替代 Preference 的 applicability time。

Preference 缺少 semantic temporal information **MUST NOT** 被解释为永久偏好。

不同时期的不同 Preference 信息可以作为不同 Preference instances 共存，例如某一时期拒绝注射、另一时期接受注射。

历史 Preference 正式字段表虽然没有独立 temporal 字段，但 v1 Core **MAY** 表达 Preference temporal applicability，以避免把可随时间变化的偏好误解为永久状态。

Preference 的具体字段、偏好类型词表、取值模型、confidence surface、Provenance / Evidence 的具体结构、frequency / recurrence 模型和语法仍为 **TODO**。

## 12. Context

Context 是 PBDL-Core 的候选核心概念，用于承载解释 Behavior 或 Preference 所需的上下文信息。

上下文模型、作用域规则、允许的维度、继承规则和语法仍为 **TODO**。

## 13. Evidence 与 Provenance

R1C 冻结 Provenance 与 Evidence 的最小语义边界。

### 13.1 Provenance

Provenance 回答：

> “这条 Behavior / Preference 信息是怎么来的？”

Provenance 描述信息的来源与产生路径。其语义 **MUST** 足以让下游判断该信息来自什么来源或产生方式，并能够区分来源直接描述的信息与外部推断得到的信息。

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

同一个 Behavior 或 Preference **MAY** 具有多条 provenance linkage，例如患者自述、EHR 记录与设备观测共同支持同一项结构化语义。

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

R1C 不冻结 Evidence 的具体字段、identity requirement、嵌套方式或外部引用格式。

### 13.2.1 Provenance time boundary

Provenance 可以包含报告、记录、抽取、观测或生成发生的时间信息。

这类 Provenance time **MUST NOT** 自动承担 Behavior / Preference / Relation 的 semantic temporal extent。

同一条信息的 semantic time 与 provenance time 可以不同，也可以只提供其中之一。

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

R1C 不删除 `evidence_source` 或 `source_type` 的历史兼容意义，也不冻结它们最终对应的 surface field。

### 13.6 Confidence boundary

confidence **MUST NOT** 成为所有 Preference 的强制属性。

DIRECT self-report **MUST NOT** 被迫赋予模型式 confidence。

如果未来 confidence 用于 INFERRED information，其语义 **MUST** 能够说明：

- confidence 由谁或什么系统生成；
- confidence 衡量什么；
- confidence 对应哪个 inference process / model / analytic process。

R1C 不冻结 confidence 的字段名、数值范围、算法、校准方式或阈值。

历史 `Preference.confidence_score` 因此继续保留为待细化概念，但不得被解释为所有 Preference 的必需 Core 属性。

### 13.7 Provenance identity

R1C **不要求** Provenance 自身具有独立的 document-local identity。

当前冻结的最小引用需求是 Behavior / Preference 指向或携带足够的 provenance information；目前没有 Core 场景要求其他实体稳定引用某个 Provenance instance。

未来若共享 provenance、provenance chaining、Evidence 引用或其他明确使用场景需要稳定引用 Provenance，可在后续设计轮次重新冻结 identity requirement。

Provenance 的具体 Schema、field names、嵌套结构与 serialization 仍为 **TODO**。

## 14. Relations

Relation 用于在两个允许作为 Relation endpoint 的 PBDL semantic entities 之间显式表达语义联系。

R1B 冻结 Relation 的最小语义组成：

- source endpoint
- target endpoint
- relation type concept

这些是抽象语义要求，不冻结具体 surface field name、JSON field 或 DSL syntax。

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

- concrete temporal fields；
- temporal serialization；
- normative relation vocabulary；
- derived relation strength；
- directionality details；
- syntax。

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

跨文档 identity / reference protocol、frequency / recurrence、具体 temporal field、exact date/time serialization、partial-date representation details、Provenance / Evidence 的具体 Schema、confidence surface、trigger / symptom、术语词表、Context 详细结构和 Constraint 模型仍为 **TODO**。

## 17. 规范化表示

规范化表示目前尚未冻结到字段级。

[`schema/pbdl-v1.schema.json`](schema/pbdl-v1.schema.json) 当前只是合法的 JSON Schema Draft 2020-12 占位文件，**MUST NOT** 被解释为已经冻结最终 PBDL 字段模型。

**TODO：** 定义规范化序列化格式、必要时的排序或归一化规则、字段名称以及往返转换要求。

## 18. 校验模型

校验架构尚未冻结。

未来的校验模型预计至少需要区分结构合法性与语义合法性，但具体分层、Validator 行为、严重级别模型和错误码仍为 **TODO**。

R0 不定义 Validator 实现。

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

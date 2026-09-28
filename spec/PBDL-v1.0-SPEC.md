# PBDL 1.0 规范

**状态：** 草案
**目标版本：** PBDL 1.0


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

`Behavior` 与`Preference` 是 PBDL-Core 的主要研究对象。

Treatment Pathway（治疗路径）**不属于** PBDL-Core；未来可由扩展或上层应用定义。

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

只有在相关语言构造已经被正式定义时，这些规范性要求才具有确定含义。任何标记为`TODO` 的未决语法或字段名，都不得因为示例、占位文件或实现习惯而被视为已经标准化。

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

PBDL-Core 定义以下四类核心语义对象：

- Subject：Behavior 与 Preference 所描述的主体，以及文档内主体引用的稳定锚点。
- Behavior：对某个 Subject 已描述或已断言的行为、未发生行为或行为状态的表示。
- Preference：对某个 Subject 已表达或已推断的倾向、选择、优先级、厌恶或偏好的表示。
- Relation：在允许的端点类型之间显式表达语义联系的 Core 构造。

`Context` 用于对`Behavior` /`Preference` 的语义解释提供情境限定，但不作为具有独立身份的可引用一级 Core 实体。其规范归属为`Behavior` /`Preference` 下的嵌入式限定信息，具体字段、coded/text 值结构、局部`provenance` 与相等性见 §8.5、§12 与 §17.4.5。`Provenance` 与`Evidence` 的语义边界、字段、附着方式以及`SourceDescriptor` /`GeneratorDescriptor` /`Evidence` 的具体结构见 §13 与 §17.8。JSON Schema 与 DSL 语法仍留待后续定义。

### 5.1 文档与 Subject 绑定

一个 PBDL 文档 **MUST** 至少包含一个 Subject。

一个 PBDL 文档 **MAY** 包含多个 Subject。

每个 Behavior **MUST** 绑定到且仅绑定到一个 Subject。

每个 Preference **MUST** 绑定到且仅绑定到一个 Subject。

§17 定义了规范文档与对象的字段归属、`EntityId` 词法约束以及规范引用对象结构。DSL 表层语法仍未定义。即使未来表层语法在单`Subject` 文档中允许省略显式主体引用，规范语义仍 **MUST** 能够确定该`Behavior` 或`Preference` 唯一对应的`Subject`。

### 5.2 核心对象身份要求

核心对象的最小身份要求如下：

| Core 构造 | v1 Core 身份要求 | 理由 |
|---|---|---|
| Subject | **MUST** 具有身份 | Behavior 与 Preference 需要稳定绑定到明确主体 |
| Behavior | **MUST** 具有身份 | Relation 以及历史`associated_behavior` 兼容方向需要稳定引用 Behavior 实例 |
| Preference | **MUST** 具有身份 | Relation 需要稳定引用 Preference 实例 |
| Relation | **v1 Core 最小模型不要求身份** | 不允许 Relation 作为 Relation 端点，也没有已定义的 Core 构造需要引用 Relation 本身 |

`Relation` 不要求身份并不禁止未来扩展为`Relation` 提供标识符；这类能力不属于当前 Core 的最小要求。

### 5.3 标识符范围与稳定性

Subject、Behavior 与 Preference 的 实体标识符 **MUST** 在其所属 PBDL 文档 内唯一。三类实体共享同一个 文档内身份命名空间；同一个 identifier **MUST NOT** 在同一文档中被另一个 Subject、Behavior 或 Preference 重复使用。

v1 Core **MUST NOT** 强制要求全局 UUID、URI 或其他跨系统全局标识符。

在同一 PBDL 文档 的生命周期内，用于内部引用的 identifier **MUST** 保持足够稳定，以保证已建立的内部引用不会因为对象重排而改变指向。

数组位置、列表序号或其他仅由容器位置推导出的值 **MUST NOT** 作为规范性 entity 身份。

跨文档身份与跨文档引用协议不属于当前规范范围，保留为未来工作。

### 5.4 显示标签不是实体身份

显示标签、类型名称、类别名称或术语代码本身 **MUST NOT** 自动充当 实体实例 身份。

例如，`medication_nonadherence` 如果表示一个 Behavior type，则它描述的是“该 Behavior 属于什么类型”，而不是“这是哪个 Behavior 实例”。

同样，`behavior_type`、`preference_category` 与 `Relation` 类型 概念 都不是相应实体实例的身份。

### 5.5 引用模型

Core引用**MUST** 在其声明的引用范围 内解析到恰好一个实体。

在 v1 Core 最小模型中，内部引用范围 为当前 PBDL 文档。

无法解析到任何实体的引用是无效的。

能够解析到多个实体的 歧义引用是无效的。

Behavior 与 Preference 对 Subject 的绑定 **MUST** 使用可解析到明确 Subject身份的引用语义，不得依赖模糊显示标签。

Relation 的 source 端点 与 target 端点 **MUST** 使用 entity 引用，不得使用未解析的自由文本标签作为规范性引用。

### 5.6 `Relation` 端点矩阵

PBDL-Core`Relation` 允许以下最小端点集合：

| 来源端点 | 目标端点 | Core v1 |
|---|---|---|
| Behavior | Behavior | 允许 |
| Behavior | Preference | 允许 |
| Preference | Behavior | 允许 |
| Preference | Preference | 允许 |
| Subject | Behavior / Preference / Subject | 不允许作为 Core `Relation` 端点 |
| Relation | Any Core 实体 | 不允许 |
| Any Core 实体 | Relation | 不允许 |

`Subject` 是`Behavior` /`Preference` 的稳定归属锚点，而不是通用关系图节点。若未来出现必须直接表达`Subject` 层级关系的明确使用场景，可由后续规范扩展。

PBDL-Core 不允许`Relation→Relation`，以避免在没有明确使用场景时引入高阶关系、关系注释图或关系实体化语义。

§17 定义了`EntityId` 词法形式与`SubjectRef` /`CoreEntityRef` /`ActorRef` 的规范引用表示。DSL 语法与 JSON Schema 仍为 **TODO**。

### 5.7 时间语义基础

PBDL-Core 的最小时间语义用于回答：

- Behavior 在什么时候发生、持续或适用；
- Preference 在什么时候适用；
- Relation 在什么时候成立或适用。

PBDL-Core 区分两类不同的时间语义：

- **语义时间**：描述 Behavior / Preference / Relation 本身发生、成立或适用的时间；
- **Provenance 时间**：描述相关信息何时被报告、记录、抽取、观测或生成。

语义时间 与 Provenance 时间 **MUST NOT** 被视为同一个时间概念。记录时间 **MUST NOT** 自动替代 Behavior / Preference / Relation 的 语义时间。

例如，患者在 9 月 20 日报告“上周漏服了三次药”时：

- “上周”属于 Behavior 语义时间；
- “9 月 20 日”属于 provenance / reporting time。

Behavior、Preference 与 Relation **SHOULD** 基于同一套 Core temporal abstraction 表达 语义时间范围，但三者使用该 abstraction 的语义角色不同。

#### 5.7.1 Instant

Instant 表示一个时间点。

`Instant` 可以具有不同的来源精度，例如只精确到年、月、日，或更高精度的具体时刻。具体日期时间序列化形式见 §8.2 的 `TemporalValue` 词法定义。

#### 5.7.2 Interval

Interval 表示一个时间区间。

Interval 可以具有：

- start 与 end；
- 已知 start、未提供 end；
- 未提供 start、已知 end。

一个 Interval **MUST** 至少具有一个有效边界。两个边界都不存在时，该结构 **MUST NOT** 被解释为有意义的 时间范围。

单边界 `Interval` 中缺失的另一侧边界只表示该边界未提供。

缺失的 边界 **MUST NOT** 自动解释为：

- 永久持续；
- 一直持续到现在；
- 一直持续到未来；
- 从无限过去开始；
- 数学意义上的 unbounded interval。

如果未来需要显式表达 ongoing、unbounded 或 known-open-ended 时间语义，应由后续规范单独定义；当前规范不定义这些语义。

如果 start 与 end 同时存在且能够比较，则 start **MUST NOT** 晚于 end。

#### 5.7.3 未提供语义时间

Behavior、Preference 或 Relation **MAY** 没有语义时间信息。

§5.7 不要求引入显式的 未知 token；缺少 时间信息 可以表示 语义时间 未提供。

缺少语义时间信息 **MUST NOT** 被解释为：

- 永久成立；
- 从出生至今；
- 当前仍成立；
- 始终如此；
- 反复发生；
- 时间不重要。

它只表示 规范语义 当前没有提供该项时间信息。

#### 5.7.4 时间精度保留

对时间信息进行 规范化 或其他规范化转换时，转换结果 **MUST** 保留来源实际支持的时间精度，并 **MUST NOT** 发明来源未提供的精度。

例如，来源只有“2026-09”时，规范化 **MUST NOT** 仅为了获得完整 timestamp 而将其伪造成“2026-09-01T00:00:00”。

同样，“2026 年” **MUST NOT** 被自动伪造成某一个具体日期。

§8.2 定义 partial-date / date-time 的规范词法形式，并通过词法形式保留 year / month / date / minute / second / fractional-second 精度。

#### 5.7.5 时区信息保留

如果来源未提供 timezone / offset，规范化 **MUST NOT** 凭空声明一个具体 timezone / offset。

如果来源已经提供 timezone / offset，规范表示 **MUST** 能够保留该来源提供的信息。

当前规范不另行定义 timezone / offset 序列化；§8.2 定义可选 offset / zone suffix，并继续禁止凭空补造来源未提供的 timezone / offset。

#### 5.7.6 相对时间

相对 temporal expression 可以出现在来源中，例如：

- 昨天；
- 上周；
- 治疗后三天；
- 出院后一个月。

如果 相对 temporal expression 保留在规范语义表示 中，它 **MUST** 具有足以解释其含义的明确 锚点。

或者，在形成规范PBDL语义之前，上游转换已经将其解析为足够明确的 绝对 / anchored temporal expression。

无法确定 锚点 的裸相对时间 **MUST NOT** 被假装成唯一确定的 绝对 时间范围。

当前规范不定义 相对-time DSL 语法。

#### 5.7.7 Frequency / recurrence 与 时间范围 是不同维度

`Behavior` frequency / recurrence 的最小语义边界见 §10.5。

语义时间范围 回答“Behavior 在什么时候发生、持续或适用”；frequency / recurrence 回答“某类 Behavior occurrence 以什么重复模式或频度发生”。

二者 **MUST** 保持可区分，并 **MAY** 同时存在。

例如，“2026 年 1 月至 3 月，每周漏服两次”中：

- “2026 年 1 月至 3 月”属于 §5.7 语义时间范围；
- “每周漏服两次”属于 §10.5 Behavior frequency / recurrence 信息。

“持续三个月” **MUST NOT** 被解释为“每三个月一次”；“每天”也 **MUST NOT** 被当作一个 Interval。

当前规范不把 recurrence 语义扩展到 `Preference` 或 `Relation`，也不定义 RRULE、cron-like language、calendar engine 或具体 temporal / recurrence 序列化。

### 5.8 `Annotation` 语义

`Annotation` 用于承载轻量的人类可读补充信息。

Annotation 用于为某个规范语义对象/ assertion 提供人类可读的补充说明、澄清或解释性文本。它是 auxiliary 人类可读的 信息，而不是规范机器语义 的唯一载体。

Annotation **MAY** 用于保留：

- 对 Behavior 的额外说明；
- 对 Preference 的人类可读补充；
- 来源中无法完全结构化、但值得保留的说明；
- 人工或外部系统产生的解释性备注。

`Annotation` 的最小规范字段、附着位置与基数见 §17，`Text` 词法约束见 §8.1。作者/生成者表示、JSON Schema 与 DSL 语法仍留待后续定义。

#### 5.8.1 `Annotation` 不是机器语义的后门

如果某项信息对身份、引用、`Behavior` 类型、`Preference` 值、时间语义、频率、`Context`、`Relation` 类型、关系方向、`Provenance`、DIRECT / INFERRED 或因果/非因果区分等规范机器语义具有规范性意义，符合规范的表示 **MUST NOT** 只把它藏在自由文本 `Annotation` 中。

如果某项语义已有 结构化规范机制，Annotation **MAY** 补充解释，但 **MUST NOT** 替代该 结构化 机制。

Conforming 使用方 **MUST NOT** 被迫通过自然语言理解 note / Annotation 才能确定对象的核心 机器语义。

#### 5.8.2 `Annotation` 本身不创建语义断言

Annotation 文本自身 **MUST NOT** 自动创建新的 Behavior、Preference、Relation、Context、因果 claim、risk 结果、recommendation 或其他 派生 / 应用 结果。

例如 Behavior 已结构化为“患者漏服药物”，而 Annotation 写“可能因为工作压力较大”，该文本本身 **MUST NOT** 自动使 规范语义 获得 来源归因的 reason、因果 Relation、Context 或 派生 clinical conclusion。

若 Annotation 中的内容需要成为 机器-consumable 语义，它必须通过已有适用的 结构化语义机制 表达，并遵守相应 provenance / derivation 规则。

#### 5.8.3 `Annotation` 的派生与来源类别

`Annotation` 至少区分以下 provenance / derivation 情况，但当前规范不定义对应的表层 enum：

1. **来源描述/来源承载的文本**：来源本身已经包含该说明；忠实保留或轻度规范化时，`Annotation` **MAY** 具有 DIRECT provenance 语义。
2. **人工撰写的解释性 annotation**：人工标注者或审阅者额外增加的解释；它 **MUST** 与来源描述的内容保持来源可区分，**MUST NOT** 冒充患者、临床人员或原始来源直接说过的话。
3. **模型/分析过程生成的解释性 annotation**：模型、规则或分析过程在来源未表达的基础上生成新解释；该新增内容 **MUST** 保持 INFERRED derivation 语义，并 **MUST NOT** 标成 DIRECT 来源文本。

是否使用 LLM / NLP 本身不决定 DIRECT / INFERRED。

如果来源明确写“因为恶心，患者停止服药”，LLM 仅忠实改写为“患者将恶心描述为停药原因”，且没有新增来源不存在的解释，该 `Annotation` **MAY** 继续属于 DIRECT、忠实于来源的表示。

如果 LLM 新增“可能因为患者对药物存在恐惧”，而来源未表达该解释，则新增部分属于 INFERRED。

#### 5.8.4 `Annotation` 不等同于`Provenance` 或`Evidence`

Annotation **MUST NOT** 替代 Behavior、Preference 或 Relation assertion 的 必需 Provenance 要求。

“来源是谁”“如何产生”“DIRECT / INFERRED” **MUST NOT** 仅通过 note 文本表达并要求下游 NLP 猜测。

Annotation 与 Evidence 也不是同一概念：

- Evidence 回答“有什么材料支持 / 承载这项信息”；
- Annotation 回答“有什么人类可读的补充说明”。

将 来源文本 复制到 Annotation 中 **MUST NOT** 自动使该 Annotation 成为规范性 Evidence 对象；Evidence material 也不自动成为 Annotation。

§5.8 不设计 quote、source span、文档 offset 或 evidence excerpt schema。

#### 5.8.5 `Annotation` 不建立因果关系或`Relation`

Annotation 中出现`because`、`due to`、因、导致、所以、可能因为等语言 **MUST NOT** 仅凭自由文本内容自动建立规范因果 语义。

来源归因的理由继续使用 §10.3 语义；模型生成的解释在适用时继续保持 INFERRED derivation。

同样，Annotation 文本 **MUST NOT** 自动创建规范Relation。

如果 Preference–Behavior 关联、`Relation` 类型、方向性 或 端点 需要 机器语义，必须显式使用 §14 Relation 机制，而不是只隐藏在 Annotation 中。

#### 5.8.6 `Annotation` 不替代时间、频率或`Context` 语义

如果 Annotation 中的“最近”“上周”“经常”“每天”“工作时”等信息需要成为规范机器语义，它们必须分别遵守 §5.7 temporal、§10.5 frequency / recurrence 与 Context 语义。

Annotation **MUST NOT** 作为这些 结构化语义的唯一规范性表达。

#### 5.8.7 `Annotation` 不创建派生分析结果或校验器状态

Annotation 中的“严重不依从”“未来风险很高”等文本 **MUST NOT** 自动使 PBDL-Core 获得 risk tag、clinical severity、adherence score、prediction 或 recommendation。

这些仍属于 来源描述的语义或 Core 外部 派生 / 应用层，具体取决于实际来源与结构化建模。

Annotation **MUST NOT** 用于重新引入 旧版`Behavior.validity_flag`，也 **MUST NOT** 替代 校验 error、warning、schema violation 或其他 validator / report output。

#### 5.8.8 `Annotation` 的身份与图结构边界

Annotation 不要求独立 身份，不加入 Subject / Behavior / Preference 文档内身份命名空间，也不是 Relation 端点。

§5.8 不新增 Annotation→Annotation、Annotation→Relation、Relation→Annotation 或其他 Annotation graph edge。

Annotation 是附着于现有规范语义对象/ assertion 的 lightweight auxiliary 信息，而不是新的 具有身份的 Core graph entity。

#### 5.8.9 不包含隐藏思维链

PBDL-Core **MUST NOT** 要求模型暴露、存储或交换 hidden chain-of-thought、private reasoning trace、token-level reasoning、internal scratchpad 或 hidden 模型 deliberation 作为规范性 Annotation 内容。

外部系统 **MAY** 提供 concise 解释、rationale summary 或 结果-oriented annotation，但其 source / generator / derivation **MUST** 能与 来源承载的 text 保持可区分。

旧版`reasoning_note` 中的 “reasoning” **MUST NOT** 被解释为 PBDL-Core 要求保存模型私有推理过程。

#### 5.8.10 缺少`Annotation` 与结构化语义优先级

Behavior / Preference **MAY** 没有 Annotation。

缺少 Annotation **MUST NOT** 被解释为没有 Context、没有 Provenance、没有 Evidence、没有解释、assertion 已完全理解或 assertion 不需要 provenance。

它只表示没有提供额外 人类可读的 annotation。

如果 Annotation 与 结构化 规范语义 冲突，conforming 使用方 **MUST NOT** 仅根据 Annotation 静默覆盖 结构化 语义。

此类冲突需要由上游修正、校验 / review 或其他明确机制处理；§5.8 不设计 conflict resolver。

## 6. 词法结构

词法结构尚未完整定义。

**TODO：**

- 字符集要求
- 空白符规则
- 注释规则
- 标识符
- 字面量
- 转义规则
- 保留字

除非由后续规范明确定义，否则任何 token、keyword、delimiter 或 literal 语法都不具有规范性。

## 7. 语法

当前语法仍有意保持不完整。

当前语法占位文件位于 [`grammar/pbdl.ebnf`](grammar/pbdl.ebnf)。

**TODO：** 定义 Patient / Subject、Behavior、Preference、Context、Evidence / Provenance 与 Relation 的具体语法。

## 8. 类型系统

§17 定义了规范对象模型的最小结构类型、必需/可选字段、基数、类型化引用归属与命名嵌套语义类型。

`VersionToken`、`EntityId`、`SubjectRef`、`CoreEntityRef`、`ActorRef`、`ExternalActorRef`、`DerivationKind`、`SourceDescriptor`、`GeneratorDescriptor`、`Evidence` 与引用表示的具体规范形式见本章与 §17。

`Text`、`TemporalValue`、`Coding` 与`Confidence` 的规范定义分别见本章、§15 与 §17。

### 8.1 Text

规范 Text 是 JSON-compatible Unicode string。

Text **MUST**：

- decode 为有效 Unicode scalar-value sequence；
- 至少包含一个不属于 Unicode White_Space property 的 code point。

因此空字符串与仅由 whitespace 组成的字符串 **MUST NOT** 作为规范Text。

Text **MUST NOT** 被 规范化 自动：

- trim；
- case-fold；
- Unicode 规范化；
- 解释为 Coding / 术语 token。

规范 Text 相等性 使用**精确 Unicode scalar-value sequence 相等性**。

因此 canonically distinct code-point sequences 即使视觉上相似，也 **MUST NOT** 在没有额外明确 规范化 规范 时被自动视为相等。

该规则使 `Evidence.content` 与 `Annotation.text` 无法用空值或仅空白字符的值伪造“存在内容”。

当前规范不定义 Markdown、HTML、rich-text 或自然语言本体语义。

### 8.2 TemporalValue

规范 TemporalValue 是 constrained string。它通过 词法形式 本身保留 来源支持的 temporal precision 与 timezone / offset 信息。

TemporalValue **MUST** 精确符合以下一种 规范。

#### 8.2.1 日期族形式

Year precision：

    YYYY

其中 YYYY 为 0001..9999。

Month precision：

    YYYY-MM

其中 MM 为 01..12。

Date precision：

    YYYY-MM-DD

其中 date **MUST** 是 proleptic Gregorian calendar 中真实存在的日期。

Date-family value **MUST NOT** 带 time、offset 或 zone suffix。

#### 8.2.2 日期时间形式

Minute precision：

    YYYY-MM-DDTHH:MM<zone?>

Second precision：

    YYYY-MM-DDTHH:MM:SS<zone?>

Fractional-second precision：

    YYYY-MM-DDTHH:MM:SS.F<zone?>

其中：

- HH = 00..23；
- MM = 00..59；
- SS = 00..59；
- leap-second lexical value 60 不属于当前规范；
- F 为 1..9 位 decimal digits，其位数属于 preserved precision 信息；
- calendar date **MUST** 有效。

`<zone?>` 可以省略，或采用以下一种形式：

    Z
    +HH:MM
    -HH:MM
    [ZoneToken]
    Z[ZoneToken]
    +HH:MM[ZoneToken]
    -HH:MM[ZoneToken]

数值型 offset 范围为 -14:00..+14:00；绝对值为 14 小时时 minute **MUST** 为 00。

ZoneToken **MUST** 为 非空、case-sensitive token，字符限于 ASCII letters / digits /`.` /`_` /`+` /`-` /`/`，并 **MUST NOT** 含 whitespace、`[` 或`]`。

Bracketed ZoneToken 只用于保留来源提供的 timezone identifier，例如`[America/Los_Angeles]`；PBDL-Core **MUST NOT** 从 ZoneToken 名称自行推导未提供的 数值型 offset。

来源未提供 timezone / offset 时，规范化 **MUST NOT** 添加`Z`、数值型 offset 或 ZoneToken。

来源提供 数值型 offset、zone identifier 或二者时，规范表示 **MUST** 保留来源实际提供的信息。

#### 8.2.3 无效形式

以下不属于规范TemporalValue：

- time-only value；
- date-only value 携带 timezone / offset；
- impossible Gregorian date；
- malformed month / day / clock component；
- 未解析 相对 phrase；
- 为补齐精度而伪造的日期 / time / timezone。

未解析 相对 temporal expression 继续遵守 §5.7 / §17：必须在规范化 前可靠解析，或只作为 Evidence / Annotation 保真保存，**MUST NOT** 伪装成 TemporalValue。

#### 8.2.4 精度

Temporal precision 完全由 词法形式 保留：

-`2026` ≠ year expanded to a date；
-`2026-09` ≠ first day of September；
- minute precision ≠ second precision；
-`.1`、`.10` 与`.100` 保留不同 fractional precision。

规范化 **MUST NOT** 为了统一时间戳形状而添加来源未提供的组成部分。

#### 8.2.5 `TemporalValue` 规范信息相等

TemporalValue规范相等性 使用 **规范信息相等**，不是 physical instant equivalence。

两个 TemporalValue 只有在完整 lexical string 精确相同时才 语义等价。

因此：

    2026-09-27T10:00Z

与：

    2026-09-27T18:00+08:00

即使可能表示相同 physical instant，也 **MUST NOT** 作为规范信息相等，因为 preserved local lexical value 与 offset 信息 不同。

同样：

-`Z` 与`+00:00` 不 规范信息相等；
- timezone absent 与 timezone present 不 规范信息相等；
- ZoneToken presence / value 不同不 规范信息相等；
- precision 不同不 规范信息相等。

实现 **MAY** 提供独立的 physical-instant 比较 operation，但该 operation **MUST NOT** 改写或替代 规范信息相等，也 **MUST NOT** 为缺失 offset / timezone 的值发明时区。

#### 8.2.6 `Interval` 校验的最小时间可比性

Interval 边界 顺序 使用保守的 “definitely later than” 判断。

Date-family values 可以在 proleptic Gregorian calendar 上按其 precision 对应的可能日期范围比较。

例如：

-`2026-10` 的最早可能日期晚于`2026-09-15` 的最晚可能日期，因此作为 start/end 时可判定 start later than end；
-`2026-09` 与`2026-09-15` 的可能范围重叠，因此不能据此判定 start later than end，也 **MUST NOT** 发明具体 day 来强行比较。

Date-time values：

- 两者都有 显式 数值型 offset 时，可以基于 offset 将各自 precision range 映射到 physical instant range后进行 顺序 check；
- 两者都没有任何 offset / ZoneToken 时，可以按 local civil date-time precision range比较；
- 一方有 数值型 offset、另一方没有时，视为不可比较；
- 只有 bracketed ZoneToken 而无 数值型 offset 时， 不要求 timezone database / DST resolution，因此不据此做 physical 顺序 rejection；
- date-family 与 date-time-family 之间不做强制 顺序 比较。

只有当 start 的**最早可能值**仍严格晚于 end 的**最晚可能值**时，才必须判定 start later than end。

如果 ranges 重叠或当前信息不足以建立可比较 顺序，validator **MUST NOT** 通过补造 precision / timezone 来拒绝该 Interval。

本节定义最小 有效性 边界，不要求完整 date arithmetic engine。

### 8.3 BehaviorFrequency

`BehaviorFrequency` 是明确的带判别标记联合类型：

    BehaviorFrequency =
        ObservedCountFrequency
        | RateFrequency
        | RecurrenceFrequency
        | QualitativeFrequency

四种 变体 **MUST NOT** 通过 arbitrary string 合并为同一个 frequency 字段。

所有 变体 **MAY** 具有：

    provenance? : Provenance[1..*]

该局部 `provenance` 字段继续完全遵守 §17.10 的“继承当前完整集合、完全覆盖、禁止叠加合并、冗余时省略”规则。

#### 8.3.1 QuantitativeFrequencyPrecision

ObservedCountFrequency、RateFrequency 与 RecurrenceFrequency 使用 必需 precision token：

    "exact" | "approximate"

`"exact"` 表示规范数值型 / recurrence statement 未携带来源中的 近似 qualifier。

`"approximate"` 表示来源明确表达约数、近似频率或近似 recurrence cadence。

Precision token **MUST NOT** 被替换成 Confidence，也 **MUST NOT** 被 使用方 解读为 统计 confidence level。

#### 8.3.2 FrequencyPeriod

规范 FrequencyPeriod：

    FrequencyPeriod {
        value : positive integer
        unit  : "day" | "week" | "month" | "year"
    }

value **MUST** >= 1。

§8.3–§8.4 不加入`"hour"`：当前 stress cases 不需要 hour-level regimen engine；day-part recurrence 已覆盖当前规范 time-of-day 要求。需要 hour-level recurrence 的来源在当前规范 **MUST NOT** 被偷偷改写成 day fraction。

§8.3–§8.4 不允许 non-integer period value。来源若表达当前 规范 无法无损表示的非整数 period，规范化器 **MUST NOT** 舍入 / rescale / 发明等价 duration；原始信息可由 Evidence / Annotation 保真，并等待 未来扩展。

`month` /`year` 表示 calendar period 概念，**MUST NOT** 被自动换算为固定天数。

FrequencyPeriod 相等性 要求 value 数值精确相等且 unit token 相同。

#### 8.3.3 ObservedCountFrequency

规范结构：

    ObservedCountFrequency {
        kind        : "observed_count"
        count       : non-negative integer
        precision   : "exact" | "approximate"
        window?     : Interval
        provenance? : Provenance[1..*]
    }

count 必需，且 **MUST** >= 0。

count = 0 合法，表示来源明确支持在所述 observation语义下 发生次数 为零；它 **MUST NOT** 被解释为 missing frequency。

window 可选。

允许 count-only 表示。例如来源只说“漏服了 3 次”，可以 canonicalize 为 count = 3、window absent，而 **MUST NOT** 发明 observation window。

window 存在时使用 Interval；window 是 observation /引用window，不是 rate denominator，也 **MUST NOT** 自动把 count 转成 rate。

#### 8.3.4 RateFrequency

规范结构：

    RateFrequency {
        kind        : "rate"
        value       : non-negative finite number
        period      : FrequencyPeriod
        precision   : "exact" | "approximate"
        provenance? : Provenance[1..*]
    }

value、period、precision 必需。

value **MUST** >= 0 且 有限。

RateFrequency 的含义是平均 / 频率值 “value occurrences per period”。

period **MUST** 显式存在；只有一个裸`value = 2` **MUST NOT** 被解释为 rate。

观测的 count **MUST NOT** 因具有 window 自动 canonicalize 为 RateFrequency。

#### 8.3.5 RecurrenceFrequency

规范结构：

    RecurrenceFrequency {
        kind              : "recurrence"
        period            : FrequencyPeriod
        precision         : "exact" | "approximate"
        times_per_period? : positive integer
        days_of_week?     : Weekday[1..*]
        day_part?         : DayPart
        provenance?       : Provenance[1..*]
    }

period 与 precision 必需。

times_per_period 若存在，**MUST** >= 1。

times_per_period 缺失只表示来源未提供每 period 的 发生次数，**MUST NOT** 默认为 1。

Weekday规范tokens：

    "mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun"

days_of_week 若存在：

-集合**MUST** 非空；
- 重复项 weekday **MUST NOT** 出现；
- 集合顺序 **MUST NOT** 具有 语义含义；
- period **MUST** 精确为 { value: 1, unit: "week" }；
- times_per_period **MUST** 缺失，以避免同时存在两个 competing occurrence-count mechanisms。

days_of_week 缺失表示未提供 weekday 计划，**MUST NOT** 表示 every weekday。

DayPart规范tokens：

    "morning" | "afternoon" | "evening" | "night"

day_part 可选；缺失表示未提供 day-part qualifier。

DayPart 是 来源描述的 categorical time-of-day 概念，§8.3–§8.4 **MUST NOT** 为这些 token 偷偷绑定统一 clock-hour thresholds。

day_part 可与 daily recurrence 或 weekly days_of_week recurrence 共存；§8.3–§8.4 不引入 具体 clock-time 计划、RRULE 或 cron 语义。

RecurrenceFrequency 表达 重复模式，**MUST NOT** 自动生成 具体 观测发生记录 timestamps。

#### 8.3.6 QualitativeFrequency

规范结构：

    QualitativeFrequency {
        kind        : "qualitative"
        value       : QualitativeFrequencyToken
        provenance? : Provenance[1..*]
    }

QualitativeFrequencyToken 为以下规范lowercase tokens：

    "never"
    "rarely"
    "occasionally"
    "sometimes"
    "often"
    "frequently"
    "usually"
    "intermittently"
    "always"

这些 token 表示 来源描述的 定性 frequency 概念。

Core **MUST NOT** 为任一 token 绑定 数值型 阈值、probability、rate、percentage 或 recurrence interval。

Token 列表顺序 **MUST NOT** 被解释为规范性的 数值型 scale 或 clinical severity 顺序。

`"never"` /`"always"` 继续受 所属对象 temporal / Context 范围 限定；范围 缺失 **MUST NOT** 自动升级为 lifetime 范围。

#### 8.3.7 `BehaviorFrequency` 内容相等

`BehaviorFrequency` 的**语义内容相等**明确忽略 `BehaviorFrequency.provenance`。

不同 `kind` 的变体 **MUST NOT** 语义等价。

`ObservedCountFrequency` 的内容相等要求：

- `count` 相同；
- `precision` token 相同；
- `window` 同时缺失，或 `window` 的时间内容相等。

这里 `window` 的时间内容相等只比较 `Interval.kind` / `start` / `end`，其中 `TemporalValue` 按规范信息相等比较，并忽略 `window.provenance`。

`RateFrequency` 的内容相等要求：

- `value` 按有限数学数值比较且语义相等；
- `period` 相等；
- `precision` token 相同。

`RecurrenceFrequency` 的内容相等要求：

- `period` 相等；
- `precision` token 相同；
- `times_per_period` 同时缺失，或数值相同；
- `day_part` 同时缺失，或 token 相同；
- `days_of_week` 同时缺失，或作为无重复 token 的集合相等；顺序不影响相等性。

`QualitativeFrequency` 的内容相等要求 `value` token 完全相同。

当前规范不定义 `BehaviorFrequency` 的模糊相似度。

#### 8.3.8 `BehaviorFrequency` 完整限定信息相等

完整限定信息相等与频率内容相等是两个不同层级。

完整 `BehaviorFrequency` 相等 **MUST** 同时满足：

1. §8.3.7 的内容相等；
2. `BehaviorFrequency` 的有效来源集合按 §17.10 的 `Provenance` 语义相等规则判定为语义等价；
3. 若 `ObservedCountFrequency.window` 存在且具有独立的 `TemporalExtent.provenance`，则双方 `window` 的有效来源信息也必须语义等价。

因此，`provenance` 不属于频率**内容**，但属于完整规范限定信息。

### 8.4 PreferenceValue

`PreferenceValue` 是最小带标签联合类型：

    PreferenceValue =
        CodedPreferenceValue
        | TextPreferenceValue
        | BooleanPreferenceValue
        | NumericPreferenceValue

§8.3–§8.4 不新增 ordinal / strength、引用-valued、list / multi-select 变体。

#### 8.4.1 CodedPreferenceValue

    CodedPreferenceValue {
        kind  : "coded"
        value : Coding
    }

value 必需。

当适用的术语或 category 契约提供可靠且不丢失来源语义的 `Coding` 时，规范化器 **SHOULD** 使用 coded 变体，而不是仅为方便退化为自由文本。

如果没有可靠 binding，规范化器 **MUST NOT** 发明 Coding。

#### 8.4.2 TextPreferenceValue

    TextPreferenceValue {
        kind  : "text"
        value : Text
    }

value 必需，并遵守 §8.1 Text 契约。

Text 变体 用于来源保真：当 source preference value 无法可靠映射到 Coding、布尔 或 数值型语义时，**MAY** 使用 Text。

Text 变体 **MUST NOT** 成为 结构化语义backdoor。

如果规范性 category/value binding 明确要求某个可靠 coded value，规范化器 **MUST NOT** 仅为了避免 术语 mapping 而使用 Text。

使用方 **MUST NOT** 被迫通过 NLP 才能恢复本可可靠结构化的所有 PreferenceValue。

#### 8.4.3 BooleanPreferenceValue

    BooleanPreferenceValue {
        kind  : "boolean"
        value : boolean
    }

value 必需。

布尔 变体 只应在 Preference.category 的语义确实把 value 定义为 binary choice / 状态 时使用。

例如 category 表示 phone contact acceptance 时，value = false 可以表示“不希望电话联系”。

布尔 false 是一个真实 PreferenceValue，**MUST NOT** 被解释为 missing Preference；缺少 Preference assertion 也 **MUST NOT** 被解释为 false。

规范化器 **MUST NOT** 仅因为 旧版 string 看起来像`"yes"` /`"no"` 就在缺少 category / source语义support 时猜 布尔。

#### 8.4.4 NumericPreferenceValue

    NumericPreferenceValue {
        kind     : "number"
        operator : "eq" | "lt" | "lte" | "gt" | "gte"
        value    : finite number
        unit?    : Coding
    }

operator 与 value 必需。

value **MUST** 有限；NaN 与 ±Infinity 无效。

operator 保留 数值型 preference 的 比较 语义。

因此“等待时间不超过 30 分钟”需要 operator =`"lte"`，而不能只保存裸 number 30。

unit 可选，但若 source/category语义表示 dimensioned quantity 且 source 提供 unit，规范表示 **MUST** 保留该 unit。

unit 使用已有 Coding，§8.3–§8.4 **MUST NOT** 新增 arbitrary unit string type。

Unitless 数值型 合法，仅当：

- 来源明确表达 dimensionless number；或
- 适用的 `Preference.category` 语义契约明确定义该 `value` 为无量纲。

当 quantity 语义需要 unit 但来源未提供 unit 时，规范化器 **MUST NOT** 猜测 minutes、days、percent 或其他 unit。

#### 8.4.5 偏好强度与序数边界

§8.3–§8.4 不新增 preference-strength / ordinal 变体。

例如“强烈偏好居家管理”中：

- “居家管理”如果有可靠 Coding，可以进入 CodedPreferenceValue；
- “强烈” **MUST NOT** 在当前规范被发明成 ordinal number、Confidence 或 派生 preference-strength score。

需要保留的原始强度措辞可由 `Evidence` / `Annotation` 保真；未来若确有需要，应由专门的 preference-strength 规范另行定义。

#### 8.4.6 引用与列表边界

PreferenceValue 不包含 CoreEntityRef 变体。

旧版 / source 中 Preference 与 Behavior 的 关联 继续使用 §14 Relation，而 **MUST NOT** 通过 引用-valued PreferenceValue 绕回第二套 link 机制。

PreferenceValue 也不包含 通用 list / multi-select 变体。

如果来源表达多个可独立成立的 Preference assertions，规范化器 **MAY** 使用多个 Preference 实例；如果多值集合本身具有不可拆分语义而当前 union 无法无损表示，**MUST NOT** 发明 list 语义，可保留 来源材料并等待 未来扩展。

#### 8.4.7 `PreferenceValue` 相等性

`PreferenceValue` 的相等性由 `kind` 判别字段决定。

不同 `kind` **MUST NOT** 语义等价。

CodedPreferenceValue：

- 使用 §15 的 `Coding` 规范信息相等。

TextPreferenceValue：

- 使用 §8.1 的 `Text` 相等性。

BooleanPreferenceValue：

- 使用精确布尔值相等。

NumericPreferenceValue：

- `operator` token 必须相同；
- `value` 使用有限数学数值的精确相等；
- `unit` 同时缺失，或按 §15 的 `Coding` 规范信息相等判定为语义等价。

当前规范不定义 `PreferenceValue` 的模糊相似度。

#### 8.4.8 旧版`PreferenceValue` 迁移

旧版`Preference.preference_value` 迁移 **MUST** 保留 来源支持的 type 语义。

- source / binding 可靠支持 Coding → **MAY** 使用 coded；
- source/category 可靠支持 布尔 → **MAY** 使用 布尔；
- source 可靠支持 数值型 comparator / value / unit语义→ **MAY** 使用 number；
- source 只保留 raw string，且无法可靠类型化 → 使用 text。

规范化器 **MUST NOT**：

- 根据字符串外观猜 布尔；
- 发明 术语 code；
- 猜 unit；
- 猜 数值型 comparator / scale；
- 把无可靠类型信息的 旧版 text 当作 typed value。

### 8.5 Context

`Context` 是轻量嵌入式限定信息：

    Context {
        value       : ContextValue
        provenance? : Provenance[1..*]
    }

value 必需。

`provenance` 可选，并继续遵守 §17.10 的“继承当前完整集合、完全覆盖、禁止叠加合并、冗余时省略”规则。

Context **不**具有独立 身份，不进入 文档 root 集合，也不是 Relation 端点。

#### 8.5.1 ContextValue

ContextValue 使用与 PreferenceValue **不同的**最小 带标签联合类型：

    ContextValue =
        CodedContextValue
        | TextContextValue

§8.5–§8.6 不复用 PreferenceValue，因为 Context 不具有 preference comparator、preference choice 或 preference-specific value 语义。

##### CodedContextValue

    CodedContextValue {
        kind  : "coded"
        value : Coding
    }

当适用的术语或 context binding 能可靠表达情境概念时，规范化器 **SHOULD** 使用 coded 变体。

例如可以表达 traveling、work setting、family support present、home setting、communication via a particular channel 或 workday-like social context，前提是有可靠 Coding。

当前规范不定义这些具体 code 或词汇。

##### TextContextValue

    TextContextValue {
        kind  : "text"
        value : Text
    }

Text 变体 是 保真回退。

当来源明确包含 contextual 信息，但无法可靠 术语-map 时，规范化器 **MAY** 使用 TextContextValue。

如果适用的规范性 binding 已经提供可靠 `Coding`，规范化器 **SHOULD** 使用 coded 变体，而 **MUST NOT** 仅为实现方便把所有 `Context` 降级为 `Text`。

规范化器 **MUST NOT** 为了避免 Text 回退 而发明 术语 code。

TextContextValue **MUST NOT** 成为 arbitrary 元数据 bag，也 **MUST NOT** 要求 downstream NLP 才能恢复本可可靠结构化的所有 Context。

§8.5–§8.6 不加入 布尔 / 数值型 ContextValue 变体，因为 C1–C10 stress cases 不需要它们；family-support-present 等 来源概念s 可作为 coded context 概念 表达，无法可靠 coding 时用 Text 保真回退。

#### 8.5.2 `Context` 语义边界

Context 表达 co-occurring / situational / background qualification，而不表达 来源归因的 reason、已验证的 cause、Provenance、语义时间范围 或 工作流状态。

例如：

- “旅行期间漏服”在只有 co-occurring situation 语义时 → Context(traveling)；
- “因为旅行漏服”来源明确表达 reason → BehaviorFactor，而不是仅 Context；
- “恶心时停药”若只支持 contextual coincidence → Context；
- “因为恶心停药” → 来源归因的 BehaviorFactor。

“工作日”只有在来源把它作为社会 / 生活情境概念时 **MAY** 表示为 Context；如果其唯一语义是 calendar recurrence / day filter，应使用已经适用的 temporal / frequency 语义，而 **MUST NOT** 为方便重复编码成 Context。

Context **MUST NOT** 创建 Behavior↔Behavior、Behavior↔Preference 或 Preference↔Preference 显式 entity link；这些继续使用 Relation。

#### 8.5.3 `Context` 相等性

`Context` 的语义内容相等**不包含 `provenance`**。

两个 `Context` 的内容语义等价，当且仅当：

- `ContextValue.kind` 相同；
- coded value 使用 §15 的 `Coding` 规范信息相等；或
- text value 使用 §8.1 的 `Text` 相等性。

不同 `ContextValue.kind` **MUST NOT** 语义等价。

`Context` 的完整限定信息相等要求：

1. `Context` 内容相等；
2. 有效来源集合按 §17.10 的 `Provenance` 语义相等规则判定为语义等价。

`Behavior.contexts` / `Preference.contexts` 的集合顺序 **MUST NOT** 表示优先级、因果关系或其他语义顺序。

两个 `Context` 项如果完整限定信息相等，则在规范集合中属于冗余重复项；规范化 **MUST** 至多保留一个。内容相同但有效来源信息不同的 `Context` 不属于完整信息相等的重复项。

当前规范不定义 `Context` 的模糊相似度。

### 8.6 BehaviorFactor

`BehaviorFactor` 定义如下：

    BehaviorFactor {
        role        : FactorRole
        factor      : FactorValue
        direction   : FactorDirection
        provenance? : Provenance[1..*]
    }

role、factor、direction 必需。

provenance 可选，并完全复用 §17.10 nested provenance 规则。

BehaviorFactor 是 Behavior-local non-Core factor qualifier，不具有独立 身份，也不是 Relation 端点。

#### 8.6.1 FactorRole

规范 FactorRole tokens：

    "reported_reason"
    "observed_association"
    "antecedent"
    "explanatory"

语义：

-`"reported_reason"`：来源明确把 factor 描述为该 Behavior 的理由 / 原因归因；这是 来源归因的 语义，不是 已验证的 因果 truth。
-`"observed_association"`：来源只支持 factor 与 Behavior 的 recorded / 观测的 关联 或 co-occurrence，不声称 reason。
-`"antecedent"`：来源支持 factor 在 Behavior 之前出现；temporal precedence 不等于 因果关系。
-`"explanatory"`：外部 human / 模型 / 规则 / 分析 过程 给出的 解释性 factor 语义。若该 解释 超出 来源直接内容，其有效 provenance **MUST** 保持`"inferred"` derivation。

`FactorRole` **MUST NOT** 使用 `"inferred"` 作为 `role`；DIRECT / INFERRED / UNDETERMINED 属于 `Provenance.derivation`。

§8.5–§8.6 不新增`causes`、`causal_factor`、`verified_cause` 等 因果 role。

#### 8.6.2 FactorDirection

规范 FactorDirection tokens：

    "factor_to_behavior"
    "behavior_to_factor"
    "unspecified"

direction 必需，从而显式区分“来源支持方向”与“来源没有足够方向信息”。

`"factor_to_behavior"` 只表示 来源支持的语义orientation 从 factor 指向 所属对象 Behavior，**MUST NOT** 自动表示 factor caused Behavior。

`"behavior_to_factor"` 同理只表示相反 orientation，**MUST NOT** 自动表示 Behavior caused factor。

`"unspecified"` 表示来源没有足够信息确定 orientation；规范化器 **MUST NOT** 通过 旧版字段name、token 顺序、temporal proximity 或 NLP guess 补造方向。

对于`"antecedent"` role，direction **MUST** 为`"factor_to_behavior"`，因为该 role 定义的是 factor precedes 所属对象 Behavior。

对于`"reported_reason"` role，direction **MUST** 为`"factor_to_behavior"`，因为 source attribution 表达 factor 被报告为 所属对象 Behavior 的理由。

`"observed_association"` 与`"explanatory"` 可以根据来源 / inference 支持使用任一 direction token，包括`"unspecified"`。

Direction 与 因果关系 始终是不同维度。

#### 8.6.3 FactorValue

FactorValue 使用 带标签联合类型：

    FactorValue =
        CodedFactorValue
        | TextFactorValue

##### CodedFactorValue

    CodedFactorValue {
        kind  : "coded"
        value : Coding
    }

当 factor 可以可靠 术语-map，例如 dizziness / nausea 等 来源概念 时，规范化器 **SHOULD** 使用 coded 变体。

##### TextFactorValue

    TextFactorValue {
        kind  : "text"
        value : Text
    }

当 factor 只有 来源措辞、无法可靠 术语-map 时，TextFactorValue 用于 fidelity preservation。

规范化器 **MUST NOT** 发明 factor Coding。

Factor text **MUST NOT** 被仅塞入 Annotation 后再要求下游 NLP 恢复 BehaviorFactor 机器语义。

§8.5–§8.6 不新增 Symptom Core 实体。

#### 8.6.4 `BehaviorFactor` 因果语义边界

BehaviorFactor 本身 **MUST NOT** 创建 因果 Relation，也 **MUST NOT** 创建 Relation.weight。

以下都不等价于 已验证的 因果关系：

- reported_reason；
- antecedent；
- observed_association；
- direction；
- inferred / 解释性 factor。

如果未来需要规范性的因果 `Relation` 词汇，必须由专门的 `Relation` 词汇规范定义；当前规范不做该设计。

#### 8.6.5 `BehaviorFactor` 与`Relation` 的边界

BehaviorFactor 只用于 Behavior-local non-Core factor。

如果 factor 实际是已有的文档内 `Behavior` 或 `Preference` 实体，并且语义是显式类型化实体关系，规范表示 **MUST** 使用 `Relation`，而不是把该实体的 `display` / label 降级成 `BehaviorFactor`。

BehaviorFactor **MUST NOT** 成为绕过 /§14 Relation 端点 / type 契约 的第二套 entity-link 机制。

#### 8.6.6 `BehaviorFactor` 相等性

`BehaviorFactor` 的语义内容相等**不包含 `provenance`**。

两个 `BehaviorFactor` 的内容语义等价，当且仅当：

- `role` token 相同；
- `direction` token 相同；
- `factor.kind` 相同；
- coded factor 使用 §15 的 `Coding` 规范信息相等；或
- text factor 使用 §8.1 的 `Text` 相等性。

因此，nausea + `reported_reason` 与 nausea + `observed_association` **MUST NOT** 语义等价。

`BehaviorFactor` 的完整限定信息相等要求：

1. `BehaviorFactor` 内容相等；
2. 有效来源集合按 §17.10 的 `Provenance` 语义相等规则判定为语义等价。

`Behavior.factors` 的集合顺序 **MUST NOT** 表示优先级、因果关系、时间顺序或其他语义顺序。

两个 `BehaviorFactor` 项如果完整限定信息相等，则在规范集合中属于冗余重复项；规范化 **MUST** 至多保留一个。

当前规范不定义 `BehaviorFactor` 的模糊相似度。

仍为 **TODO** 的主要是：

- 类型兼容 / conversion 规则；
- 未来的字节级确定性序列化规范；
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

每个 PBDL 文档 **MUST** 至少包含一个 Subject，并 **MAY** 包含多个 Subject。

每个 Subject **MUST** 具有 文档内 身份。

每个 Behavior 与 Preference **MUST** 能够解析到恰好一个 Subject。

§17 规定规范 `Subject` 仅包含必需的 `id` 字段；`EntityId` 词法约束见 §17.3。`Subject` 隐私表示、外部标识符绑定方式与 DSL 表层语法仍为 **TODO**。

## 10. Behavior

Behavior 表示对某个 Subject 已描述或已断言的行为、未发生行为或行为状态。

它用于回答类似以下问题：

> 这个主体做了什么、没有做什么，或表现出了什么行为状态？

Behavior **MUST** 绑定到恰好一个 Subject，并 **MUST** 具有稳定的 文档内 身份。

Behavior 本身不等价于：

- diagnosis
- risk 结果
- recommendation
- 因果 解释
- Preference
- Pathway step

Behavior 的身份表示一个具体 Behavior 实例，而不是其类型或显示标签。因此 Behavior type **MUST NOT** 自动充当 Behavior 身份。

### 10.1 旧版`executor` 兼容性

历史`Behavior.executor` 概念继续保留兼容价值。

Subject 与 Behavior executor / actor 不是同一个概念：

- Subject 表示“这条 Behavior / Preference 描述围绕谁”；
- executor / actor 表示“谁执行了该行为或参与了该动作”。

在最常见情况下，两者可以是同一人；但历史设计也可能需要表达 caregiver 等其他 actor。

当前规范不引入完整 Participant 模型，也不在此处定义 `executor` 的最终字段类型。后续规范 **MUST NOT** 仅因为 `Behavior` 已绑定 `Subject` 就无条件删除历史 `executor` 语义。

每个规范Behavior 实例 **MUST** 实际具有至少一条 provenance 关联链路，使其来源能够被追踪。仅仅“语言理论上支持 provenance”不足以满足该要求。

### 10.2 `Behavior` 时间语义

`Behavior` **MAY** 具有语义时间范围，用于描述该 `Behavior` 语义内容发生、持续或适用的时间范围。

历史 `Behavior.temporal_scope` 的时间表达能力继续保留，其规范方向是映射到共享 Core 时间抽象，而不是沿用旧字符串表示。

Behavior 缺少 语义时间 **MUST NOT** 被解释为永久行为、当前行为或反复行为；它只表示该 Behavior 的 语义时间 未指定。

### 10.3 Trigger / Symptom 关联语义

§10.3 保留历史`Behavior.behavior_trigger` 与`Behavior.symptom_triggered` 所表达的“原因 / 诱因 / 症状关联”能力，但不继承 旧版 名称中`trigger` /`triggered` 的默认因果含义。

旧版 trigger / triggered naming **MUST NOT** 单独建立以下任一语义：

- A caused B；
- A clinically caused B；
- A is a 已验证的 因果 factor of B。

字段名称本身 **MUST NOT** 被视为因果证据。

§10.3 至少区分以下三类非等价语义情况。

#### 10.3.1 来源明确归因的理由

当来源明确把某因素描述为 Behavior 的原因、理由或诱因时，规范语义 **MAY** 保留“该来源把 X 归因为 / 描述为 Y 的原因或理由”这一 来源归因的 reason。

例如患者明确说“因为头晕，我停药了”，可以表示“患者报告头晕是其停药理由”。

来源归因的 reason **MUST NOT** 被 规范语义 自动等价为 已验证的 因果 relation。

如果来源本身明确表达该原因，而 LLM / NLP 只进行忠实抽取、解析、规范化或术语映射，没有新增来源未表达的解释，该结构化结果仍 **MAY** 具有 DIRECT provenance 语义。

Source attribution 的来源身份 **MUST** 能够通过 §13 Provenance 保持可追踪。

#### 10.3.2 观测或记录的关联与前置关系

如果来源只记录某因素与 Behavior 共现、在其之前出现、在相近 Context 中出现，或存在记录上的关联，但来源没有明确声称“这是 Behavior 的原因”，规范语义 **MUST NOT** 自动把该信息升级为 来源归因的 reason。

观测的 / recorded 关联 or antecedent **MUST NOT** 自动成为 因果 claim。

特别地，temporal precedence 只说明时间顺序。A precedes B **MUST NOT** 自动推出 A caused B。

#### 10.3.3 推断解释

如果来源本身没有明确表达原因，但 LLM、ML 模型、规则 engine、分析 过程 或其他推导过程根据输入生成“X 可能解释 / 导致 Y”之类的解释，该信息属于 INFERRED 解释性 信息。

INFERRED 解释 **MUST NOT** 静默表示为 DIRECT 来源归因的理由，也 **MUST NOT** 被伪装成已验证的因果关系。

DIRECT / INFERRED 的判断继续遵守 §13：依据语义内容是否相对于来源内容经过推导，而不是处理链路中是否出现 LLM / NLP / 模型 / tool。

#### 10.3.4 旧版`behavior_trigger` 兼容性

历史`Behavior.behavior_trigger` 的表达能力继续保留。

规范 转换 **MUST NOT** 仅因为 旧版 字段名为`behavior_trigger` 就赋予 因果 语义。

只有来源语义足够明确时，旧版 value 才可以被解释为更具体的 来源归因的 reason、观测的 antecedent、contextual 关联 或 inferred 解释 等语义类别。

如果 旧版 value 的真实含义不清楚，规范 转换 **MUST NOT** 擅自升级为 报告的 / 来源归因的 reason 或 因果 解释。

当前规范不定义这些未来类别的表层名称、具体字段或 enum。

#### 10.3.5 旧版`symptom_triggered` 兼容性与方向

历史`Behavior.symptom_triggered` 的表达能力继续保留，但该 旧版 字段名本身存在方向歧义，例如：

- symptom → behavior；
- behavior → symptom；
- symptom 与 behavior 仅有关联而来源没有明确方向。

`symptom_triggered` 字段名 **MUST NOT** 单独决定语义direction。

如果 规范语义 表达 symptom-related direction，该 direction **MUST** 有来源内容支持。

如果来源不支持方向，规范化 **MUST NOT** 发明方向。

Direction 与 因果关系 是两个不同维度：

- symptom precedes behavior **MUST NOT** 自动推出 symptom caused behavior；
- symptom follows behavior **MUST NOT** 自动推出 behavior caused symptom。

§10.3 不新增 Symptom 一级 PBDL-Core 实体，也不修改 `Relation` 端点矩阵。Symptom-related 信息的最终结构归属尚未定义；未来可以由 `Behavior` 局部结构化信息、`Context`、外部 coded 概念、扩展或其他结构承担。

当前规范不定义新的规范性 `Relation` 词汇。`related_to`、`associated_with`、`reported_reason_for`、`precedes`、`follows` 等仍是非规范性候选，除非后续规范另行定义。

§17 将 `Behavior` 局部、非 Core 实体的 trigger / symptom / reason 关联归入 `Behavior.factors`；若两端均为允许的 Core 实体且表达显式的类型化实体关系，仍使用 `Relation`。

`BehaviorFactor` 的具体表示见 §8.6：

- role = reported_reason / observed_association / antecedent / 解释性；
- factor = coded / text FactorValue；
- direction = factor_to_behavior / behavior_to_factor / unspecified；
- provenance? 继续复用 §17.10。

旧版`behavior_trigger` /`symptom_triggered` 的 规范化 **MUST** 依据真实 source语义选择 Context、BehaviorFactor 或 Relation，而 **MUST NOT** 仅根据 旧版字段name 猜测 reason、direction 或 因果关系。

规范性 Relation 词汇、具体 symptom 术语 规范、JSON Schema 与 DSL syntax 尚未定义。

### 10.4 旧版`communication_status` 兼容性

历史`Behavior.communication_status` 的表达能力继续保留，但单一 旧版 字段混合了多种不同语义。规范 转换 **MUST NOT** 仅凭`communication_status` 字段名决定其规范语义 category，也 **MUST NOT** 默认把这些语义继续压成一个通用 Behavior 状态。

旧版 `communication_status` 的语义至少分为以下四类情况。

#### 10.4.1 实际沟通`Behavior`

如果来源描述 Subject / actor 实际实施或没有实施某个沟通行为，例如：

- 患者告诉医生自己漏服了药；
- 患者给护士打电话报告副作用；
- 患者没有告诉医生自己已经停药；

这首先属于 观测的 / 报告的 communication behavior，而不是单纯 工作流状态。

只要该信息满足 `Behavior` 的既有语义边界，它 **MAY** 作为 `Behavior` 语义内容表达。

“患者告诉医生 X”与“X 被医生记录进 EHR”不是同一个概念；前者描述沟通行为，后者在表达信息来源、记录过程或进入系统的路径时属于 Provenance 语义。

当前规范不定义 communication behavior 的具体 behavior type、actor、recipient 或 channel 字段。既有 `Behavior.executor` 继续遵守本节兼容边界；当前规范不新增 Participant 一级 Core 实体。

#### 10.4.2 沟通情境信息

如果 旧版`communication_status` 的真实语义是限定另一个 Behavior / Preference 如何处于某种沟通情境，例如“该漏服行为已经向临床人员披露”或“该偏好尚未向家属沟通”，这类信息可以保留为 candidate contextual / communication qualification。

该类语义 **MUST** 与 实际沟通 `Behavior`、Provenance 信息、工作流 / 应用状态 保持可区分。

规范 `Behavior` 不保留 `communication_status` 字段，并继续按实际沟通 `Behavior` / `Context` / `Provenance` / 工作流或应用状态四路分流。

§8.5 规定 `Context` 可用 coded / text `ContextValue` 表达沟通情境概念，例如 communication-via-WeChat；这 **MUST NOT** 被解释为工作流状态，也不重新引入 `communication_status : string`。

具体 communication 词汇 / Communication 扩展 尚未定义。

#### 10.4.3 沟通相关`Provenance`

如果 旧版`communication_status` 实际想表达：

- 谁报告或记录了这条信息；
- 信息从哪个来源或渠道进入系统；
- 谁抽取、生成或记录了该信息；
- 信息何时被记录、抽取或生成；

这些语义属于 §13 Provenance，而不是 通用 Context。

规范 转换 **MUST NOT** 为了保留 旧版`communication_status` 而复制、覆盖或混淆已经属于 Provenance 的语义。

#### 10.4.4 工作流与应用状态

如果 旧版`communication_status` 实际表示`pending review`、`reviewed`、`acknowledged`、`escalated`、`assigned`、`notified`、`message sent`、`task completed`、`closed` 等软件或业务流程状态，这些信息默认属于 工作流 / 应用层。

PBDL-Core **MUST NOT** 默认把此类 工作流 / 应用状态 当作患者自身 Behavior 的 intrinsic语义状态。

历史能力可以由 未来扩展、应用 元数据 或外部 工作流 system 继续承载； 不设计该 扩展。

#### 10.4.5 沟通不等于事实认证

信息 communicated **MUST NOT** 自动等价为 信息 已验证的。

同样，`acknowledged` **MUST NOT** 自动等价为`agreed`、`verified` 或`true`。

例如患者已经告诉医生“我每天都按时服药”，只说明发生过报告 / 沟通，不表示该内容已经被认证为现实真值。该边界继续遵守 §13 “PBDL records sourced 信息, not certified truth”。

如果来源同时包含沟通行为、其他 Behavior 和 来源归因的 reason，规范 转换 **MUST NOT** 仅压缩成一个`communication_status` 而丢失其余可区分语义；旧版 迁移 **MUST** 以实际来源含义为准。

### 10.5 `Behavior` 频率与重复模式语义

`Behavior` 语义内容 **MAY** 描述：

- 一个具体 occurrence；
- 一个 behavior 状态；
- 来源明确描述的 summarized / recurring behavior 模式。

规范语义 **MUST** 保留来源描述的是具体 occurrence、已观察 occurrence 汇总，还是 recurring / 定性 模式。

规范化 **MUST NOT** 仅因为来源描述了 模式，就自动展开出来源没有提供的 具体 观测发生记录 timestamps；也 **MUST NOT** 仅因为存在若干独立 发生记录，就自动把它们压缩为 recurring 模式。

#### 10.5.1 参考时间窗内的观测或报告计数

来源可以描述一个引用window 中实际观察或报告的 发生次数，例如“过去 7 天漏服 3 次”。

这表示在该引用window 中存在 count 信息。

观测的 / 报告的 count within a引用window **MUST NOT** 仅通过 规范化 自动变成 重复规则 或稳定 frequency 模式。

例如：

- “过去 7 天漏服 3 次” **MUST NOT** 自动等价为“每周固定漏服 3 次”；
- “漏服 3 次”在没有引用period 时 **MUST NOT** 被转换为`3/week`、`3/month` 或其他 rate。

Count、rate 与 重复模式 是不同语义。当前规范不定义额外的 rate 字段。

#### 10.5.2 重复或周期模式

如果来源明确描述某项 Behavior 具有重复模式，例如“每天吸烟”“每周运动三次”“每天早晨测血压”，规范语义 **MAY** 保留 recurring / periodic 模式。

Recurring 模式 **MUST NOT** 被强制展开成未来或过去的 具体 观测发生记录 timestamps。

“每天”描述的是 模式，不表示来源已经观察或确认每一天都存在一个具体 occurrence。

如果多个独立 发生记录 被外部 模型 / 分析 过程 总结为 recurring 模式，而来源本身没有表达该 模式，则该 模式 属于 INFERRED provenance 语义。

#### 10.5.3 定性频率

来源可以使用`often`、`sometimes`、`rarely`、`frequently`、`occasionally`、`intermittently` 等 定性 frequency / 模式 信息。

规范化 **MUST NOT** 仅为了数值化或规范化方便，把 定性 frequency 擅自映射到来源未提供的具体阈值、概率、rate 或 recurrence interval。

例如：

-`often` **MUST NOT** 无来源依据地变成`>= 5 times/week`、`70%` 或`daily`；
-`intermittent` **MUST NOT** 自动变成`every N hours` 或固定的`N times/week`。

#### 10.5.4 精确、近似与定性表达

规范化 **MUST** 在语义层面保留 频率信息 是 精确、近似 还是 定性。

例如：

- “每周大约 3 次” **MUST NOT** 被转换为“exactly 3 times/week”；
- “几乎每天” **MUST NOT** 被转换为“exactly daily”；
- “偶尔” **MUST NOT** 被转换为来源未提供的固定 rate。

当前规范不定义额外的 近似 字段。

#### 10.5.5 预期或处方计划不等于实际`Behavior` 频率

Expected / prescribed 计划 与 actual patient Behavior frequency **MUST** 保持可区分。

例如，“医生要求每天服药两次”描述 prescribed / expected regimen，不表示患者实际每天服药两次。

规范语义 **MUST NOT** 仅根据 expected / prescribed 计划 自动生成 actual Behavior frequency。

反过来，actual Behavior frequency **MUST NOT** 自动被解释成 prescribed 计划。

即使同时知道 prescribed 计划 与 actual Behavior frequency，PBDL-Core **MUST NOT** 因此自动生成 adherence percentage、poor adherence、noncompliant 或其他 派生 adherence judgment。

§10.5 不设计 Prescription、Regimen 或 adherence analysis 模型。

#### 10.5.6 分母与频率值边界

当来源只提供 发生次数 而没有引用period 时，规范化 **MUST NOT** 发明 frequency rate。

当来源缺少 expected opportunities / doses 或其他 denominator 时，规范化 **MUST NOT** 发明 adherence ratio、adherence percentage、nonadherence rate 或其他比例。

例如“过去 7 天漏服 3 次”只直接支持 missed count 与引用window；它本身不提供该期间应服药的总次数。

#### 10.5.7 发生记录不会自动建立重复模式

若来源只提供多个 具体 发生记录，规范 转换 **MUST NOT** 自动宣称存在 recurring 模式。

例如 Monday、Tuesday、Wednesday 各记录一次 exercise，不自动等价为“patient exercises daily”。

如果来源明确总结为 daily，则可以保留来源描述的模式；如果模式是模型/规则/分析过程根据发生记录推断所得，则该模式 **MUST** 保留 INFERRED provenance 语义，并 **MUST NOT** 静默表示为 DIRECT 来源描述的频率。

如果 LLM / NLP 只忠实抽取来源已经明确表达的 frequency / recurrence，例如“我基本每天都会测血压”，结果仍 **MAY** 属于 DIRECT provenance 语义。

#### 10.5.8 未提供频率信息及其范围

Behavior **MAY** 没有 frequency / recurrence 信息。

缺少 frequency / recurrence 信息 **MUST NOT** 被解释为：

- once；
- only once；
- non-recurring；
- irregular；
- continuous；
- daily；
- 未知 but frequent。

它只表示 规范语义 没有提供 repetition / 频率信息。

Frequency / recurrence **MUST NOT** 成为所有 Behavior 的强制属性。

`never`、`always` 等具有强 范围 含义的 frequency expressions **MUST NOT** 在缺少来源支持的 temporal / contextual 范围 时被自动解释为 lifetime 范围、从出生至今或未来永久成立。

#### 10.5.9 持续时间、`Context`、理由与`Provenance` 的边界

Duration / 时间范围 与 frequency **MUST** 保持可区分。

“持续 3 小时”描述 duration / 时间范围；“每 3 小时一次”描述 recurring interval / 模式。§10.5 不设计完整 duration arithmetic。

Frequency / recurrence 信息属于 `Behavior` 语义内容的限定，但它与 `Context`、来源归因的 reason 和 `Provenance` 是不同维度。

例如“工作日经常忘记服药”可以同时包含 定性 frequency 与 workday Context；若来源另说“因为工作忙所以忘记”，还包含 §10.3 来源归因的 reason。规范语义 **MUST NOT** 把这些语义压成一个 frequency 字符串。

Frequency assertion 继续继承该 Behavior 的 §13 source traceability；“谁报告该 frequency”或“谁根据日志推断该 模式”属于 Provenance，而不是 frequency value 本身。

§10.5 不把 recurrence 语义契约 扩张到 Preference 或 Relation。若未来出现明确需求，应另行审议。

§17 规定 `Behavior.frequencies : BehaviorFrequency[0..*]` 作为独立的结构化限定信息，并允许在必要时具有局部 `provenance`。

§8.3 进一步规定：

- observed_count / rate / recurrence / 定性 四种 discriminated 变体；
- count-only 观测的 表示；
- FrequencyPeriod；
- 精确 / 近似 precision token；
- weekly weekday 计划 与 有限 day-part token；
- 定性 frequency token set；
- BehaviorFrequency 语义内容相等 与完整 qualifier 相等性。

Duration arithmetic、hour-level recurrence、RRULE / cron、Preference recurrence、JSON Schema 与 DSL syntax 尚未定义。

### 10.6 旧版`reasoning_note` 兼容性

历史 `Behavior.reasoning_note` 的人类可读说明能力继续保留，但其规范语义归属统一为 §5.8 的 `Annotation` 语义。

旧版`reasoning_note` **MUST NOT** 因字段名中的 “reasoning” 被解释为 PBDL-Core 自己执行并认证了正确推理、clinical reasoning、已验证的 解释 或 因果 reasoning。

如果旧版 `reasoning_note` 忠实承载来源已经明确表达的说明，其 `Annotation` **MAY** 具有 DIRECT provenance 语义。

如果人工标注者、模型、规则引擎或分析过程新增了来源未表达的解释，规范表示 **MUST** 保持其真实的人工撰写或 INFERRED derivation 区分；模型生成的新解释 **MUST NOT** 冒充 DIRECT 来源文本。

旧版`reasoning_note` **MUST NOT** 替代 结构化 Behavior 语义、必需 Provenance、Evidence、§10.3 reason / 因果关系 边界 或 派生-结果 边界。

§5.8 **MUST NOT** 被解释为要求保存模型 hidden chain-of-thought / private reasoning trace。

§17 规定旧版 `reasoning_note` → `Behavior.annotations`，且 `Annotation` 采用轻量嵌入结构；更细的序列化以及作者/生成者表示仍留待后续定义。

## 11. Preference

Preference 表示某个 Subject 对选项、属性、治疗特征或结果所表达或推断出的倾向、选择、优先级、厌恶或偏好。

Preference **MUST** 绑定到恰好一个 Subject，并 **MUST** 具有稳定的 文档内 身份。

Preference 本身不等价于：

- 观测的 Behavior
- clinical recommendation
- risk 结果
- conflict 结果
- objective constraint or barrier

现实信息中可能存在客观 constraint / barrier，但 不新增 Constraint 一级 Core 实体。相关语义边界保留为未来设计问题。

Preference category 或显示标签 **MUST NOT** 自动充当 Preference 身份。

### 11.1 旧版`associated_behavior` 兼容性

历史 `Preference.associated_behavior` 所表达的“偏好与行为之间存在关联”继续保留兼容价值，但其规范归属由 §14 的 `Relation` 规则承担。

在规范PBDL语义中，`Preference.associated_behavior` **MUST NOT** 继续作为与 Core Relation 平行的第二套 first-class 关联 机制。

旧版`Preference.associated_behavior` **MUST** canonicalize 为显式的 Preference–Behavior Relation。

因此，历史字段继续作为 旧版 compatibility input 概念 保留，但规范Preference 不再同时维护：

- dedicated`associated_behavior` link；
- 与其表达同一语义的 Relation。

如果旧输入使用自由文本 Behavior label 表达`associated_behavior`，规范 转换 **MUST** 先将其解析到恰好一个 Behavior 身份。

- 0 个匹配：未解析 / 无效；
- 多个匹配：歧义 / 无效。

规范 转换 **MUST NOT** 通过数组位置、最近文本、第一个匹配或 LLM 猜测静默选择一个 Behavior。

旧版`associated_behavior` 本身只证明来源声明 Preference 与某个 Behavior 存在某种 关联。它 **MUST NOT** 自动意味着 Preference caused Behavior、Behavior caused Preference、Preference resulted from Behavior、Preference conflicts with Behavior 或 Preference explains Behavior。

如果旧版或来源材料支持更具体的关系含义，规范语义 **SHOULD** 保留来源支持的最具体语义；但规范化 **MUST NOT** 生成来源没有支持的更强 `Relation` 类型。

当前规范不定义该 `Relation` 的具体规范类型 code 或词汇 token。

每个规范Preference 实例 **MUST** 实际具有至少一条 provenance 关联链路，使下游能够判断该 Preference 是直接表达还是外部推断所得。

直接表达与推断出的 Preference 可以具有相同的 preference category 与 preference value，但其 provenance语义**MUST** 保持可区分，不得仅依赖自然语言 note 来判断。

### 11.2 `Preference` 时间语义

Preference **MAY** 具有 语义时间范围，用于描述该 Preference 的适用时间范围。

Preference 的表达时间、记录时间、抽取时间或生成时间属于 Provenance 时间；这些时间 **MUST NOT** 自动替代 Preference 的 applicability time。

Preference 缺少语义时间信息 **MUST NOT** 被解释为永久偏好。

不同时期的不同 Preference 信息可以作为不同 Preference 实例 共存，例如某一时期拒绝注射、另一时期接受注射。

历史 Preference 正式字段表虽然没有独立 temporal 字段，但 v1 Core **MAY** 表达 Preference temporal applicability，以避免把可随时间变化的偏好误解为永久状态。

### 11.3 旧版`note` 兼容性

旧版 `Preference.note` 的兼容能力继续保留。

其历史人类可读说明能力继续保留，并在规范语义归属上统一解释为 §5.8 的 `Annotation` 语义。

`Preference.note` **MUST NOT** 承担`preference_category`、`preference_value` 或其他 结构化 Preference 机器语义 的唯一表达。

例如，仅有 `note = "不喜欢打针"` **MUST NOT** 被视为规范结构化 `Preference` 语义内容的替代品。

Preference Annotation **MUST NOT** 自动成为 Evidence 或 Provenance，也 **MUST NOT** 仅凭文本内容创建新的 Behavior、Preference、Relation、Context、因果 claim 或 派生 结果。

§17 规定旧版 `Preference.note` → `Preference.annotations`，并定义 `Annotation` 的最小 `text` + `provenance` 字段；更细的序列化以及作者/生成者表示仍留待后续定义。

`Preference` 的规范字段见 §17；`SourceDescriptor` / `Evidence` 与 `Confidence` 的具体表示见 §17.8；`PreferenceValue` 的 coded / text / 布尔 / number 带标签联合类型见 §8.4。

### 11.4 `PreferenceValue` 表示边界

Preference.value **MUST** 使用 §8.4 PreferenceValue，而 **MUST NOT** 使用 arbitrary untyped JSON 或 untagged string 作为规范机器 value。

TextPreferenceValue 是 词汇 / typing 无法可靠恢复时的保真 回退，不是规避 结构化语义的默认逃生口。

布尔 false 是明确 value，不等于 missing Preference。

NumericPreferenceValue 必须显式保留 comparator；dimensioned quantity 的 unit 不能被猜测。

§8.3–§8.4 不设计 Preference recurrence、Preference conflict、ordinal / strength analytics、multi-select engine、JSON Schema 或 DSL syntax。

## 12. Context

`Context` 的最小语义职责与具体规范表示见 §8.5 与 §12。

Context 用于表达解释某个 Behavior / Preference 时，与其发生、成立或被理解相关的情境性背景或条件限定。它的职责是 **qualify 语义解释**，而不是证明原因、执行推理、记录来源或承载软件工作流。

规范 Context：

    Context {
        value       : ContextValue
        provenance? : Provenance[1..*]
    }

ContextValue 为 coded / text 带标签联合类型，详见 §8.5。

### 12.1 `Context` 不是兜底容器

Context **MUST NOT** 被当作“无法分类的信息都放进 Context”的默认 catch-all container。

已经具有明确语义职责的信息 **MUST NOT** 仅为了结构便利而被重新解释为 通用 Context：

- 信息从哪里来、如何产生，属于 §13 Provenance；
- Behavior / Preference / Relation 何时发生、成立或适用，属于 §5.7语义temporal 语义；
- 来源归因的 reason、观测的 antecedent 与 inferred 解释 继续使用 §10.3 / §8.5–§8.6 BehaviorFactor 语义；
- risk、conflict、recommendation、score、因果 inference 等 派生 analysis 属于 Core 外部的 派生 / 应用 结果；
- 工作流 / 应用状态 默认属于 Core 外。

Context **MUST NOT** 作为绕过既有 Provenance、temporal、BehaviorFactor / reason 或 派生-analysis 边界的替代容器。

### 12.2 `Context` 不建立因果关系

某因素被表示为 Context **MUST NOT** 自动表示该因素 caused Behavior、caused Preference 或 clinically explains an outcome。

例如，Behavior 发生在 traveling context 中，只说明该 Behavior 具有 traveling contextual qualification；它 **MUST NOT** 自动推出 traveling caused the Behavior。

如果来源明确表达“因为旅行忘记服药”，应使用 BehaviorFactor reported_reason 语义，而不是仅靠 Context 获得 reason / 因果 语义。

Context **MUST NOT** 仅因为某因素影响或限制行为，就自动把它定义为 objective Constraint / Barrier。

### 12.3 `Context` 保真回退

当 contextual 概念 可可靠 术语-map 时，规范化器 **SHOULD** 使用 CodedContextValue。

当来源有 contextual 信息，但无法可靠 术语-map 时，TextContextValue 提供 保真回退。

规范化器 **MUST NOT** 发明 术语 code。

Text 回退 **MUST NOT** 让所有 Context 退化成自由文本，也不能成为 arbitrary 元数据 bag。

### 12.4 `Context` 与时间/频率语义边界

Calendar / date-time语义extent 属于 TemporalExtent。

Behavior recurrence / weekday 计划 属于 BehaviorFrequency。

“工作日”只有在来源语义是社会 / 生活情境概念时 **MAY** 作为 Context；如果它只是 recurrence / calendar filter，**MUST NOT** 因实现方便重复编码成 Context。

Context 不设计 规则 / predicate engine。

### 12.5 未提供`Context`

Behavior / Preference **MAY** 没有显式 Context 信息。

缺少 Context **MUST NOT** 被解释为：

- context-free；
- 普遍适用；
- unconditional；
- 在任何环境都成立。

它只表示 规范语义 当前没有提供额外 contextual qualification。

### 12.6 `Context` 的身份、引用与集合边界

Context 不要求独立 身份，不加入 Subject / Behavior / Preference 文档内身份命名空间，不进入 root 集合，也不成为 Relation 端点。

Behavior.contexts / Preference.contexts 的 集合顺序 **MUST NOT** 产生语义优先级。

完整信息相等 Context 重复项 的 规范化 见 §8.5.3。

§8.5–§8.6 不新增 shared Context 身份、ContextRef、Constraint / Barrier entity 或 Communication entity。

Context JSON Schema 与 DSL syntax 尚未定义。

## 13. Evidence 与 Provenance

`Provenance` 与 `Evidence` 的最小语义边界见 §13。

### 13.1 Provenance

Provenance 回答：

> “这条 Behavior / Preference / Relation assertion 是怎么来的？”

Provenance 描述信息或 语义断言 的来源与产生路径。其语义 **MUST** 足以让下游判断该信息来自什么来源或产生方式，并能够区分来源直接描述的信息与外部推断得到的信息。

概念上，Provenance 可以涉及：

- 来源类型；
- 来源身份或外部引用；
- 产生方式；
- 记录、抽取或生成该信息的主体 / 系统；
- 在必要时用于来源解释的时间信息；
- 该信息是否经过推断。

以上描述的是语义职责，不是字段列表或 Schema。

每个规范Behavior **MUST** 至少具有一条 provenance 关联链路。

每个规范Preference **MUST** 至少具有一条 provenance 关联链路。

每个规范Relation assertion **MUST** 至少具有一条 provenance 关联链路 或等价的可追踪 provenance 语义。

Relation assertion 的 provenance **MUST NOT** 被 source 端点 或 target 端点 的 provenance 自动替代。Relation provenance 的详细规则见 §14.7。

同一个 Behavior、Preference 或 Relation assertion **MAY** 具有多条 provenance 关联链路。

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

§17 规定 `Evidence` 为可选的 `Provenance.evidence` 嵌入集合，且不要求 `Evidence` 身份；具体字段与 `locator`/`content` 表示见 §17.8.5。

### 13.2.1 `Provenance` 时间边界

Provenance-related time 可以涉及报告、记录、观测、抽取或生成等不同 event roles。

这类 Provenance 时间 **MUST NOT** 自动承担 Behavior / Preference / Relation 的 语义时间范围。

同一条信息的 语义时间 与 Provenance 时间 可以不同，也可以只提供其中之一。

§17规范Provenance **不提供** 无角色的 通用 top-level`time` 字段，因为单一 TemporalValue 无法在 source 与 generator 共存时无歧义地区分 reporting / recording / observation time 与 extraction / generation time。

§17.8.3 / §17.8.5 规定 source / reporting / recording / observation 相关时间的具体归属：使用角色明确的 `SourceTimeEvent`，并由 `SourceDescriptor` 或具体 `Evidence` 项承载。

§17.8.4 规定 extraction / generation 相关时间的具体归属：使用 `GeneratorDescriptor` 下角色明确的 `GeneratorTimeEvent`。

如果未来需要 provenance-level event timeline，应采用具有 显式 role语义的结构，而 **MUST NOT** 重新引入无角色 通用 Provenance 时间。

### 13.3 DIRECT 与 INFERRED

`Provenance` 至少区分两类必须可区分的语义；具体表层 enum 名称当前规范不定义。

DIRECT / INFERRED 判断的是**结构化语义内容相对于来源内容的产生方式**，而不是处理链路中是否使用了某种模型或工具。

使用 LLM、NLP 或其他工具进行 extraction、parsing、规范化、术语 mapping 或 序列化 转换，本身 **MUST NOT** 自动使该信息成为 INFERRED。

如果结构化语义忠实表示来源中已经明确报告、记录或观测到的内容，即使抽取或标准化过程由 LLM / NLP 完成，该信息仍 **MAY** 属于 DIRECT。

只有当结构化语义内容超出来源直接表达、记录或观测的内容，并由模型、规则、分析过程或其他推导过程生成时，该信息才属于 INFERRED provenance 语义。

#### DIRECT

DIRECT 表示信息直接来自某个来源的报告、记录或观测，例如概念上的：

- patient self-report；
- survey response；
- clinician documentation；
- device observation；
- manual entry。

DIRECT **MUST NOT** 被解释为“已经证明绝对真实”。它只表示 PBDL 没有把该项语义标记为由外部推理过程生成的结论。

#### INFERRED

INFERRED 表示信息由 LLM、ML 模型、规则 engine、分析 过程 或其他 inference 过程 根据其他输入推断产生。

INFERRED 信息 **MUST NOT** 静默表示成 DIRECT 或来源直接描述的信息。

规范语义表示 **MUST** 使下游能够区分 DIRECT 与 INFERRED provenance 语义，而不能仅通过自由文本 note 猜测。

对于 Preference：

- 来源明确表达“我不想每天打针”，LLM 仅将其结构化抽取为 injection aversion 时，仍可属于 DIRECT / expressed `Preference`；
- 来源没有明确表达该偏好，而模型根据多项行为记录推断“患者可能偏好低治疗负担方案”时，属于 INFERRED Preference。

即使两者最终具有相同的 preference category 或 preference value，其 provenance语义仍 **MUST** 可区分。

### 13.4 冲突来源与多来源

如果多个来源支持的是同一项结构化语义，一个 Behavior / Preference **MAY** 关联多条 provenance。

如果不同来源表达的语义内容实质不同或相互冲突，规范表示 **MUST NOT** 通过 provenance 合并、对象折叠或其他方式丢失、掩盖或使这些冲突语义不可区分。

默认情况下，这些冲突内容 **SHOULD** 保持为不同的 Behavior / Preference 实例；未来若采用其他表示方式，也必须保持各项冲突语义可区分。

例如：

- 患者自述规律服药；
- 设备或记录显示存在漏服；

二者可以并存，但不应因为主体相同就被静默压缩成一个单一 Behavior 并仅附加两个 provenance source。

PBDL-Core 不负责自动裁决冲突，不在 §13 设计 ConflictAnalysis。

### 13.5 旧版来源字段兼容性

历史`Behavior.evidence_source` 的来源追踪能力继续保留，但其规范性方向是映射到统一的 Provenance / Source 语义，而不是把单一 string 字段定义为最终模型。

历史`Preference.source_type` 同样收敛到统一的 Provenance / Source 语义。

Behavior 与 Preference **SHOULD NOT** 长期维护两套彼此独立、语义重复的来源机制。

`evidence_source` 与 `source_type` 的历史兼容意义继续保留；§17 规定其规范归属统一进入 `Provenance`，不再保留旧版平行字段。

### 13.6 `Confidence` 边界

confidence **MUST NOT** 成为所有 Preference 的强制属性。

DIRECT self-report **MUST NOT** 被迫赋予模型式 confidence。

如果 confidence 用于 INFERRED 信息，其语义 **MUST** 能够说明：

- confidence 由谁或什么系统生成；
- confidence 衡量什么；
- confidence 对应哪个 inference 过程 / 模型 / 分析 过程。

规范 `confidence` 归属为可选的 `Provenance.confidence`；`value` + `metric` + 可选 `scale` 的最小具体契约与相等性见 §17.8.6。校准 框架、阈值 策略、metric 词汇 governance、JSON Schema 与 DSL 序列化尚未定义。

历史`Preference.confidence_score` 因此继续保留为待细化概念，但不得被解释为所有 Preference 的必需 Core 属性。

### 13.7 `Provenance` 身份

Provenance 自身仍 **不要求** 独立的 文档内 身份。

当前 必需 provenance-bearing规范语义断言 至少包括：

- Behavior；
- Preference；
- Relation assertion。

§14 新增 Relation assertion provenance 要求 **MUST NOT** 被解释为 Provenance 因此必须具有 身份，也 **MUST NOT** 被解释为 Relation 因此必须具有 身份。

当前仍没有 Core 场景要求其他实体通过稳定 Core引用指向某个 Provenance 实例。

`Provenance` 的最小字段与嵌入式附着方式见 §17；`SourceDescriptor` / `GeneratorDescriptor` / `Evidence`、嵌套 `provenance` 相等性与继承、`Confidence` 语义以及基于 `Text` / `TemporalValue` / `Confidence` 的来源相等性均在相关小节定义。共享 `Provenance` 身份、provenance chaining、JSON Schema 与 DSL 序列化仍为 **TODO**。

## 14. Relations

Relation 用于在两个允许作为 Relation 端点 的 PBDL语义entities 之间显式表达语义联系。

`Relation` 的最小语义组成如下：

- source 端点
- target 端点
- 关系类型 概念

`Relation` 的抽象语义见 §14；规范字段 `source` / `target` / `type` / `temporal` / `provenance` / `annotations` 与 `CoreEntityRef` 引用结构见 §17。JSON Schema 与 DSL 语法尚未定义。

Relation source 与 target **MUST** 是 entity 引用，并 **MUST** 分别解析到恰好一个允许的 端点 entity。

未定义引用是无效的。

歧义引用是无效的。

自由文本 label **MUST NOT** 直接充当规范性 Relation 端点 引用。历史 string label 可以作为 旧版输入，但在形成规范化语义前 **MUST** 被解析到明确 entity 身份。

### 14.1 Core 允许的端点

PBDL-Core Relation 在 中允许：

- Behavior → Behavior
- Behavior → Preference
- Preference → Behavior
- Preference → Preference

PBDL-Core 不允许 `Subject` 作为 Core `Relation` 端点。

PBDL-Core 不允许 `Relation` 作为 `source` 或 `target`，因此不支持 `Relation→Relation` 或实体→`Relation`。

### 14.2 `Relation` 时间语义

Relation **MAY** 具有 语义时间范围，用于描述该 Relation 本身成立或适用的时间范围。

历史 `Relation.temporal` 的时间能力继续保留，其规范方向是映射到共享 Core 时间抽象，而不是沿用旧字符串表示。

Relation 时间元数据 与 `Relation` 类型语义是不同维度。

Relation 时间元数据 **MUST NOT** 自动被解释为`precedes`、`follows`、before、after 或其他 顺序 relation。

如果未来 Relation 词汇 定义`precedes`、`follows` 等类型，其先后语义属于 `Relation` 类型 本身，而不是 时间元数据 的隐式解释。

对于历史`Relation.temporal` 中混合了“适用时间”和“关系先后类型”的数据，规范 转换 **MUST NOT** 在未区分真实含义时直接把旧值视为单一 时间范围。

### 14.3 `Relation` 身份

Relation 在 v1 Core 最小模型中**不要求自身具有 身份**。

这是因为当前没有已定义的 Core引用需要指向 Relation 本身，且 Relation 也不是允许的 Relation 端点。

未来若 `Evidence` / `Provenance`、扩展或其他明确使用场景需要稳定引用 `Relation`，后续规范可增加 `Relation` 身份要求；当前规范不提前定义。

### 14.4 `Relation.type` 默认不表示因果关系

`Relation` 类型 概念 用于说明 source 与 target 之间“是什么关系”，但 `Relation` 类型 **MUST NOT** 因其名称或存在本身就被解释为因果关系。

PBDL-Core 当前不将`causal_effect` 定义为默认关系，也不把未经证据支持的因果权重作为 Core 的默认能力。

`Relation` 的语义时间范围与 `Relation.type` 顺序语义相互独立，见 §5.7。

§8.2 已定义以下 `TemporalValue` 规则：

- TemporalValue 词法形式；
- temporal precision preservation；
- 数值型 offset / ZoneToken 表示；
- 规范信息相等；
- minimum Interval comparability。

因此上述 TemporalValue 表示 details 不再属于本节 TODO。

仍为 **TODO** 的是：

- final JSON Schema integration；
- DSL syntax / 序列化；
- 规范性 relation 词汇 与 具体 关系类型 codes；
- inverse relation conventions；
- 派生 relation-strength 工件 structure；
- relation 词汇 序列化。

### 14.5 显式`Relation` 边界

Relation 表示两个允许 端点 之间由 规范语义 **显式声明**的 typed语义link。

仅仅因为两个实体：

- 属于同一 Subject；
- 同时出现或时间相近；
- 具有相同 Context；
- 出现在同一 Evidence / 来源材料；
- 出现在同一句话或相邻字段；
- 使用相同 术语 code / category；

规范化 **MUST NOT** 自动创建 Relation。

如果上游 模型、规则 engine 或 分析 过程 基于这些信息推断存在 Relation，该 Relation 是 INFERRED relation assertion，并继续遵守 §13 provenance / derivation 边界。

### 14.6 `Relation.type` 语义契约与方向性

每个规范Relation **MUST** 使用具有稳定、机器可解释语义定义的 关系类型。

`Relation` 类型 定义 source / target 在该关系中的 语义角色，并 **MUST** 使 conforming implementation 能够判断该关系的 方向性 语义，例如 有向 或 对称 / non-有向。

每个 规范性 关系类型 definition **MUST** 明确其允许的 端点 语义角色 / 端点 kinds。具体 关系类型 可以比 global 端点 matrix 更严格，但 **MUST NOT** 扩大 global 端点 matrix 所允许的 Core 端点 combinations。

每个 规范性 关系类型 definition **MUST** 明确其 因果语义状态：它要么明确承载 因果 语义，要么明确属于 non-因果 语义。

如果 关系类型 definition 没有明确赋予 因果 语义，规范 使用方 **MUST NOT** 根据 type name、方向性、端点 order 或其他隐式线索把它解释为 因果 relation。

`Relation` 类型 **MUST NOT** 只是一段自由文本说明、显示标签或 UI 文案。

A conforming规范Relation **MUST** 使用其语义由适用 PBDL 词汇 / 术语 binding 定义的 关系类型。未定义 或 free-text-only 关系类型语义**MUST NOT** 被当作规范性 机器语义。

当前规范不定义完整的 `Relation` 词汇、具体 code、序列化形式或开放/封闭词汇策略，也不新增具体因果关系类型。`Relation` 的规范结构字段见 §17；规范关系词汇仍待专门定义。

对于 有向 关系类型，交换 source / target 会改变或破坏该 关系类型 所定义的语义。

对于对称/非定向关系类型，交换端点顺序 **MUST NOT** 被解释为不同的关系语义。

规范化 **MUST NOT** 在不知道 关系类型 方向性语义时自行猜测、反转或重排 端点。

Source → target 的 端点 顺序 本身 **MUST NOT** 自动建立 因果关系、temporal precedence、influence、优先级、evidence-for 或 parent/child 语义；这些只能由 关系类型 definition 明确规定。

有向 Relation **MUST NOT** 因其 方向性 自动等价为 因果 Relation。

### 14.7 `Relation` 断言的`Provenance`

每个规范Relation assertion **MUST** 具有至少一条 provenance 关联链路 或等价的可追踪 provenance 语义。

Relation assertion 的 provenance **MUST NOT** 被 source 端点 或 target 端点 的 provenance 自动替代。

端点 assertions 与 relation assertion 是不同语义陈述。例如：

- Behavior A 可以来自 device observation；
- Preference B 可以来自 patient self-report；
- A 与 B 之间的 relation 可以由 模型 推断。

此时两个端点可以分别具有 DIRECT provenance，而 `Relation` 断言本身仍属于 INFERRED。

`Relation` 断言的 DIRECT / INFERRED 判定继续遵守 §13：依据关系语义内容是否相对于来源内容经过推导，而不是处理链路中是否使用了 LLM / NLP / tool。

如果来源明确表达某 `Relation`，而 LLM / NLP 只忠实抽取该关系且没有新增语义推断，该 `Relation` 断言 **MAY** 是 DIRECT / 来源描述的。

如果 `Relation` 来自模型、规则引擎、统计过程或其他分析推断，它 **MUST** 保持 INFERRED provenance 语义，并 **MUST NOT** 静默表示为 DIRECT 来源描述的 `Relation`。

如果 Relation 表达 来源归因的 reason，它仍继续遵守 §10.3：来源归因的 reason 不等价于 已验证的 因果关系。

同一个 Relation 语义断言 **MAY** 具有多条 provenance 关联链路，但更多 provenance **MUST NOT** 自动意味着 Relation 更真实、更强或更 因果。

### 14.8 不同`Relation` 断言与去重

相同 端点 pair 不代表相同 Relation assertion。

不同的：

- 关系类型；
- direction；
- temporal applicability；
- DIRECT / INFERRED derivation 语义；
- provenance 支持的含义；

都可以使 Relation assertions 在语义上不同。

Semantically distinct Relation assertions **MUST** 保持可区分，规范化 **MUST NOT** 仅因为 source / target 相同就静默合并。

规范化 **MAY** 合并真正语义等价、端点 相同、type 相同、direction 相同、temporal applicability 相同，且合并不会丢失 provenance distinction 或 derivation distinction 的重复 Relation assertion。

当前规范不定义具体去重算法。

### 14.9 `Relation` 身份规则保持不变

§14 不改变身份decision：Relation 在当前 v1 Core minimum 中仍然 **不要求自身具有 身份**。

新增 Relation provenance 要求 **MUST NOT** 被解释为 Relation 因此获得 必需 身份。

Relation 继续 **MUST NOT** 作为 Relation 端点， 端点 matrix 保持不变。

### 14.10 `Relation` 时间语义独立性

Relation 语义时间范围 继续表示 Relation 本身何时成立或适用。

Temporal extent、关系类型 与 方向性 是三个不同维度。

存在 时间元数据 **MUST NOT** 自动把 关系类型 推断为`precedes` /`follows`；关系类型 是 有向 也 **MUST NOT** 自动生成 temporal 顺序 语义。

### 14.11 `Relation.weight` 仍属于派生结果

历史`Relation.weight` 的 disposition 保持为 **MOVE_DERIVED**。

`Relation.weight` **MUST NOT** 重新成为默认 PBDL-Core Relation intrinsic语义strength。

旧`weight` 可能代表 correlation coefficient、模型 score、ranking weight、confidence-like value、关联 strength、因果 effect estimate 等彼此不同的语义，不能被 Core 当成一个统一概念。

如果外部分析提供 relation strength、statistic、score 或 effect estimate，该结果属于派生/分析工件。其 metric 语义、derivation 方法、模型/算法、provenance、version 与适用端点/关系需要由未来的派生结果规范明确；§14 不设计该 Schema。

来源描述的 定性 strength 与 派生 数值型 relation strength **MUST** 保持可区分。

例如来源中的“患者强烈偏好口服药”不能仅因为出现“强烈”就被转换成`Relation.weight = 0.9`；文本中的“二者高度相关”也不能在没有统计定义时被伪造成 数值型 relation weight。

## 15. 术语绑定

`Coding` 的具体规范表示如下：

    Coding {
        system   : string
        code     : string
        display? : Text
        version? : string
    }

`system` 与 `code` 必需。

`display` 与 `version` 可选。

`system`、`code`，以及存在时的 `version` **MUST** 为非空字符串。

Core **MUST NOT** 要求 `system` 一定是 URI；具体术语绑定规范可以进一步约束 `system`，但 Core 不做该假设。

`Coding` 的机器语义身份为：

    Coding identity = system + code

`display` 仅是人类可读表示，**MUST NOT** 改变 `Coding` 的机器身份。

`version` 不改变上述基本 `system + code` 身份，但属于规范信息。

### 15.1 `Coding` 相等性

两个 `Coding` 的基本机器身份相同，当且仅当：

- `system` 字符串精确相同；
- `code` 字符串精确相同。

两个 `Coding` 的规范信息相等则要求：

- `system` 精确相同；
- `code` 精确相同；
- `version` 同时缺失，或精确相同；
- `display` 同时缺失，或按 `Text` 相等性判定为语义等价。

因此，相同 `system + code`、不同 `version` 的 `Coding` 仍共享基本机器身份，但 **MUST NOT** 被视为规范信息相等。

不同 `display` 也 **MUST NOT** 改变机器身份，但会使规范信息表示不相等。

Core **MUST NOT** 自动 trim、case-fold、URI-normalize 或对 `system` / `code` / `version` 做术语规范化。

当前规范不定义任何具体 SNOMED CT、LOINC、ICD 或其他医学术语 code。

## 16. 语义约束

当前规范的语义约束如下：

1. PBDL-Core **MUST** 区分来源直接描述的信息与外部推断、分析或计算得到的信息。
2. PBDL-Core **MUST NOT** 因信息被写入 PBDL 就宣称该信息在现实世界中已经被认证为绝对真实。
3. 一个 PBDL 文档 **MUST** 至少包含一个 Subject，并 **MAY** 包含多个 Subject。
4. Subject、Behavior 与 Preference **MUST** 具有 文档内 身份。
5. Subject、Behavior 与 Preference 共享同一个 文档内身份命名空间，其 identifier **MUST** 在所属 PBDL 文档 内唯一。
6. identifier **MUST NOT** 由数组位置或列表顺序充当规范性 身份。
7. Behavior 与 Preference **MUST** 各自绑定到恰好一个 Subject。
8. 每个规范Behavior **MUST** 实际具有至少一条 provenance 关联链路。
9. 每个规范Preference **MUST** 实际具有至少一条 provenance 关联链路。
10. 规范语义表示 **MUST** 能区分 DIRECT 与 INFERRED provenance 语义。该判断依据是结构化语义内容相对于来源内容是否经过推导，而不是处理链路中是否使用了 LLM、NLP、模型或其他工具。
11. 仅使用工具进行 extraction、parsing、规范化、术语 mapping 或 序列化 转换 **MUST NOT** 自动使信息成为 INFERRED。
12. INFERRED 信息 **MUST NOT** 静默表示成 DIRECT / 来源描述的信息。
13. 同一个 Behavior / Preference **MAY** 具有多条 provenance 关联链路，但多来源 **MUST NOT** 自动表示更高真值或可信度。
14. 如果不同来源表达的语义内容实质不同或冲突，规范表示 **MUST NOT** 通过 provenance/source 合并、对象折叠或其他方式丢失、掩盖或使这些冲突语义不可区分。默认情况下，**SHOULD** 使用彼此分离的 `Behavior` / `Preference` 实例。
15. Provenance 与 Evidence **MUST NOT** 被当作完全同义概念。
16. confidence **MUST NOT** 成为所有 `Preference` 的强制属性，DIRECT self-report **MUST NOT** 被迫赋予模型式 confidence。
17. Provenance 在 §13 中不要求独立 身份。
18. 语义时间 与 Provenance 时间 **MUST NOT** 被视为同一个时间概念，Provenance / reporting time **MUST NOT** 自动替代 Behavior / Preference / Relation 的 语义时间。
19. Behavior、Preference 与 Relation **SHOULD** 使用共享 Core temporal abstraction 表达 语义时间范围。
20. Core temporal abstraction 至少支持 Instant、Interval 与未提供 语义时间 三种最小语义情况。
21. Interval **MUST** 至少具有一个有效边界；若 start 与 end 同时存在且可比较，start **MUST NOT** 晚于 end。
22. 单边界 `Interval` 中未提供的另一侧边界只表示边界未提供，**MUST NOT** 自动解释为永久、ongoing、一直延伸到现在或未来、从无限过去开始，或数学意义上的 unbounded interval。
23. 缺少语义时间信息 **MUST NOT** 被解释为永久、当前、始终、反复或“时间不重要”。
24. 规范化 **MUST** 保留来源实际支持的 temporal precision，并 **MUST NOT** 发明来源未提供的时间精度。
25. 来源未提供 timezone / offset 时，规范化 **MUST NOT** 凭空补充；来源已提供时，规范表示 **MUST** 能够保留。
26. 规范语义 中保留的 相对 temporal expression **MUST** 具有明确 锚点；无明确 锚点 的裸相对时间 **MUST NOT** 被假装成唯一确定的 绝对 时间范围。
27. Relation 时间元数据 **MUST NOT** 自动承担`precedes` /`follows` 等 `Relation` 类型 顺序 语义。
28. Behavior type、Preference category、显示标签与 `Relation` 类型 **MUST NOT** 自动充当 实体实例 身份。
29. Core引用**MUST** 在当前文档引用范围 内解析到恰好一个实体。
30. 未定义引用与 歧义引用均无效。
31. Relation source / target **MUST** 使用明确 entity 引用，不能使用未解析的自由文本标签。
32. Core Relation 端点 仅允许 Behavior 与 Preference；Subject 与 Relation 均不是 中的 Relation 端点。
33. Relation 在 v1 Core 最小模型中不要求 身份，且 Relation **MUST NOT** 作为 Relation 端点。
34. PBDL-Core **MUST NOT** 将未经证据支持的因果权重作为来源直接描述的信息或默认 Core 语义。
35. Treatment Pathway 不属于初始重新设计中的 PBDL-Core。
36. 旧版`trigger` /`triggered` naming **MUST NOT** 单独建立 因果 语义；字段名称本身 **MUST NOT** 被视为因果证据。
37. 来源归因的 reason **MUST** 与 已验证的 因果语义保持可区分，规范语义 **MUST NOT** 自动把“某来源声称 X 是 Y 的原因 / 理由”升级为 已验证的 因果 relation。
38. 观测的 / recorded 关联、co-occurrence 或 temporal antecedence **MUST NOT** 自动升级为 来源归因的 reason 或 因果 claim；temporal precedence **MUST NOT** 自动推出 因果关系。
39. INFERRED 解释 **MUST NOT** 静默表示为 DIRECT 来源归因的理由，并继续遵守 §13 关于语义派生的 DIRECT / INFERRED 判定规则。
40. 如果来源不支持 symptom-related direction，规范化 **MUST NOT** 从`symptom_triggered` 字段名或时间顺序中发明 direction；已知 direction **MUST NOT** 自动等价为 因果关系。
41. Context **MUST NOT** 自动建立 因果关系；Contextual qualification **MUST NOT** 自动等价为 reason、因果 解释 或 已验证的 因果 effect。
42. `Behavior` / `Preference` 缺少显式 `Context` **MUST NOT** 被解释为无情境、普遍适用或无条件；它只表示未提供额外的情境限定。
43. Context **MUST NOT** 被用作 Provenance、语义时间、trigger / reason 语义、派生 analysis 或 工作流 / 应用状态 的默认替代容器。
44. 旧版`communication_status` **MUST NOT** 仅凭字段名决定规范语义 category，也 **MUST NOT** 默认定义为单一通用 Behavior 状态。
45. Actual communication Behavior、contextual communication 元数据、Provenance 信息 与 工作流 / 应用状态 **MUST** 保持语义可区分。
46.`communicated` /`reported` /`acknowledged` **MUST NOT** 自动等价为`verified`、`true`、`agreed` 或来源内容已得到事实认证。
47. Behavior frequency / recurrence **MUST** 与 §5.7 语义时间范围 保持可区分；duration / applicability interval **MUST NOT** 自动等价为 重复模式。
48. 观测的 / 报告的 发生次数 within a引用window **MUST NOT** 自动等价为 recurring 模式 或稳定 重复规则。
49. 定性 或 近似 frequency **MUST NOT** 被 规范化 擅自数值化、阈值化或提高到来源未提供的精确度。
50. Expected / prescribed 计划 **MUST NOT** 自动表示 actual patient Behavior frequency；actual Behavior frequency **MUST NOT** 自动表示 prescribed 计划。
51. Recurring 模式 **MUST NOT** 被 规范化 自动展开成来源没有提供的 fabricated 具体 观测发生记录s。
52. 多个观测发生记录 **MUST NOT** 自动被总结为重复模式；若模式来自外部推断，该模式 **MUST** 保留 INFERRED provenance 语义，并 **MUST NOT** 静默表示为 DIRECT 来源描述的频率。
53. 缺少 frequency / recurrence 信息 **MUST NOT** 被解释为 once、only once、non-recurring、irregular、continuous 或任何具体 repetition 模式。
54. 规范化 **MUST NOT** 在缺少引用period 时发明 frequency rate，也 **MUST NOT** 在缺少 denominator / expected opportunities 时发明 adherence ratio、adherence percentage 或其他比例。
55. Frequency / recurrence语义**MUST NOT** 成为所有 Behavior 的强制属性。
56. Relation **MUST NOT** 仅因为实体共现、属于同一 Subject、时间相近、Context 相同或共享来源材料而被隐式创建。
57. `Relation` 类型 **MUST** 具有定义明确的机器语义并决定 端点 roles / 方向性 语义；source / target 顺序 本身 **MUST NOT** 建立 因果关系、temporal precedence、importance 或其他未由 关系类型 定义的语义。
58. 有向 `Relation` **MUST NOT** 自动等价为因果 `Relation`；对于对称/非定向关系类型，交换端点顺序 **MUST NOT** 被解释为不同的关系语义。
59. 旧版`Preference.associated_behavior` 在规范语义 中 **MUST** 统一表示为 显式 Preference–Behavior Relation，**MUST NOT** 继续形成与 Relation 平行的规范link 机制。
60. 旧版`associated_behavior`引用**MUST** 解析到恰好一个 Behavior 身份；未定义 / 未解析 或 歧义 mapping 无效，规范 转换 **MUST NOT** 静默猜测目标。
61.规范转换 **MUST NOT** 仅凭 旧版`associated_behavior` 发明比来源支持更强的 relation 语义。
62. 每个规范Relation assertion **MUST** 具有至少一条 provenance 关联链路 或等价可追踪 provenance 语义；端点 provenance **MUST NOT** 自动替代 Relation assertion provenance。
63. INFERRED `Relation` 断言 **MUST NOT** 静默表示为 DIRECT 来源描述的 `Relation`，即使其端点分别具有 DIRECT provenance。
64. Semantically distinct Relation assertions **MUST NOT** 仅因为 端点 相同而被静默合并；关系类型、direction、temporal applicability 与 derivation / provenance distinction 必须得到保留。
65.`Relation.weight` **MUST NOT** 作为默认 Core Relation intrinsic语义strength；派生 数值型 strength / statistic **MUST** 与 来源描述的 relation语义保持可区分。
66. 未定义 或 free-text-only 关系类型语义**MUST NOT** 被当作规范机器语义。
67. Annotation **MUST NOT** 作为已有 结构化规范机器语义 的唯一替代载体；conforming 使用方 **MUST NOT** 被迫解析自由文本 Annotation 才能确定核心机器语义。
68. Annotation text **MUST NOT** 自动创建新的 Behavior、Preference、Relation、Context、因果 claim、risk 结果、recommendation 或其他 派生 analysis 结果。
69. `Annotation` **MUST NOT** 替代必需 `Provenance`；source / generator / DIRECT / INFERRED derivation **MUST NOT** 仅通过自由文本 note 表达并要求下游猜测。
70. 旧版 `Behavior.reasoning_note` 与 `Preference.note` 在规范语义归属上统一为 `Annotation` 语义，但 `Annotation` **MUST NOT** 因此获得必需身份或 `Relation` 端点地位。
71. 模型/分析过程在来源未表达的基础上生成的解释性 `Annotation` **MUST** 保持 INFERRED derivation 语义，并 **MUST NOT** 伪装为 DIRECT 来源文本；忠实抽取或规范化本身 **MUST NOT** 自动使 `Annotation` 成为 INFERRED。
72. Annotation **MUST NOT** 自动等价于 Evidence，也 **MUST NOT** 仅凭文本内容建立 因果关系 或 Relation。
73. Annotation 与 结构化 规范语义 冲突时，conforming 使用方 **MUST NOT** 仅根据 Annotation 静默覆盖 结构化 语义。
74. PBDL-Core **MUST NOT** 要求 hidden chain-of-thought、private 模型 reasoning trace、internal scratchpad 或 hidden 模型 deliberation 作为规范性 Annotation 内容。

跨文档身份/引用协议、communication 词汇、Constraint / Barrier 模型、规范性 relation 词汇 / codes / inverse conventions、派生 relation-strength 工件 Schema、JSON Schema、DSL syntax 与术语词表仍为 **TODO**。

## 17. 规范对象模型

本节定义 PBDL-Core 的字段级规范对象模型。

本节定义规范对象图、字段归属、必需/可选、基数、嵌套限定信息归属、类型化引用归属、必需`provenance` 附着方式以及旧版字段到规范表示的归属。

本节 **不定义** JSON 序列化形式、JSON Schema、DSL 语法或实现规范。

[schema/pbdl-v1.schema.json](schema/pbdl-v1.schema.json) 仍只是 JSON Schema Draft 2020-12 占位文件；本节 **MUST NOT** 被解释为已经修改或定义该 Schema 文件。

### 17.1 规范根对象：`PBDLDocument`

规范 root对象名称定义为 PBDLDocument。

|字段| 类型 | 基数 | 要求 |
|---|---|---:|---|
| pbdl_version | VersionToken | 1 | 必需 |
| subjects | Subject | 1..* | 必需集合|
| behaviors | Behavior | 0..* | 必需集合，**MAY** 为空 |
| preferences | Preference | 0..* | 必需集合，**MAY** 为空 |
| relations | Relation | 0..* | 必需集合，**MAY** 为空 |

规范 文档 **MUST** carry an 显式 PBDL version declaration through pbdl_version。

`VersionToken` 是受约束的字符串词法 token。

当前 PBDL 1.0规范文档 的`pbdl_version` **MUST** 精确为：

    "1.0"

VersionToken 只表示 PBDL language / 规范-模型 version，**MUST NOT** 携带 implementation build number、git SHA、模型 version、schema URI 或产品版本。

当前规范不允许任意 implementation-defined version token 冒充 PBDL version。未来 PBDL 版本应由对应规范显式定义新的规范token。

PBDLDocument **MUST NOT** 增加 文档级 risk、recommendation、Pathway、工作流 状态、global annotation bag 或 global arbitrary 元数据 bag 作为 §17 Core 字段。

### 17.2 根集合顺序

subjects、behaviors、preferences、relations 的 集合位置 **MUST NOT** 承担 entity 身份。

除非未来某个嵌套类型另行定义顺序语义，规范集合顺序 **MUST NOT** 被下游解释为：

- 优先级；
- 因果关系；
- temporal order；
- ranking；
-语义身份。

上述根集合在语义模型中均为顺序无关。字节级确定性数组排序 **不属于**当前语义规范模型；该能力明确留给未来的确定性序列化规范，见 §22.11。

### 17.3 Subject

规范 Subject字段inventory：

|字段| 类型 | 基数 | 要求 |
|---|---|---:|---|
| id | EntityId | 1 | 必需 |

§17 不给 Subject 增加 name、age、sex、address、phone、完整 demographics、完整 EHR record、annotations、provenance、context 或 工作流 元数据。

Subject / Behavior / Preference 继续共享 文档内身份命名空间。

`EntityId` 是非空、区分大小写的 ASCII 词法 token：

    [A-Za-z_][A-Za-z0-9._-]*

EntityId **MUST** 满足该 词法形式。

EntityId 不要求 UUID，不承载全局 身份，也 **MUST NOT** 由 display、type、Coding.code 或 集合位置 派生。

Subject / Behavior / Preference 继续共享同一个 文档内 EntityId 命名空间。

### 17.4 Behavior

规范 Behavior字段inventory：

|字段| 类型 | 基数 | 要求 |
|---|---|---:|---|
| id | EntityId | 1 | 必需 |
| subject | SubjectRef | 1 | 必需 |
| type | Coding | 1 | 必需 |
| executor | ActorRef | 0..1 | 可选 |
| temporal | TemporalExtent | 0..1 | 可选 |
| frequencies | BehaviorFrequency | 0..* | 可选集合|
| contexts | Context | 0..* | 可选集合|
| factors | BehaviorFactor | 0..* | 可选集合|
| provenance | Provenance | 1..* | 必需 |
| annotations | Annotation | 0..* | 可选集合|

规范字段 `type` 正式承担旧版 `behavior_type` 的结构化机器含义：

- 旧版 Behavior.behavior_type → Behavior.type。

规范模型 **MUST NOT** 同时保留 type 与 behavior_type 两套平行 字段。

#### 17.4.1 Behavior.type

Behavior.type 使用 §15 已定义的 Coding语义type。

Coding 的概念职责保持：

- code + system 承担机器语义 身份；
- display 为人类可读展示；
- version 为可选信息。

`Coding` 的规范对象结构与相等性见 §15；JSON Schema 与 DSL 序列化尚未定义。

Behavior.type **MUST** 承担 结构化 机器语义，**MUST NOT** 由 Annotation 替代。

#### 17.4.2 Behavior.executor

executor 保留 旧版 executor语义capability，并为 可选 ActorRef。

`executor` 表示谁执行或参与 `Behavior`；它 **MUST NOT** 等价于 `Subject` 归属关系。

`ActorRef` 的规范联合类型如下：

    ActorRef = SubjectRef | ExternalActorRef

`SubjectRef` 变体使用 §17.7 定义的规范引用对象：

    { "ref": EntityId }

ExternalActorRef 变体 使用与 SubjectRef 结构互斥的 对象：

    {
        "kind": "person" | "device" | "software" | "other",
        "external_id"?: {
            "system": string,
            "value": string
        },
        "display"?: Text,
        "role"?: Text
    }

ExternalActorRef.kind 为 必需。

external_id、display、role 均 可选。

若 external_id 存在，其 system 与 value **MUST** 为 非空 string。external_id 表示外部命名空间中的稳定 identifier，**不属于** PBDL Core EntityId 命名空间。

display / role 仅为 人类可读的 description，**MUST NOT** 单独建立 stable actor 身份。

Caregiver / clinician 通常可使用 `kind = "person"` 并通过 `role` / `display` 描述；device 使用 `kind = "device"`；external software / system 使用 `kind = "software"`。

ActorRef union 采用 structural discrimination：

- 含 必需`ref` 且不含 ExternalActorRef字段的对象→ SubjectRef；
- 含 必需`kind` 且不含`ref` 的对象→ ExternalActorRef。

同时含`ref` 与`kind` 的 ActorRef **MUST** 被视为无效 规范表示。

ExternalActorRef 是 non-具有身份的 embedded descriptor，不进入 Subject / Behavior / Preference 文档内身份命名空间，也不成为 Relation 端点。

如果来源提供稳定的 `external_id`，该外部身份 **MAY** 用于表达多个 `Behavior` 中的同一外部 actor。

如果只有 display / role 而无 external_id，规范 使用方 **MUST NOT** 因文本相同就断言多个 Behavior 描述的是同一个 stable actor 实例。

当前规范不新增 Actor / Participant 实体、Participant 身份命名空间或 Participant `Relation` 端点。

#### 17.4.3 `Behavior.temporal` 与`TemporalExtent`

Behavior.temporal 为 可选 single TemporalExtent。

`TemporalExtent` 的规范结构如下：

    TemporalExtent = Instant | Interval

    Instant {
        kind        : "instant"
        at          : TemporalValue
        provenance? : Provenance[1..*]
    }

    Interval {
        kind        : "interval"
        start?      : TemporalValue
        end?        : TemporalValue
        provenance? : Provenance[1..*]
    }

Instant.at 必需。

Interval 的 start / end 至少一个存在。

TemporalExtent.provenance 为 可选；一旦存在，集合 **MUST** 至少包含一个 Provenance，显式空 集合无效。

`TemporalExtent` 具有可选的局部 `provenance`。

理由是 所属对象的 `provenance` 无法无损覆盖以下情况：

- `Behavior` 为 DIRECT，但 temporal 来自另一来源；
- `Behavior` 为 DIRECT，但 temporal 由模型推断；
- Preference 所属对象的 `provenance` = {P1,P2}，但 temporal 仅由 P1 支持；
- `Relation` 断言为 DIRECT，但 temporal applicability 为 INFERRED。

TemporalExtent.provenance **MUST** 完全复用 §17.10 的统一 继承 / 覆盖 / 相等性 /规范省略 规则：

- 局部字段缺失 → 继承所属对象当前适用的完整 `provenance` 集合；
- local present → 完全覆盖；
- additive merge → forbidden；
- 显式局部集合与继承的完整集合语义等价 → 规范形中省略。

当前规范 **MUST NOT** 为时间 `provenance` 发明第二套机制。

TemporalValue 词法约束、precision、timezone preservation 与 相等性 见 §8.2。

§5.7 允许 相对 time 带 锚点 保留或在规范化 前解析。§17 / 采用更严格 规范表示：TemporalExtent 的 结构化 边界 必须是 §8.2 合法 TemporalValue。

如果上游可基于明确 锚点 将 相对 expression 可靠解析为 Instant / Interval，则 **MAY** canonicalize。

如果不能可靠解析，规范化 **MUST NOT** 发明 绝对 time 或把 未解析 相对 expression 伪装成 TemporalExtent。

原始 相对 phrase **MAY** 通过 Evidence / Annotation 保真保存，但 **MUST NOT** 被当作 结构化 TemporalExtent。

当 Interval 同时具有 start 与 end 时，顺序 有效性 使用 §8.2.6 的保守 comparability 规则。

`TemporalExtent` 的内容相等与完整规范信息相等统一按 §22.9.1 处理。

#### 17.4.4 Behavior.frequencies

Behavior.frequencies 为 可选 BehaviorFrequency[0..*]。

BehaviorFrequency 具体 带判别标记联合类型、有效性 与 相等性 见 §8.3。

Behavior.frequencies集合**MAY** 同时包含不同 变体，例如：

- recurrence = daily once；
- observed_count = last week 3 occurrences。

两者表达不同 语义维度，**MUST NOT** 因指向同一 Behavior 而互相覆盖或自动 去重。

规范表示 **MUST NOT** 使用`frequency: "每天两次"` 等 arbitrary string 作为最终机器语义替代。

每个 BehaviorFrequency 变体 **MAY** carry 局部 `provenance`。

BehaviorFrequency 局部 `provenance` 完全遵守 §17.10：

- 局部字段缺失 → 继承所属对象当前适用的完整 `provenance` 集合；
- local present → 完全覆盖；
- additive merge → forbidden；
- redundant 显式 local set →规范省略。

ObservedCountFrequency.window 自身若携带 TemporalExtent.provenance，也继续独立遵守同一 §17.10 规则。

Prescribed / expected 计划 **MUST NOT** canonicalize 成 actual BehaviorFrequency，除非当前 Behavior assertion 本身描述的就是 计划-following / prescribed behavior 语义。

#### 17.4.5 Behavior.contexts

Behavior.contexts 为 可选 Context[0..*]。

Preference.contexts 同样使用 §8.5 Context 具体 type。

Context 不是 具有身份的 entity，不进入 文档 root 集合，也不是 Relation 端点。

Context 具体 字段：

    Context {
        value       : ContextValue
        provenance? : Provenance[1..*]
    }

ContextValue / 相等性 / text 回退 见 §8.5。

Context 局部 `provenance` 完全遵守 §17.10：

- 局部字段缺失 → 继承所属对象当前适用的完整 `provenance` 集合；
- local present → 完全覆盖；
- additive merge → forbidden；
- 冗余的显式完整集合 → 规范形中省略。

如果 Context 只由 所属对象的 `provenance` 的真子集支持，局部 `provenance` **MUST** 存在。

Context 集合顺序 **MUST NOT** 表示 优先级、因果关系 或 temporal order。

Context **MUST NOT** 成为 arbitrary 元数据 bag，也 **MUST NOT** 替代 TemporalExtent、BehaviorFrequency、BehaviorFactor、Provenance、Relation 或 工作流/应用 元数据。

#### 17.4.6 Behavior.factors

Behavior.factors 为 可选 BehaviorFactor[0..*]。

BehaviorFactor 具体 type 见 §8.6：

    BehaviorFactor {
        role        : FactorRole
        factor      : FactorValue
        direction   : FactorDirection
        provenance? : Provenance[1..*]
    }

`BehaviorFactor` 承载 `Behavior` 局部、非 Core factor 语义，包括来源归因的理由、观测关联、前置关系、外部解释性 factor 与旧版 symptom-related direction。

BehaviorFactor **MUST NOT** 成为 通用 Relation replacement。

如果 factor 实际是当前文档中的 `Behavior` / `Preference` 实体，并表达显式类型化实体关系，规范模型 **MUST** 使用 `Relation`。

BehaviorFactor **MUST** 是 结构化 qualifier，而不是 arbitrary reasoning string。

BehaviorFactor 局部 `provenance` 完全遵守 §17.10。

特别地，如果所属 `Behavior` 为 DIRECT，而解释性 factor 是模型/分析推断，则 factor **MUST** 显式写出局部 `provenance`，使有效 derivation 保持 `"inferred"`，不能继承成所属对象的 DIRECT。

FactorRole、FactorDirection、FactorValue、因果关系 边界 与 相等性 详见 §8.6。

#### 17.4.7 旧版`Behavior` 字段归属

规范 Behavior **MUST NOT** 保留 communication_status 字段。

旧版 communication_status 按 canonicalize：

- actual communication behavior → Behavior；
- contextual communication qualification → Context；
- source / reporting 信息 → Provenance；
- 工作流 / 应用状态 → Core 外。

规范 Behavior **MUST NOT** 保留 risk_tag、validity_flag 或 reasoning_note：

- risk_tag → 派生 / 应用 结果；
- validity_flag → validator / report output；
- reasoning_note → annotations。

其他主要 旧版 mapping：

| 旧版字段 | 规范字段归属 |
|---|---|
| behavior_type | Behavior.type |
| executor | Behavior.executor |
| temporal_scope | Behavior.temporal |
| evidence_source | Behavior.provenance |
| behavior_trigger / symptom_triggered | Context when source supports only situational / co-occurring qualification; Behavior.factors when source supports Behavior-local non-Core reason / 关联 / antecedent / 解释 / direction 语义; Relation when both 端点 are Core entities and语义are 显式 typed relation |

### 17.5 Preference

规范 Preference字段inventory：

|字段| 类型 | 基数 | 要求 |
|---|---|---:|---|
| id | EntityId | 1 | 必需 |
| subject | SubjectRef | 1 | 必需 |
| category | Coding | 1 | 必需 |
| value | PreferenceValue | 1 | 必需 |
| temporal | TemporalExtent | 0..1 | 可选 |
| contexts | Context | 0..* | 可选集合|
| provenance | Provenance | 1..* | 必需 |
| annotations | Annotation | 0..* | 可选集合|

`PreferenceValue` 的具体带标签联合类型、有效性、迁移与相等性见 §8.4。

旧版字段归属：

| 旧版字段 | 规范字段归属 |
|---|---|
| preference_category | Preference.category |
| preference_value | Preference.value |
| source_type | Preference.provenance |
| confidence_score | Provenance.confidence when语义/ generator are supportable |
| associated_behavior | Relation |
| note | Preference.annotations |
| preference_conflict_flag | 派生 ConflictAnalysis / 应用 结果 |

规范 `Preference` **MUST NOT** 继续保留 `source_type`、`confidence_score`、`associated_behavior`、`note`、`preference_conflict_flag`、`preference_category` 或 `preference_value` 作为与新规范字段归属平行的旧版字段。

旧版 `confidence_score` **MUST NOT** 被无条件搬入 `Provenance.confidence`；只有在其 metric 含义与 generator / inference 过程可说明时才可保留。

### 17.6 Relation

规范 Relation字段inventory：

|字段| 类型 | 基数 | 要求 |
|---|---|---:|---|
| source | CoreEntityRef | 1 | 必需 |
| target | CoreEntityRef | 1 | 必需 |
| type | Coding | 1 | 必需 |
| temporal | TemporalExtent | 0..1 | 可选 |
| provenance | Provenance | 1..* | 必需 |
| annotations | Annotation | 0..* | 可选集合|

Relation 继续 **不要求 id 字段**。

`Relation` 不要求自身身份：Core `Relation` 表达语义断言，而不承诺跨文档版本的稳定生命周期句柄。

同一 端点 pair 上 type、temporal applicability 或 provenance语义不同的 Relation assertions 继续依其 规范语义内容 保持可区分。

仅 `Annotation` 发生变化 **MUST NOT** 被解释为 `Relation` 因此获得新的 Core 身份；temporal / type / provenance 语义内容的变化则可以表示一个不同的 `Relation` 断言。

Cross-version 生命周期 tracking、audit handles 与 Core 外 派生 工件 对特定 Relation assertion 的稳定定位属于 应用 / 扩展 responsibility，**MUST NOT** 通过 集合位置 冒充 Core 身份。

规范 Relation **MUST NOT** 具有 weight 字段、nested Relation 端点 或独立 inferred direction 字段。

Relation 方向性 继续由 Relation.type 语义契约 决定。

`Relation` 断言的内容相等与完整规范信息相等见 §22.9.3；该规则 **MUST NOT** 被解释为给 `Relation` 增加身份。

旧版 Relation.weight 继续属于 派生 / 分析 工件，不进入规范Core Relation。

### 17.7 类型化引用

唯一的规范内部引用结构如下：

    {
        "ref": EntityId
    }

`SubjectRef` 与 `CoreEntityRef` 使用同一对象结构，但具有不同的类型化解析契约。

#### 17.7.1 SubjectRef

    SubjectRef {
        ref : EntityId
    }

SubjectRef.ref **MUST** 解析到当前 PBDLDocument 中恰好一个 Subject。

#### 17.7.2 CoreEntityRef

    CoreEntityRef {
        ref : EntityId
    }

`CoreEntityRef.ref` **MUST** 解析到当前 `PBDLDocument` 中恰好一个 `Behavior` 或 `Preference`，并继续同时受全局 `Relation` 端点矩阵与具体 `Relation.type` 允许端点角色的约束。

Bare EntityId string **MUST NOT** 作为规范引用 表示。

引用对象**MUST NOT** 使用 display label、array index、Coding.code 或 type label 代替 ref。

规范内部引用采用对象包装而不是裸字符串，以减少显示字符串歧义，并为未来版本化引用扩展保留明确结构边界；当前规范引用对象不增加 `display` 或 `type` 字段。

### 17.8 Provenance

规范 Provenance 最小字段inventory：

|字段| 类型 | 基数 | 要求 |
|---|---|---:|---|
| derivation | DerivationKind | 1 | 必需 |
| source | SourceDescriptor | 0..1 | 可选, conditionally 必需 |
| generator | GeneratorDescriptor | 0..1 | 可选, conditionally 必需 |
| evidence | Evidence | 0..* | 可选集合|
| confidence | Confidence | 0..1 | 可选 |

Provenance 不要求 身份，也不进入 文档级 pool。

Provenance 默认 embedded / attached to the assertion it traces：

- Behavior.provenance : Provenance[1..*]；
- Preference.provenance : Provenance[1..*]；
- Relation.provenance : Provenance[1..*]；
- Annotation.provenance : Provenance[1..*]。

#### 17.8.1 Provenance.derivation

`DerivationKind` 具有三种语义状态：

- DIRECT；
- INFERRED；
- UNDETERMINED。

§17/§13 已定义的 DIRECT / INFERRED 区分保持不变。

DIRECT 表示结构化语义内容忠实来自来源描述、记录或观测的信息。

INFERRED 表示语义内容超出来源直接表达，由 human、模型、规则或分析过程产生推导。

UNDETERMINED 仅表示：derivation 元数据 对 规范化器 / 迁移 pipeline **真实不可用或无法可靠判定**。

UNDETERMINED **MUST NOT** 被解释为：

- 部分直接、部分推断；
- 使用方可以把它当作 DIRECT；
- 生成方 可以在 derivation 已知时跳过分类；
- 一种 confidence level。

新生成规范 PBDL 的生成方如果拥有足够信息判定 DIRECT 或 INFERRED，**MUST NOT** 使用 UNDETERMINED 逃避分类。

旧版迁移在历史元数据不足、无法可靠重建 derivation 时 **MAY** 使用 UNDETERMINED，而 **MUST NOT** 猜测 DIRECT 或 INFERRED。

UNDETERMINED provenance **MUST** 保持至少一条可追踪 来源路径；通常 source 可以是被迁移的 旧版 record / 来源材料。已知的 source、generator、Evidence 信息 **MUST** 被保留，缺失 元数据 **MUST NOT** 被发明。

如果连最小可追踪 来源路径 都不存在，则 规范化 **MUST** 报告 provenance 要求 无法满足，而 **MUST NOT** 仅靠 UNDETERMINED token 伪造 provenance completeness。

UNDETERMINED 是规范有效的迁移语义，但符合规范的 validator **SHOULD** 产生 provenance-quality warning，以提示 derivation 分类未能恢复。

Tool / generator 的存在本身 **MUST NOT** 决定 derivation。

`DerivationKind` 的规范词法 token 为且仅为：

-`"direct"`
-`"inferred"`
-`"undetermined"`

规范表示 **MUST NOT** 使用 `DIRECT`、`INFERRED`、`UNDETERMINED`、`unknown`、`unspecified`、`mixed` 或其他平行同义词作为序列化 token。

#### 17.8.2 `Provenance.source` 与`generator`

source 表示原始 信息 source / source descriptor。

generator 表示产生、抽取、转换或推导语义结果 的 human / 模型 / 规则 / 分析 agent or 过程 descriptor。

条件不变量：

- DIRECT provenance **MUST** 具有 `source`；
- INFERRED provenance **MUST** have generator；
- UNDETERMINED provenance **MUST** have source；generator **MAY** 存在，例如 迁移 / 转换 过程。

仅有 SourceDescriptor.kind **不足以** 满足 UNDETERMINED 的 traceable source-path 要求。

对于 derivation =`"undetermined"`，除了 source字段必需 之外，还 **MUST** 至少满足以下一项：

1.`source.locator` 存在；
2.`Provenance.evidence` 至少包含一个能够保留 来源材料 的 Evidence 项。

Evidence 项 继续遵守 §17.8.5：`content` /`locator` 至少一个存在。

因此，以下结构 **MUST NOT** 被视为已经满足 traceable source-path 要求：

    {
        "derivation": "undetermined",
        "source": {
            "kind": "legacy_record"
        }
    }

该附加可追踪性要求**只适用于** `"undetermined"`；当前规范 **MUST NOT** 因此把所有 DIRECT provenance 扩大为必须具有 `locator`。

一个 Provenance **MAY** 同时具有 source 与 generator。

例如，LLM 从 EHR 文本忠实抽取 DIRECT 语义时，可以是：

- source = EHR source；
- generator = extraction system；
- derivation = "direct"。

因此 generator 的存在 **MUST NOT** 自动意味着 inferred。

`Provenance` **MUST NOT** 在顶层重新引入无角色的通用 `time : TemporalValue`。

#### 17.8.3 SourceDescriptor

规范 SourceDescriptor：

    SourceDescriptor {
        kind         : SourceKind
        locator?     : string
        display?     : Text
        times?       : SourceTimeEvent[0..*]
    }

SourceDescriptor.kind 为 必需，并使用以下规范lowercase tokens：

-`"patient_self_report"`
-`"questionnaire"`
-`"clinician_documentation"`
-`"ehr_record"`
-`"device_observation"`
-`"legacy_record"`
-`"other"`

`locator` 为可选非空字符串，用于保存 source-system external identifier / locator。它不是 PBDL Core 引用，也不加入 `EntityId` 命名空间。

display 为 可选 人类可读的 source description。

SourceTimeEvent：

    SourceTimeEvent {
        role : "reported" | "recorded" | "observed"
        at   : TemporalValue
    }

role 与 at 均 必需。

SourceDescriptor.times 的 集合顺序 **MUST NOT** 具有 语义含义。

Source / reporting / recording / observation related time **MUST** 使用 role-显式 SourceTimeEvent；**MUST NOT** 被压回一个 歧义 通用 Provenance 时间。

如果某个时间属于具体 Evidence material 而不是 source descriptor 整体，应由该 Evidence 项 的 times 承载。

#### 17.8.4 GeneratorDescriptor

规范 GeneratorDescriptor：

    GeneratorDescriptor {
        kind        : GeneratorKind
        identifier? : string
        version?    : string
        display?    : Text
        times?      : GeneratorTimeEvent[0..*]
    }

GeneratorDescriptor.kind 为 必需，并使用以下规范lowercase tokens：

-`"human"`
-`"llm"`
-`"rule_engine"`
-`"analytic_model"`
-`"migration_process"`
-`"other"`

identifier、version、display 均 可选；若 identifier / version 存在，值 **MUST** 为 非空 string。

GeneratorDescriptor identifier 不是 PBDL Core EntityId，也不建立 Participant 身份。

GeneratorTimeEvent：

    GeneratorTimeEvent {
        role : "extracted" | "generated" | "transformed" | "migrated"
        at   : TemporalValue
    }

role 与 at 均 必需。

GeneratorDescriptor.times 的 集合顺序 **MUST NOT** 具有 语义含义。

Extraction / generation / 转换 / 迁移 related time **MUST** 使用 role-显式 GeneratorTimeEvent。

GeneratorDescriptor 的存在 **MUST NOT** 自动把 derivation 判为`"inferred"`。

#### 17.8.5 Evidence

规范 Evidence：

    Evidence {
        kind      : EvidenceKind
        content?  : Text
        locator?  : string
        times?    : SourceTimeEvent[0..*]
    }

Evidence.kind 为 必需，并使用以下规范lowercase tokens：

-`"text_excerpt"`
-`"document_reference"`
-`"questionnaire_response"`
-`"device_observation"`
-`"legacy_material"`
-`"other"`

`content` 与 `locator` 均可选，但一个 `Evidence` **MUST** 至少提供二者之一。

如果 locator 存在，其值 **MUST** 为 非空 string。

`content` 用于内联人类可读的 excerpt / response；`locator` 用于外部材料定位。二者 **MAY** 同时存在。

`Evidence.content` 使用 §8.1 的 `Text` 契约，因此 empty / whitespace-only `content` 无效。

Evidence.times **MAY** 使用 SourceTimeEvent 保存只属于该 evidence 项 的 报告的 / recorded / 观测的 time。

如果同一个 source-related time 已由更具体 Evidence 项 承载，规范表示 **SHOULD NOT** 为了方便而无语义区别地同时复制到 SourceDescriptor.times。

Evidence 继续：

- no 必需 身份；
- embedded under Provenance；
- **MUST NOT** 与 Annotation 合并；
- **MUST NOT** 要求复制完整 EHR / source 文档 进入 PBDL Core。

#### 17.8.6 Provenance.confidence

如果规范 Core 需要保留 confidence，其规范字段位置为可选的 `Provenance.confidence`。

Confidence **MUST NOT** 成为 Behavior / Preference / Relation intrinsic truth 字段。

DIRECT self-report **MUST NOT** 被迫填写 `Confidence`。

最小规范表示如下：

    Confidence {
        value  : number
        metric : string
        scale? : {
            min : number
            max : number
        }
    }

value 与 metric 必需。

scale 可选。

value、scale.min、scale.max 若存在都 **MUST** 是 有限 number；NaN、positive infinity、negative infinity 不属于规范Confidence。

metric **MUST** 为 非空 string，并承担“该数字衡量什么”的语义标识责任。

Core 不定义 confidence metric 词汇，但生成方 **MUST NOT** 因 `value` 恰好落在 0..1 就自动解释为 probability。

如果 scale 存在：

- min 与 max 必需；
- min **MUST** strictly less than max；
- value **MUST** 落在 inclusive range [min,max]。

scale 可以省略；这允许表达 range 尚未定义或本来无 bounded range 的 模型 score / human certainty measure。

### 17.8.6.1 `Confidence` 典型边界情况

- calibrated probability：可用明确 metric，例如 生成方-defined`"probability"`，并可声明 scale {min:0,max:1}；
- uncalibrated 模型 score：metric 必须说明是何种 score；**MUST NOT** 因 0..1 range 自动称为 probability；
- human annotation certainty：可使用与 模型 score 不同的 metric；
- 旧版 `confidence_score`：只有在其 metric 含义可恢复/支持时才可规范化为 `Confidence`；
- score range 未知：允许省略 scale，但 metric 仍 必需。

旧版 `confidence_score` 若没有可支持的 metric 含义，**MUST NOT** 通过发明 `metric` 或 `scale` 被迁入规范 `Confidence`。原始旧版材料可以按实际来源通过 `Evidence` / `Annotation` 或 Core 外迁移报告保真保存。

当前规范不设计 校准 框架、阈值 策略 或 统计 解释。

### 17.8.6.2 `Confidence` 相等性

两个 `Confidence` 语义等价，当且仅当：

- `metric` 字符串精确相同；
- `value` 数值严格相等；
- `scale` 同时缺失，或双方 `scale.min` 与 `scale.max` 分别数值严格相等。

`Confidence` 相等性 **MUST NOT** 使用隐式浮点容差、舍入容差或统计等价。

JSON number 的不同词法写法如果表示同一有限数学数值，可以在数值语义上相等；当前规范不要求保留 number 的词法写法作为 confidence 信息。

### 17.9 Annotation

规范 `Annotation` 的最小字段如下：

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| text | Text | 1 | 必需 |
| provenance | Provenance | 1..* | 必需 |

Annotation：

- 不要求 id；
- 不是 Relation 端点；
- 不进入独立的文档级集合；
- 作为轻量嵌入结构附着于当前允许的规范断言或对象。

§17 允许：

- Behavior.annotations；
- Preference.annotations；
- Relation.annotations。

§17 不增加 Subject.annotations。

每个 `Annotation` **MUST** 具有自己的 `provenance[1..*]`，从而区分来源承载、人工撰写与模型生成的 annotation。

当 source / generator / derivation 不同时，所属对象的 `provenance` **MUST NOT** 自动替代 `Annotation.provenance`。

`Annotation.text` 使用 §8.1 的 `Text` 约束。

`Annotation` 的内容相等与完整规范信息相等见 §22.9.2；`Annotation` 文本或 `provenance` 差异 **MUST NOT** 改变所属实体身份。

### 17.10 嵌套限定信息的 `provenance` 继承与相等性

所属对象层级的 `provenance` 描述所属对象断言。

`BehaviorFrequency` / `BehaviorFactor` / `Context` 共用以下局部 `provenance` 字段契约；§8.3 的 `BehaviorFrequency` 与 §8.5–§8.6 的 `Context` / `BehaviorFactor` 均复用该契约：

    provenance? : Provenance[1..*]

该字段整体可选；一旦存在，集合 **MUST** 至少包含一个 `Provenance`。显式空集合 `provenance: []` **MUST NOT** 用来表示继承。

#### 17.10.1 省略局部 `provenance`

嵌套语义限定信息 **MAY** 省略局部 `provenance`，**仅当**该限定信息的来源语义与直接所属对象对它适用的完整来源集合一致。

省略局部 `provenance` 表示动态继承直接所属对象当前适用的完整来源集合。

规范序列化文档 **MUST NOT** 依赖不可见的历史快照来解释省略的局部 `provenance`。

因此，如果所属对象的 `provenance` 从 {P1,P2} 修改为 {P1,P2,P3}，而限定信息继续省略局部 `provenance`，则新文档中该限定信息继承的来源语义也变为 {P1,P2,P3}。

如果转换要求限定信息继续只由旧集合 {P1,P2} 支持，则所属对象增加 P3 时，该限定信息 **MUST** 显式写出局部 `provenance`。

#### 17.10.2 显式局部 `provenance`

如果限定信息：

- source 不同；
- generator 不同；
- derivation 不同；
- 或仅由所属对象 `provenance` 的真子集支持；

则该限定信息 **MUST** 携带显式局部 `provenance`。

当局部 `provenance` 存在时，它表示该限定信息的完整来源集合，并完全覆盖继承。

规范模型 **MUST NOT** 支持“继承所属对象 `provenance` + 添加局部 `provenance`”的叠加式混合合并语义。

#### 17.10.3 `Provenance` 语义相等

两个 `Provenance` 只有在以下具体维度均语义等价时，才允许视为语义等价：

1. `derivation` token 相同；
2. `source` 都缺失，或 `SourceDescriptor` 语义等价；
3. `generator` 都缺失，或 `GeneratorDescriptor` 语义等价；
4. `evidence` 集合按顺序无关比较判定为语义等价；
5. `confidence` 同时缺失，或按 §17.8.6.2 的 `Confidence` 相等性判定为语义等价。

`SourceDescriptor` / `GeneratorDescriptor` / `Evidence` 的语义相等基于其具体字段：

- 标量字段和 token 字段的值相同；
- `Text` 字段按 §8.1 的精确 Unicode 标量值序列相等；
- `TemporalValue` 字段按 §8.2.5 的规范信息相等；
- 可选字段同时缺失，或值语义等价；
- `times` 集合采用顺序无关比较，其中 time-event 的 `role` 必须相同，`at` 必须按 `TemporalValue` 相等；
- `Evidence` 集合采用顺序无关比较；
- `Confidence` 按 §17.8.6.2 比较。

集合比较采用一一语义匹配；集合顺序 **MUST NOT** 产生语义差异。完整信息相等的 `provenance` / `evidence` / time-event 重复项按 §22.8 进行规范化。

#### 17.10.4 规范化

限定信息省略局部 `provenance` 并继承所属对象集合 {P1...Pn}，与显式局部 `provenance` 恰为同一完整语义集合 {P1...Pn} 时，两种表示 **MUST** 被视为语义等价。

规范化 **MUST** 省略与从直接所属对象继承得到的完整来源集合语义等价的冗余显式局部 `provenance`。

因此：

- 所属对象 {P1}，子项省略；
- 所属对象 {P1}，子项显式 {P1}；

二者语义等价，且规范形为子项省略 `provenance`。

同理，所属对象 {P1,P2}、子项显式 {P1,P2} 时，必须规范化为省略局部 `provenance`。

`Provenance` 集合顺序 **MUST NOT** 产生语义差异。

`TemporalValue`、`Text` 与 `Confidence` 的相等性已经定义，因此 `Provenance` 语义相等不再因这些叶类型未定义而受阻。

`Provenance` 的语义相等与规范化均为顺序无关；字节级确定性顺序不属于语义含义，明确留给未来的确定性序列化规范，见 §22.11。

#### 17.10.5 范围

上述继承、覆盖、相等性与规范化语义统一适用于：

- BehaviorFrequency；
- BehaviorFactor；
- Context；
- TemporalExtent。

`TemporalExtent` 的局部 `provenance` **采用同一机制**，不另建时间专用的来源信息系统。

规范模型 **MUST NOT** 用单一所属对象层级的 DIRECT / INFERRED / UNDETERMINED 标签粗暴覆盖内部 `derivation` 实际不同的嵌套限定信息，也 **MUST NOT** 把所属对象中不支持该限定信息的 `provenance` 错误继承给它。

### 17.11 具有实体身份的对象与嵌入结构

§17 保持身份边界：

- Subject：必需 身份；
- Behavior：必需 身份；
- Preference：必需 身份；
- Relation：no 必需 身份。

以下 §17 named structures 不获得 必需 身份，不加入 Subject / Behavior / Preference 文档内身份命名空间，也不是 Relation 端点：

- TemporalExtent；
- BehaviorFrequency；
- Context；
- BehaviorFactor；
- Annotation；
- Provenance；
- Evidence。

PBDLDocument 是规范root container，不因本节获得 entity身份语义。

### 17.12 规范字段归属取代旧版平行字段

规范模型 **MUST NOT** 同时保留以下平行 mechanisms：

| 规范字段归属 | **MUST NOT** 与规范字段并存的旧版平行字段 |
|---|---|
| Behavior.type | Behavior.behavior_type |
| Preference.category | Preference.preference_category |
| Preference.value | Preference.preference_value |
| Behavior.annotations | Behavior.reasoning_note |
| Preference.annotations | Preference.note |
| Relation | Preference.associated_behavior |
| Provenance | Behavior.evidence_source |
| Provenance | Preference.source_type |
| Context / Behavior / Provenance / 应用层 according to语义| Behavior.communication_status |

旧版输入 **MAY** 被迁移，但规范输出 **MUST** 只使用 §17 规定的字段归属。

### 17.13 明确不属于规范 Core 的字段

以下 旧版字段**MUST NOT** 进入 PBDL-Core 规范对象 模型：

- Behavior.risk_tag → 派生 / 应用 结果；
- Behavior.validity_flag → validator / report output；
- Preference.preference_conflict_flag → 派生 ConflictAnalysis / 应用 结果；
- Relation.weight → 派生 / 分析 工件；
- 所有 Treatment Path / Pathway字段→ 扩展 / 应用层。

这些字段**MUST NOT** 为了历史兼容被重新塞回规范Core。

### 17.14 仍待定义的能力

身份、引用、actor、source、generator 与 evidence 基础类型已经定义。

`Text`、`TemporalValue`、`TemporalExtent` 局部 `provenance`、`Coding`、`Confidence` 与相关相等性基础已经定义。

§8.3–§8.4 已定义 `BehaviorFrequency` 与 `PreferenceValue`。

§8.5–§8.6 已定义：

- Context；
- `ContextValue` 的 coded / text 联合类型；
- `Context` 内容相等与完整限定信息相等；
- FactorRole；
- FactorDirection；
- `FactorValue` 的 coded / text 联合类型；
- BehaviorFactor；
- `BehaviorFactor` 内容相等与完整限定信息相等；
- `Context`、`BehaviorFactor` 与 `Relation` 的判定边界。

主要业务复合语义类型已经定义。

以下能力仍留待后续规范定义：

- 类型兼容与转换细节；
- 规范全局序列化顺序；
- 规范性 `Relation` 词汇与逆关系约定；
- JSON Schema 集成；
- DSL / EBNF 语法；
- 实现。

当前章节不定义这些后续能力。

## 18. 校验模型

完整校验架构尚未定义。

未来的校验模型预计至少需要区分结构合法性与语义合法性，但具体分层、严重级别模型、错误码与实现仍为 **TODO**。

已定义的最小校验后果包括：

- 旧版迁移因历史元数据真实不足而使用 `"undetermined"`，可以形成规范有效的 provenance；
- 符合规范的 validator **SHOULD** 对 `"undetermined"` 产生 provenance-quality 警告；
- 生成方已掌握足够 derivation 信息却使用 `"undetermined"`，属于语义不符合；
- 缺少 §17.8 所要求的可追踪来源路径时，`"undetermined"` **MUST NOT** 使 provenance 要求自动变为已满足；
- `Text` 必须满足 §8.1 的非空白内容规则；
- `TemporalValue` 必须满足 §8.2 的词法、Gregorian 日期与 offset 有效性；
- `Interval` 的 start/end 在 §8.2.6 可判定 start 明确晚于 end 时必须无效；
- `TemporalExtent` 的显式局部 `provenance` 必须满足 §17.10 的完全覆盖与禁止叠加合并规则；
- `Coding` 的必需与非空约束必须满足 §15；
- `Confidence` 必须满足有限数值、`metric` 与可选 `scale` 范围规则；
- `BehaviorFrequency` 必须满足 §8.3 的变体判别、count/rate/period 与 recurrence 集合规则；
- `BehaviorFrequency` 的定量 `precision` 必须显式为 `"exact"` 或 `"approximate"`；
- `RateFrequency` 缺少 `period` 必须无效；
- `RecurrenceFrequency` 的 weekday 重复项、非法 period/day schedule 组合必须无效；
- `PreferenceValue` 必须满足 §8.4 的带标签联合类型判别；
- `NumericPreferenceValue.value` 必须有限，`operator` 必须为允许的 token，`unit` 若存在必须为有效 `Coding`；
- `Context` 必须满足 §8.5 的 coded/text 带标签联合类型判别；
- 完整信息相等的 `Context` 重复项不得在规范 `context` 集合中重复保留；
- `BehaviorFactor` 的 `role` / `direction` / factor 变体必须满足 §8.6；
- `antecedent` 与 `reported_reason` 的 `direction` 必须为 `factor_to_behavior`；
- inferred explanatory factor 若不能与所属对象的 `provenance` 保持相同 derivation / applicable set，必须显式写出局部 `provenance`；
- `BehaviorFactor` 指向已有 Core 实体的显式类型化关系必须使用 `Relation`，不得通过 factor text/code 规避。

当前规范不定义 Validator 实现。

§22.13 将当前条件不变量分为 STRUCTURAL / REFERENCE / SEMANTIC / NORMALIZATION / VOCABULARY，以明确 JSON Schema、resolver、语义 validator 与规范化器之间的职责边界；本节不定义 Validator 实现。

## 19. 扩展机制

扩展机制尚未设计。

Treatment Pathway **MAY** 在未来作为扩展或上层应用进行设计，但当前不属于 PBDL-Core。

规范 Core 对象使用封闭字段集合。未定义或未知字段 **MUST NOT** 被静默接受为 Core 字段，也 **MUST NOT** 仅因为名称看似扩展字段就获得扩展语义。

未来扩展 **MUST** 使用未来显式定义的扩展机制；任意未知 JSON property 不是扩展机制。

**TODO：** 定义扩展命名空间或标识方式、兼容规则、扩展发现机制，以及扩展如何参与 Core 校验且不得静默改写 Core 语义。

## 20. 示例

当前尚未编写规范性或非规范性示例。

示例目录已预留：

-`examples/valid/`
-`examples/invalid/`

**TODO：** 仅在相应语法和语义确定之后添加示例。

## 21. 版本与兼容性

目标规范版本为 PBDL 1.0。

兼容性模型尚未定义。

**TODO：** 定义语言版本声明、向后 / 向前兼容预期、弃用策略和扩展兼容规则。

## 22. 规范表示与序列化语义

本节规定规范表示、相等性、规范化与顺序边界。

本节不新增业务实体，也不改变前述业务语义；其职责是规定所有具体 Core 类型在可映射为 JSON 的语义模型中的表示、相等性、规范化与顺序边界。

### 22.1 规范类型清单

当前 具体规范type inventory 至少包括以下 named types / token families：

**Root / Core 对象**

- PBDLDocument；
- Subject；
- Behavior；
- Preference；
- Relation；
- Annotation。

**Primitive / lexical / 术语 types**

- VersionToken；
- EntityId；
- Text；
- TemporalValue；
- Coding；
- Confidence。

**引用 / actors**

- SubjectRef；
- CoreEntityRef；
- ExternalActorRef；
- ActorRef。

**Provenance**

- DerivationKind；
- SourceKind；
- SourceDescriptor；
- SourceTimeEvent；
- GeneratorKind；
- GeneratorDescriptor；
- GeneratorTimeEvent；
- EvidenceKind；
- Evidence；
- Provenance。

**Temporal**

- Instant；
- Interval；
- TemporalExtent。

**Frequency**

- QuantitativeFrequencyPrecision；
- FrequencyPeriod；
- Weekday；
- DayPart；
- QualitativeFrequencyToken；
- ObservedCountFrequency；
- RateFrequency；
- RecurrenceFrequency；
- QualitativeFrequency；
- BehaviorFrequency。

**Preference values**

- CodedPreferenceValue；
- TextPreferenceValue；
- BooleanPreferenceValue；
- NumericPreferenceValue；
- PreferenceValue。

**Context**

- CodedContextValue；
- TextContextValue；
- ContextValue；
- Context。

**Behavior factors**

- FactorRole；
- FactorDirection；
- CodedFactorValue；
- TextFactorValue；
- FactorValue；
- BehaviorFactor。

这些类型的业务字段与 token 集合继续由 §§8、15、17 规定。§22 **MUST NOT** 通过表示规则增加新的业务字段或变体。

### 22.2规范Core 对象闭包与未知字段

每个 具体规范Core对象/ embedded 结构化对象的字段set 是 **closed**。

对象只允许其 具体 type 定义的 字段。

未知 字段、拼写错误 字段、历史 旧版 alias 或尚未定义的 扩展 property **MUST NOT** 出现在规范Core 表示。

例如以下 旧版字段**MUST NOT** 与规范字段 平行存在：

-`behavior_type`；
-`temporal_scope`；
-`evidence_source`；
-`communication_status`；
-`reasoning_note`；
-`risk_tag`；
-`validity_flag`；
-`preference_category`；
-`preference_value`；
-`source_type`；
-`confidence_score`；
-`associated_behavior`；
-`note`；
-`preference_conflict_flag`；
- Relation.`weight`。

未知 property **MUST NOT** 被当作扩展。未来扩展必须使用 §19 所述未来显式扩展机制。

### 22.3 缺失、`null` 与空集合

#### 22.3.1 可选标量与对象字段

规范 Core 表示使用**字段省略**表示可选字段缺失。

当前没有任何已定义的 Core 类型把 JSON `null` 作为语义值。

因此，规范 Core 表示中：

- 可选字段缺失 → 表示未提供该可选语义值；
- `field: null` → **无效的规范 Core 表示**。

该规则适用于 `executor`、`temporal`、`source`、`generator`、`confidence`、`locator`、`display`、`identifier`、`version`、`role`、`unit`、`window`、`day_part`、`times_per_period`、`start` / `end` 等所有可选字段。

#### 22.3.2 必需根集合

`PBDLDocument` 根集合保持 §17 的规则：

- `subjects` 必需，至少 1 项；
- `behaviors` 必需，可为空；
- `preferences` 必需，可为空；
- `relations` 必需，可为空。

必需根集合 **MUST NOT** 通过省略表示为空。

#### 22.3.3 可选集合

除必需根集合与必需 `provenance` 集合外，可选集合没有元素时，规范形 **MUST** 省略该字段。

可选集合的空集合规则由该字段自身声明的基数控制：

- 基数 = `0..*` 且字段存在但为 `[]` → **MAY** 是语义有效、但需要规范化的表示；规范形 **MUST** 省略该字段；
- 基数 = `1..*` 且字段存在但为 `[]` → **无效**，不得通过省略修复基数违例。

因此，以下普通 `0..*` 可选集合显式为空时不是规范形，并 **MAY** 规范化为省略：

    annotations: []
    contexts: []
    factors: []
    frequencies: []
    evidence: []
    times: []

`days_of_week` 已由 §8.3.5 定义为存在时至少 1 项，因此：

    days_of_week: []

这是**无效**表示，不是需要规范化的表示。

局部限定信息的 `provenance` 同样是存在时 `1..*`；此外，省略具有来源继承语义。因此显式局部 `provenance: []` **MUST** 视为语义无效，而 **MUST NOT** 规范化为省略。

任何必需的 `provenance : Provenance[1..*]` 集合为空也同样无效。

### 22.4 带标签联合类型的机械判别

规范 union **MUST** 能机械、唯一判定 变体；implementation **MUST NOT** “猜哪个更像”。

| 联合类型 | 变体 | 必需判别字段 | 允许的变体字段 |
|---|---|---|---|
| ActorRef | SubjectRef |`ref` |`ref` only |
| ActorRef | ExternalActorRef |`kind` = person/device/software/other |`kind, external_id?, display?, role?` |
| TemporalExtent | Instant |`kind="instant"` |`kind, at, provenance?` |
| TemporalExtent | Interval |`kind="interval"` |`kind, start?, end?, provenance?` |
| BehaviorFrequency | ObservedCountFrequency |`kind="observed_count"` |`kind,count,precision,window?,provenance?` |
| BehaviorFrequency | RateFrequency |`kind="rate"` |`kind,value,period,precision,provenance?` |
| BehaviorFrequency | RecurrenceFrequency |`kind="recurrence"` |`kind,period,precision,times_per_period?,days_of_week?,day_part?,provenance?` |
| BehaviorFrequency | QualitativeFrequency |`kind="qualitative"` |`kind,value,provenance?` |
| PreferenceValue | CodedPreferenceValue |`kind="coded"` |`kind,value` |
| PreferenceValue | TextPreferenceValue |`kind="text"` |`kind,value` |
| PreferenceValue | BooleanPreferenceValue |`kind="boolean"` |`kind,value` |
| PreferenceValue | NumericPreferenceValue |`kind="number"` |`kind,operator,value,unit?` |
| ContextValue | CodedContextValue |`kind="coded"` |`kind,value` |
| ContextValue | TextContextValue |`kind="text"` |`kind,value` |
| FactorValue | CodedFactorValue |`kind="coded"` |`kind,value` |
| FactorValue | TextFactorValue |`kind="text"` |`kind,value` |

由于 §22.2 closed-字段 规则，变体 之外的 conflicting字段无效。

ActorRef 使用 structural discrimination：`ref` 与`kind` **MUST NOT** 共存。

其他 unions 使用 必需`kind` token；missing / 未知 discriminator 无效。

### 22.5 规范字段名规则

规范字段名只使用当前具体对象定义中规定的名称。

同一语义 **MUST NOT** 同时存在规范name 与 旧版 alias。

规范化器可以在 Core 外的旧版输入层识别历史字段，但形成规范 Core 对象后必须只保留规范字段归属。

§22 不设计 旧版 解析器。

### 22.6 通用语义字符串一致性

Text、EntityId、VersionToken、TemporalValue 与 enum/token 字段继续使用各自专门 词法约束。

对于其他定义为非空 `string` 且承担 identifier / locator / code / metric / version 语义的字段，采用统一的**语义字符串**规则：

> value **MUST** 包含至少一个不属于 Unicode White_Space property 的 code point。

该规则至少适用于：

- Coding.system；
- Coding.code；
- Coding.version（存在时）；
- ExternalActorRef.external_id.system；
- ExternalActorRef.external_id.value；
- SourceDescriptor.locator；
- GeneratorDescriptor.identifier；
- GeneratorDescriptor.version；
- Evidence.locator；
- Confidence.metric。

因此 whitespace-only string（例如`"   "`）**MUST NOT** 满足这些字段的 非空 要求。

规范化 **MUST NOT** 自动 trim、case-fold 或对这些字符串做 Unicode 规范化。

这些语义strings 的 相等性 使用 精确 Unicode scalar-value sequence 相等性；specialized type 已定义更严格 lexical/相等性 规则 时，以 specialized 规则 为准。

### 22.7 数值一致性

规范数值语义使用数学数值，而不保存 JSON number 的词法写法。

因此，在允许 number 的字段中：

    1
    1.0
    1e0

表示相同的数学数值。

`-0` 与 `0` 在数值语义相等中相等。

§22 **MUST NOT** 使用模糊容差、隐式舍入容差或统计等价。

各字段的具体约束保持不变：

- `FrequencyPeriod.value`：数学整数，>= 1；
- `ObservedCountFrequency.count`：数学整数，>= 0；
- `RecurrenceFrequency.times_per_period`：存在时为数学整数，>= 1；
- `RateFrequency.value`：有限数值，>= 0；
- `NumericPreferenceValue.value`：有限数值；
- `Confidence.value` / `scale.min` / `scale.max`：有限数值；
- `Confidence.scale` 存在时 `min < max` 且 `value ∈ [min,max]`。

JSON number 的词法规范化与确定性写法属于未来的确定性序列化规范，不属于语义相等。

### 22.8 集合语义与重复项规则

当前 Core 数组/集合的顺序 **MUST NOT** 隐式表达优先级、身份、因果关系、时间顺序、排序级别或生命周期。

规范集合分为以下类别：

| 集合类别 | 示例 | 语义顺序 | 重复项规则 |
|---|---|---|---|
| 具有身份的实体集合 | subjects / behaviors / preferences | 无 | 重复 `EntityId` 无效；共享命名空间必须唯一 |
| `Relation` 集合 | relations | 无 | 完整信息相等的重复项需要规范化；`Relation` 相等性受类型方向性契约控制；仅端点相同绝不自动去重 |
| 断言来源集合 | Behavior/Preference/Relation/Annotation.provenance | 无 | 完整信息相等的重复项需要规范化 |
| `Evidence` 集合 | Provenance.evidence | 无 | 完整信息相等的重复项需要规范化 |
| `Annotation` 集合 | Behavior/Preference/Relation.annotations | 无 | 完整信息相等的重复项需要规范化 |
| 嵌套限定信息集合 | frequencies / contexts / factors | 无 | 完整限定信息相等的重复项需要规范化 |
| token 集合 | RecurrenceFrequency.days_of_week | 无 | token 重复无效 |
| 时间事件集合 | SourceDescriptor.times / GeneratorDescriptor.times / Evidence.times | 无 | 完整信息相等的事件重复项需要规范化 |

“需要规范化”表示语义内容可以理解，但规范形 **MUST** 移除冗余的完整信息相等重复项。

不同 `provenance`、不同 `Annotation.provenance`、不同 factor role/direction、不同 temporal provenance、不同 `Relation.type`/temporal/provenance 等导致完整规范信息不同的项 **MUST NOT** 被机械去重。

`Relation` 重复项检测 **MUST** 使用 §22.9.3 的类型契约感知相等性。对于对称/非定向关系类型，交换端点后若其余断言内容与完整信息相等，可以构成重复项；对于有向类型，端点顺序具有语义。若适用的 `Relation.type` 方向性契约不可用，规范化器 **MUST NOT** 自行猜测、交换、规范化或据此去重端点。

### 22.9 相等性层级

§22 明确区分：

- 身份相等；
- 语义内容相等；
- 完整规范信息相等。

不同类型只使用对其有意义的层级。

#### 22.9.1 `TemporalExtent` 相等性

`TemporalExtent` **内容相等**：

- `kind` 必须相同；
- `Instant.at` 使用 `TemporalValue` 规范信息相等；
- `Interval.start` / `end` 必须分别同时缺失，或分别按 `TemporalValue` 相等；
- `provenance` 不参与内容相等。

`TemporalExtent` **完整规范信息相等**：

1. 内容相等；
2. 有效来源集合语义等价。

有效来源信息依 §17.10 在所属对象环境中计算。

#### 22.9.2 `Annotation` 相等性

`Annotation` **内容相等**只比较 `text`，使用 §8.1 的 `Text` 相等性。

`Annotation` **完整规范信息相等**要求：

1. `text` 内容相等；
2. `Annotation.provenance` 集合语义等价。

完整信息相等的 `Annotation` 重复项需要规范化。

`Annotation` 相等性 **MUST NOT** 改变其所属实体身份。

#### 22.9.3 `Relation` 相等性

`Relation` **断言内容相等**受适用的 `Relation.type` 语义契约控制。

共同要求：

- `type` 使用 `Coding` 规范信息相等；
- `temporal` 同时缺失，或 `TemporalExtent` 内容相等。

端点相等要求：

A. 对**有向关系类型**：

- `source` 的 `CoreEntityRef` 必须与 `source` 相等；
- `target` 的 `CoreEntityRef` 必须与 `target` 相等；
- 端点顺序具有语义。

B. 对**对称/非定向关系类型**：

- `source` / `target` 端点对按无序对比较；
- 在同一对称/非定向关系类型下，A-B 与 B-A **MUST NOT** 仅因端点顺序不同而被判为不同的关系语义。

C. 若适用的 `Relation.type` 方向性契约不可用：

- 相等性引擎/规范化器 **MUST NOT** 自行猜测关系方向性；
- **MUST NOT** 自行交换或规范化端点；
- 交换端点后的相等性/去重 **MUST** 等待适用的 `Relation` 词汇契约。

`Relation` **完整规范信息相等**要求：

1. `Relation` 断言内容相等；
2. `temporal` 同时缺失，或 `TemporalExtent` 完整信息相等；
3. `Relation.provenance` 集合语义等价；
4. `annotations` 集合按 `Annotation` 完整信息相等进行语义等价比较。

因此：

- 仅端点相同 **MUST NOT** 自动意味着同一个 `Relation`；
- 仅 annotation 不同可以造成完整规范信息不同，但 **MUST NOT** 创建 Core 身份；
- 集合位置 **MUST NOT** 作为 `Relation` 身份；
- 完整信息相等的 `Relation` 重复项属于需要规范化的表示冗余；
- 对称关系交换端点后的相等性/去重同时依赖 **VOCABULARY + SEMANTIC + NORMALIZATION**；通用结构 Schema **MUST NOT** 自行决定。

#### 22.9.4 引用与参与者

`SubjectRef` / `CoreEntityRef` 相等性：`ref` 的 `EntityId` 精确相等。

`ExternalActorRef` 规范信息相等要求：

- `kind` token 相同；
- `external_id` 同时缺失，或 `system + value` 按精确语义字符串相等；
- `display` 同时缺失，或按 `Text` 相等；
- `role` 同时缺失，或按 `Text` 相等。

`ActorRef` 相等性要求变体相同，再使用对应变体的相等性。

#### 22.9.5 `Provenance` 描述结构

`SourceTimeEvent` / `GeneratorTimeEvent` 相等要求 `role` token 相同且 `at` 按 `TemporalValue` 相等。

`SourceDescriptor` 相等要求 `kind`、`locator`、`display` 与 `times` 集合分别语义等价。

`GeneratorDescriptor` 相等要求 `kind`、`identifier`、`version`、`display` 与 `times` 集合分别语义等价。

`Evidence` 相等要求 `kind`、`content`、`locator` 与 `times` 集合分别语义等价。

`Provenance` 相等继续使用 §17.10.3，并受 §22.8 的重复项规范化规则约束。

#### 22.9.6 实体身份相等与规范信息相等

`Subject` / `Behavior` / `Preference` 的**身份相等**仅由文档内 `EntityId` 决定。

相同 `id` **MUST NOT** 自动表示完整规范信息相同。

`Subject` 当前只有 `id`，因此同一 `id` 的规范信息状态在当前模型中相同。

`Behavior` 规范信息相等要求 `id`、`subject`、`type`、`executor`、`temporal`、`frequencies`、`contexts`、`factors`、`provenance`、`annotations` 全部按对应的完整相等/集合相等规则判定为语义等价。

`Preference` 规范信息相等要求 `id`、`subject`、`category`、`value`、`temporal`、`contexts`、`provenance`、`annotations` 全部语义等价。

因此，`Behavior id=b1` 但 temporal / provenance / annotation 等发生改变时：

- 实体身份相同；
- 规范信息状态不同。

#### 22.9.7 `PBDLDocument` 相等性

`PBDLDocument` 规范信息相等要求：

1. `pbdl_version` 相等；
2. `subjects` 集合顺序无关，并可一一匹配规范信息相等的 `Subject`；
3. `behaviors` 集合按 `EntityId` 一一匹配且规范信息相等；
4. `preferences` 集合按 `EntityId` 一一匹配且规范信息相等；
5. `relations` 集合顺序无关，并可一一匹配按 §22.9.3 适用 `Relation.type` 语义契约判定为完整信息相等的 `Relation`；对称/非定向类型的交换端点 **MUST NOT** 仅因顺序不同导致文档不相等。

根数组位置 **MUST NOT** 影响文档语义相等。

### 22.10 规范有效、需要规范化与规范形

规范表示分为三个层次：

**语义有效表示**

满足业务、引用、来源与词法语义，但可能包含纯表示冗余。

**需要规范化的表示**

语义有效，但尚未达到规范形。例如：

- 基数 = `0..*` 的可选集合显式为 `[]`；
- 完整信息相等且无 `id` 的重复项；
- 显式局部 `provenance` 与继承得到的完整集合完全等价；
- 未来序列化器尚未统一 JSON number 写法或数组顺序。

**规范形**

语义有效，并已执行当前规范要求的语义规范化：

- 基数 = `0..*` 的可选空集合已省略；
- 冗余局部 `provenance` 已省略；
- 完整信息相等的冗余无 `id`/嵌入项已去重；
- 不存在旧版别名或未知字段。

以下不是“仅需规范化”，而是无效：

- JSON `null`；
- 未知 Core 字段；
- 显式局部 `provenance: []`；
- 声明基数要求至少 1 项的集合为空（例如 `subjects: []`、`days_of_week: []`、必需/局部 `provenance: []`）；必需根集合 `behaviors` / `preferences` / `relations` 可合法为 `[]`，但 **MUST NOT** 省略；
- 无效的联合类型判别字段；
- 重复 `EntityId`；
- 违反条件不变量。

PBDL 规范文档 **MUST** 达到规范形。

§22 的规范形是**语义规范形**；它不承诺字节级一致的 JSON。

### 22.11 顺序与确定性序列化边界

§22 规定：

> **语义模型中的集合顺序无关；字节级确定性 JSON 序列化延后定义。**

JSON 对象成员顺序 **MUST NOT** 具有语义含义。

当前 Core 中声明为顺序无关的数组，无论输入或序列化器如何排列，只要元素集合按本节相等性规则相同，就具有相同的语义规范信息。

当前规范**不规定**：

- JSON 对象键顺序；
- 实体数组排序；
- 无 `id` 复杂对象的结构排序键；
- JSON number 的词法写法；
- 空白与 pretty-print 规则。

未来的确定性序列化规范 **MUST** 基于当前相等性与规范形规则定义字节级顺序，而 **MUST NOT** 反过来改变 PBDL 语义。

因此，JSON Schema **MAY** 在没有字节级规范 JSON 规则的情况下定义。

### 22.12 跨类型 `Text` 保真回退边界

`TextPreferenceValue`、`TextContextValue`、`TextFactorValue` 都是保真回退，但每种 `Text` 回退只能承载其所属带标签类型自己的语义维度。

#### `Preference` 文本

TextPreferenceValue **MUST NOT** 偷偷承载：

- 关联的 `Behavior` / `CoreEntityRef` 链接；
- `Relation` 语义；
- 当前不支持的 preference-strength 数值语义；
- 其他已经有独立规范归属的机器语义。

#### `Context` 文本

TextContextValue **MUST NOT** 偷偷承载：

- BehaviorFrequency；
- TemporalExtent；
- `BehaviorFactor` 的 reason / antecedent / 解释 语义；
- 工作流状态；
- `Relation` 语义。

例如来源措辞：

> “在家里比较规律”

如果来源语义可以可靠分解：

- “在家里” → Context；
- “比较规律” → BehaviorFrequency；

规范化器 **SHOULD** 分别结构化。

如果某一部分无法可靠结构化，可用 `Evidence` / `Annotation` 保留原始完整措辞；**MUST NOT** 把跨维度的整句作为单一 `Context` 机器值。

#### `Factor` 文本

`TextFactorValue` **MUST NOT** 偷偷承载已有 Core `Behavior` / `Preference` 身份；该关系应使用 `Relation`。

Factor 的 `role` 与 `direction` 也 **MUST NOT** 隐藏在 factor 文本里而省略必需的结构化字段。

### 22.13 规范条件不变量表

| 不变量 | 类别 |
|---|---|
| PBDLDocument.subjects >= 1 | STRUCTURAL |
| behaviors/preferences/relations 根数组必需，可为空 | STRUCTURAL |
| Subject/Behavior/Preference 的 EntityId 在共享命名空间中唯一 | REFERENCE / SEMANTIC |
| EntityId 词法形式 | STRUCTURAL |
| SubjectRef 恰好解析到一个 Subject | REFERENCE |
| CoreEntityRef 恰好解析到一个 Behavior/Preference | REFERENCE |
| ActorRef = ref XOR kind 变体 | STRUCTURAL |
| 可选 Core 字段用省略表示缺失；禁止 null | STRUCTURAL |
| 可选集合基数 0..* 且存在但为空 => 规范形中省略 | NORMALIZATION |
| 可选集合基数 1..* 且存在但为空 => 无效 | STRUCTURAL / SEMANTIC |
| 局部 provenance 存在 => 非空 | STRUCTURAL / SEMANTIC |
| DIRECT => source 必需 | STRUCTURAL（条件） |
| INFERRED => generator 必需 | STRUCTURAL（条件） |
| UNDETERMINED => source 必需 | STRUCTURAL（条件） |
| UNDETERMINED => source.locator 或包含来源材料的 Evidence | STRUCTURAL + SEMANTIC |
| Evidence => `content` 或 `locator` | STRUCTURAL（条件） |
| Interval => start 或 end | STRUCTURAL（条件） |
| 可比较的 Interval 中 start 明确晚于 end => 无效 | SEMANTIC |
| Confidence.scale 存在 => min < max 且 value 位于范围内 | SEMANTIC / 数值型 |
| FrequencyPeriod.value 为整数且 >= 1 | STRUCTURAL |
| ObservedCount.count 为整数且 >= 0 | STRUCTURAL |
| Rate.value 有限且 >= 0，并且 period 必需 | STRUCTURAL |
| Recurrence.times_per_period 存在 => 整数且 >= 1 | STRUCTURAL |
| days_of_week 存在 => 非空、无重复，period=1 week，times_per_period 缺失 | STRUCTURAL + SEMANTIC |
| NumericPreference.value 有限且 operator 为允许 token | STRUCTURAL |
| 有量纲 NumericPreference 的来源提供 unit => 保留 unit | SEMANTIC（规范化） |
| Context/Factor/Frequency/Temporal 的局部 provenance 不同或仅为子集 => 显式局部 provenance | SEMANTIC |
| 冗余局部 provenance == 继承的完整集合 => 省略 | NORMALIZATION |
| reported_reason => direction=factor_to_behavior | STRUCTURAL（条件） |
| antecedent => direction=factor_to_behavior | STRUCTURAL（条件） |
| 解释性 factor 由模型推断且超出来源 => effective derivation=inferred | SEMANTIC |
| BehaviorFactor 表达已有 Core 实体关系 => Relation | SEMANTIC |
| Context 与 Factor 的分类遵循来源语义 | SEMANTIC |
| Relation.type Coding structure | STRUCTURAL |
| Relation.type 的端点角色/方向性/因果契约 | VOCABULARY + SEMANTIC |
| Relation 对有向与对称端点顺序的相等规则 | VOCABULARY + SEMANTIC |
| 对称关系交换端点后的重复项移除 | VOCABULARY + SEMANTIC + NORMALIZATION |
| 完整信息相等的嵌入式/无 id 重复项 => 规范形中去重 | NORMALIZATION |
| 未知 Core 属性 | STRUCTURAL invalid |
| Text 回退跨语义维度泄漏 | SEMANTIC（规范化） |

类别含义：

- **STRUCTURAL**：JSON Schema 可以直接表达全部或主要结构；
- **REFERENCE**：需要文档范围的 resolver；
- **SEMANTIC**：需要语义 validator / 规范化器读取跨字段信息或来源支持的语义；
- **NORMALIZATION**：属于规范化器职责，不应假装由 Schema 解决语义等价；
- **VOCABULARY**：依赖术语或 `Relation` 词汇契约。

### 22.14 `Relation` 词汇职责边界

`Relation.type` 已是 `Coding`，因此 JSON Schema 可以验证其 `Coding` 结构。

通用 JSON Schema **MUST NOT** 被要求独立决定某个 relation code 的以下语义：

- 允许哪些端点角色或类型；
- 是否有向或对称；
- 逆关系约定；
- 因果语义状态；
- 交换端点后是否断言内容相等或可去重。

对称/非定向关系中的 `Relation` 相等与交换端点去重属于 **VOCABULARY + SEMANTIC + NORMALIZATION**。通用 JSON Schema **MUST NOT** 自行判断关系是否对称，也 **MUST NOT** 自行交换或规范化端点。

这些能力属于专门的 `Relation` 词汇、语义校验与规范化职责。

当前规范不定义具体 relation code。

### 22.15 JSON Schema 前置条件

JSON Schema 可以在不重新猜测 Core 对象结构的前提下定义，因为以下前置条件已经明确：

1. 所有具体 Core 对象的字段、必需/可选属性与基数；
2. `EntityId` / `Text` / `TemporalValue` / `Coding` / 数值的基础词法约束；
3. Core 字段封闭规则；
4. 缺失与 `null` 规则；
5. 必需根集合与可选集合的空集合规则；
6. 联合类型判别字段与变体字段闭包；
7. 结构性条件不变量；
8. 引用字段及引用解析职责；
9. 语义内容相等与完整规范信息相等；
10. 重复项与规范化边界；
11. 顺序无关的语义集合规则；
12. 未知字段与扩展边界；
13. Schema 无法承担的语义、规范化与词汇职责已明确分类。

JSON Schema **MUST NOT** 尝试替代以下职责：

- 引用解析；
- 来源支持的语义判断；
- `Context` 与 `Factor` 的规范化；
- `provenance` 语义相等；
- 冗余 `provenance` / 重复项的语义规范化；
- `Relation` 词汇的端点、方向与因果校验。

### 22.16 仍待定义的表示能力

以下表示层能力仍待定义，但不阻塞结构 Schema：

- 未来的确定性字节级 JSON 序列化规范；
- 规范数组排序/对象键顺序规范；
- 通用类型转换/强制转换规则；
- 共享 `Provenance` 身份/池（若未来出现真实需要）；
- provenance chaining；
- 专门的 `Relation` 词汇、逆关系约定与因果状态定义；
- 扩展机制；
- DSL / EBNF 语法；
- 解析器 / validator / 运行时 实现；
- 规范性示例。

这些项目都有明确的职责边界；它们 **MUST NOT** 被解释为当前 Core 对象结构仍未确定。

## 附录 A：语法

当前语法占位文件位于 [`grammar/pbdl.ebnf`](grammar/pbdl.ebnf)。

当前语法有意保持不完整。

## 附录 B：校验错误码

**TODO：** 在校验语义确定后定义错误码体系。

当前不存在规范性错误码。

## 附录 C：保留关键字

**TODO：** 在词法结构与具体语法确定后定义保留关键字。

当前不存在规范性的 DSL 关键字。

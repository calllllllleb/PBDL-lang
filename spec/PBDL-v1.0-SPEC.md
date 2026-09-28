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
- `Provenance`（来源追踪）
- Evidence（证据）
- Relation（关系）

`Behavior` 与 `Preference` 是 PBDL-Core 的主要研究对象。

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

本规范使用中文规范强度词表达一致性要求；其英文对应关系如下。

- **必须（MUST）**：绝对要求，符合规范的实现或文档必须满足。
- **不得（MUST NOT）**：绝对禁止，符合规范的实现或文档不得违反。
- **应（SHOULD）**：强烈建议，仅在存在充分理由时可以偏离。
- **不应（SHOULD NOT）**：强烈不建议，仅在存在充分理由时可以采用。
- **可以（MAY）**：可选能力，可以实现，也可以不实现。

只有在相关语言构造已经被正式定义时，这些规范性要求才具有确定含义。任何标记为 `TODO` 的未决语法或字段名，都不得因为示例、占位文件或实现习惯而被视为已经标准化。

## 4. 设计原则

### 4.1 声明式表示

PBDL-Core 必须用于描述信息，而不是规定执行行为。

### 4.2 来源陈述与派生结果分离

PBDL-Core 必须区分来源直接描述的信息与外部系统推断、分析或计算得到的信息。

PBDL 表示“某个来源怎样描述、记录、观测或推断了某项 `Behavior` / `Preference` 信息”，但 PBDL-Core 本身不得因为信息被写入 PBDL，就宣称该信息在现实世界中已经被认证为绝对真实。

例如，患者自述“每天都按时服药”与设备或记录显示“过去一周存在漏服”可以同时被表示；PBDL-Core 不自动裁决哪一个来源正确。

除非被明确表示为外部派生工件或推断结果，否则 PBDL-Core 不得将以下内容伪装成来源直接描述的信息：

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

PBDL-Core 不得仅通过字段命名或默认语言构造暗示未经验证的因果关系、治疗效果或临床结论。

## 5. PBDL 核心模型

PBDL-Core 定义以下四类核心语义对象：

- `Subject`：`Behavior` 与 `Preference` 所描述的主体，也是文档内主体引用的稳定锚点。
- `Behavior`：对某个 `Subject` 已描述或已断言的行为、未发生行为或行为状态的表示。
- `Preference`：对某个 `Subject` 已表达或已推断的倾向、选择、优先级、厌恶或偏好的表示。
- `Relation`：在允许的端点类型之间显式表达语义联系的 Core 构造。

`Context` 用于限定 `Behavior` / `Preference` 的语义解释，但不作为具有独立身份、可被引用的一级 Core 实体。它以嵌入式限定信息的形式归属于 `Behavior` / `Preference`；具体字段、`coded` / `text` 值结构、局部 `provenance` 与相等性见 §8.5、§12 和 §17.4.5。`Provenance` 与 `Evidence` 的语义边界、字段、附着方式，以及 `SourceDescriptor` / `GeneratorDescriptor` / `Evidence` 的具体结构见 §13 与 §17.8。JSON Schema 与 DSL 语法仍留待后续定义。

### 5.1 文档与 Subject 绑定

一个 PBDL 文档必须至少包含一个 `Subject`。

一个 PBDL 文档可以包含多个 `Subject`。

每个 `Behavior` 必须绑定到且仅绑定到一个 `Subject`。

每个 `Preference` 必须绑定到且仅绑定到一个 `Subject`。

§17 定义了规范文档与对象的字段归属、`EntityId` 词法约束以及规范引用对象结构。DSL 表层语法仍未定义。即使未来表层语法在单 `Subject` 文档中允许省略显式主体引用，规范语义也必须能够确定该 `Behavior` 或 `Preference` 唯一对应的 `Subject`。

### 5.2 核心对象身份要求

核心对象的最小身份要求如下：

| Core 构造 | v1 Core 身份要求 | 理由 |
|---|---|---|
| `Subject` | 必须具有身份 | `Behavior` 与 `Preference` 需要稳定绑定到明确主体 |
| `Behavior` | 必须具有身份 | `Relation` 以及历史 `associated_behavior` 的兼容语义需要稳定引用 `Behavior` 实例 |
| `Preference` | 必须具有身份 | `Relation` 需要稳定引用 `Preference` 实例 |
| `Relation` | v1 Core 最小模型不要求身份 | 不允许 `Relation` 作为 `Relation` 端点，也没有已定义的 Core 构造需要引用 `Relation` 本身 |

`Relation` 不要求身份，并不禁止未来扩展为 `Relation` 提供标识符；这类能力不属于当前 Core 的最小要求。

### 5.3 标识符范围与稳定性

`Subject`、`Behavior` 与 `Preference` 的实体标识符必须在所属 PBDL 文档内唯一。三类实体共享同一个文档内身份命名空间；同一个标识符不得在同一文档中被另一个 `Subject`、`Behavior` 或 `Preference` 重复使用。

v1 Core 不得强制要求全局 UUID、URI 或其他跨系统全局标识符。

在同一 PBDL 文档的生命周期内，用于内部引用的标识符必须保持足够稳定，以保证已建立的内部引用不会因为对象重排而改变指向。

数组位置、列表序号或其他仅由容器位置推导出的值不得作为规范性的实体身份。

跨文档身份与跨文档引用协议不属于当前规范范围，保留为未来工作。

### 5.4 显示标签不是实体身份

显示标签、类型名称、类别名称或术语代码本身不得自动充当实体实例的身份。

例如，`medication_nonadherence` 如果表示一种 `Behavior` 类型，它描述的是“该 `Behavior` 属于什么类型”，而不是“这是哪个 `Behavior` 实例”。

同样，`behavior_type`、`preference_category` 与 `Relation` 类型概念都不是相应实体实例的身份。

### 5.5 引用模型

Core 引用必须在其声明的引用范围内解析到恰好一个实体。

在 v1 Core 最小模型中，内部引用的范围是当前 PBDL 文档。

无法解析到任何实体的引用是无效的。

能够解析到多个实体的歧义引用是无效的。

`Behavior` 与 `Preference` 对 `Subject` 的绑定必须使用能解析到明确 `Subject` 身份的引用语义，不得依赖模糊的显示标签。

`Relation` 的 `source` 与 `target` 端点必须使用实体引用，不得把未解析的自由文本标签作为规范性引用。

### 5.6 `Relation` 端点矩阵

PBDL-Core 的 `Relation` 允许以下最小端点集合：

| 来源端点 | 目标端点 | Core v1 |
|---|---|---|
| `Behavior` | `Behavior` | 允许 |
| `Behavior` | `Preference` | 允许 |
| `Preference` | `Behavior` | 允许 |
| `Preference` | `Preference` | 允许 |
| `Subject` | `Behavior` / `Preference` / `Subject` | 不允许作为 Core `Relation` 端点 |
| `Relation` | 任意 Core 实体 | 不允许 |
| 任意 Core 实体 | `Relation` | 不允许 |

`Subject` 是 `Behavior` / `Preference` 的稳定归属锚点，而不是通用关系图节点。若未来出现必须直接表达 `Subject` 层级关系的明确使用场景，可以由后续规范扩展。

PBDL-Core 不允许 `Relation→Relation`，以避免在没有明确使用场景时引入高阶关系、关系注释图或关系实体化语义。

§17 定义了 `EntityId` 的词法形式以及 `SubjectRef` / `CoreEntityRef` / `ActorRef` 的规范引用表示。DSL 语法与 JSON Schema 仍为 **TODO**。

### 5.7 时间语义基础

PBDL-Core 的最小时间语义用于回答：

- `Behavior` 在什么时候发生、持续或适用；
- `Preference` 在什么时候适用；
- `Relation` 在什么时候成立或适用。

PBDL-Core 区分两类不同的时间语义：

- **语义时间**：描述 `Behavior` / `Preference` / `Relation` 本身发生、成立或适用的时间；
- **来源追踪时间**：描述相关信息何时被报告、记录、抽取、观测或生成。

语义时间与来源追踪时间不得视为同一个时间概念。记录时间不得自动替代 `Behavior` / `Preference` / `Relation` 的语义时间。

例如，患者在 9 月 20 日报告“上周漏服了三次药”时：

- “上周”属于 `Behavior` 的语义时间；
- “9 月 20 日”属于 `provenance` 中的报告时间。

`Behavior`、`Preference` 与 `Relation` 应基于同一套 Core 时间抽象表达语义时间范围，但三者使用该抽象时承担不同的语义角色。

#### 5.7.1 Instant

`Instant` 表示一个时间点。

`Instant` 可以具有不同的来源精度，例如只精确到年、月、日，或更高精度的具体时刻。具体日期时间序列化形式见 §8.2 的 `TemporalValue` 词法定义。

#### 5.7.2 Interval

`Interval` 表示一个时间区间。

`Interval` 可以具有：

- 同时提供 `start` 与 `end`；
- 已知 `start`、未提供 `end`；
- 未提供 `start`、已知 `end`。

一个 `Interval` 必须至少具有一个有效边界。两个边界都不存在时，该结构不得被解释为有意义的时间范围。

单边界 `Interval` 中缺失的另一侧边界只表示该边界未提供。

缺失的边界不得自动解释为：

- 永久持续；
- 一直持续到现在；
- 一直持续到未来；
- 从无限过去开始；
- 数学意义上的无界区间。

如果未来需要显式表达“进行中”（ongoing）、“无界”（unbounded）或“已知开放端点”（known-open-ended）等时间语义，应由后续规范单独定义；当前规范不定义这些语义。

如果 `start` 与 `end` 同时存在且能够比较，则 `start` 不得晚于 `end`。

#### 5.7.3 未提供语义时间

`Behavior`、`Preference` 或 `Relation` 可以没有语义时间信息。

§5.7 不要求引入显式的未知 token；缺少时间信息即可表示“未提供语义时间”。

缺少语义时间信息不得被解释为：

- 永久成立；
- 从出生至今；
- 当前仍成立；
- 始终如此；
- 反复发生；
- 时间不重要。

它只表示当前规范语义没有提供该项时间信息。

#### 5.7.4 时间精度保留

对时间信息进行规范化或其他规范转换时，转换结果必须保留来源实际支持的时间精度，不得发明来源未提供的精度。

例如，来源只有“2026-09”时，规范化不得仅为了获得完整时间戳而将其伪造成“2026-09-01T00:00:00”。

同样，“2026 年”不得被自动伪造成某一个具体日期。

§8.2 定义部分日期和日期时间的规范词法形式，并通过词法形式保留年、月、日、分钟、秒和小数秒等不同精度。

#### 5.7.5 时区信息保留

如果来源未提供时区或偏移量，规范化不得凭空声明具体的时区或偏移量。

如果来源已经提供时区或偏移量，规范表示必须保留来源实际提供的信息。

当前规范不另行定义时区或偏移量的序列化形式；§8.2 定义可选的数值型偏移量与时区后缀，并继续禁止凭空补造来源未提供的时区或偏移量。

#### 5.7.6 相对时间

相对时间表达可以出现在来源中，例如：

- 昨天；
- 上周；
- 治疗后三天；
- 出院后一个月。

如果相对时间表达保留在规范语义表示中，它必须具有足以解释其含义的明确锚点。

或者，在形成 PBDL 的规范语义表示之前，上游转换已经将其解析为足够明确的绝对时间或锚定时间表达。

无法确定锚点的裸相对时间不得被假装成唯一确定的绝对时间范围。

当前规范不定义相对时间的 DSL 语法。

#### 5.7.7 频率/重复模式与时间范围是不同维度

`Behavior` 的频率和重复模式的最小语义边界见 §10.5。

语义时间范围回答“`Behavior` 在什么时候发生、持续或适用”；频率/重复模式回答“某类 `Behavior` 的发生以什么模式或频度重复”。

二者必须保持可区分，也可以同时存在。

例如，“2026 年 1 月至 3 月，每周漏服两次”中：

- “2026 年 1 月至 3 月”属于 §5.7 的语义时间范围；
- “每周漏服两次”属于 §10.5 的 `Behavior` 频率/重复模式信息。

“持续三个月”不得被解释为“每三个月一次”；“每天”也不得被当作一个 `Interval`。

当前规范不把重复模式语义扩展到 `Preference` 或 `Relation`，也不定义 RRULE、类 cron 语言、日历引擎或具体的时间/重复模式序列化。

### 5.8 `Annotation` 语义

`Annotation` 用于承载轻量的人类可读补充信息。

`Annotation` 用于为某个规范语义对象或断言提供人类可读的补充说明、澄清或解释性文本。它是辅助性的人类可读信息，而不是规范机器语义的唯一载体。

`Annotation` 可以用于保留：

- 对 `Behavior` 的额外说明；
- 对 `Preference` 的人类可读补充；
- 来源中无法完全结构化、但值得保留的说明；
- 人工或外部系统产生的解释性备注。

`Annotation` 的最小规范字段、附着位置与基数见 §17，`Text` 词法约束见 §8.1。作者/生成者表示、JSON Schema 与 DSL 语法仍留待后续定义。

#### 5.8.1 `Annotation` 不是机器语义的后门

如果某项信息对身份、引用、`Behavior` 类型、`Preference` 值、时间语义、频率、`Context`、`Relation` 类型、关系方向、`Provenance`、DIRECT / INFERRED 或因果/非因果区分等规范机器语义具有规范性意义，就不得只把它藏在自由文本 `Annotation` 中。

如果某项语义已经有结构化的规范表达机制，`Annotation` 可以补充解释，但不得替代该结构化机制。

符合规范的使用方不得被迫通过自然语言理解自由文本说明或 `Annotation`，才能确定对象的核心机器语义。

#### 5.8.2 `Annotation` 本身不创建语义断言

`Annotation` 文本自身不得自动创建新的 `Behavior`、`Preference`、`Relation`、`Context`、因果断言、风险结果、推荐结果或其他派生/应用结果。

例如，`Behavior` 已结构化为“患者漏服药物”，而 `Annotation` 写“可能因为工作压力较大”，该文本本身不得自动使规范语义获得来源归因的理由、因果 `Relation`、`Context` 或派生的临床结论。

若 `Annotation` 中的内容需要成为机器可消费的语义，就必须通过已有且适用的结构化语义机制表达，并遵守相应的 `provenance` / `derivation` 规则。

#### 5.8.3 `Annotation` 的派生与来源类别

`Annotation` 至少需要区分以下 `provenance` / `derivation` 情况，但当前规范不定义对应的表层枚举。

1. **来源描述或来源承载的文本**：来源本身已经包含该说明；忠实保留或轻度规范化时，`Annotation` 可以具有 `DIRECT` 来源语义。
2. **人工撰写的解释性 `Annotation`**：人工标注者或审阅者额外增加的解释；它必须与来源描述的内容保持来源可区分，不得冒充患者、临床人员或原始来源直接说过的话。
3. **模型或分析过程生成的解释性 `Annotation`**：模型、规则或分析过程在来源未表达的基础上生成新解释；该新增内容必须保持 `INFERRED` 派生语义，并不得标成 `DIRECT` 来源文本。

是否使用 LLM / NLP 本身不决定 DIRECT / INFERRED。

如果来源明确写“因为恶心，患者停止服药”，LLM 仅忠实改写为“患者将恶心描述为停药原因”，且没有新增来源不存在的解释，该 `Annotation` 可以继续属于 DIRECT、忠实于来源的表示。

如果 LLM 新增“可能因为患者对药物存在恐惧”，而来源未表达该解释，则新增部分属于 INFERRED。

#### 5.8.4 `Annotation` 不等同于 `Provenance` 或 `Evidence`

`Annotation` 不得替代 `Behavior`、`Preference` 或 `Relation` 断言所要求的 `Provenance`。

“来源是谁”“如何产生”“DIRECT / INFERRED”等信息不得只通过自由文本说明表达，再要求下游 NLP 猜测。

`Annotation` 与 `Evidence` 也不是同一概念：

- `Evidence` 回答“有什么材料支持或承载这项信息”；
- `Annotation` 回答“有什么人类可读的补充说明”。

将来源文本复制到 `Annotation` 中，不得自动使该 `Annotation` 成为规范性 `Evidence` 对象；`Evidence` 材料也不会自动成为 `Annotation`。

§5.8 不定义引用文本、来源片段位置、文档偏移量或证据摘录的结构。

#### 5.8.5 `Annotation` 不建立因果关系或`Relation`

`Annotation` 中出现 `because`、`due to`、因、导致、所以、可能因为等语言，不得仅凭自由文本内容自动建立规范因果语义。

来源归因的理由继续使用 §10.3 语义；模型生成的解释在适用时继续保持 `INFERRED` 派生语义。

同样，`Annotation` 文本不得自动创建规范的 `Relation`。

如果 Preference–Behavior 关联、`Relation` 类型、方向性或端点需要机器语义，就必须显式使用 §14 的 `Relation` 机制，而不是只隐藏在 `Annotation` 中。

#### 5.8.6 `Annotation` 不替代时间、频率或`Context` 语义

如果 `Annotation` 中的“最近”“上周”“经常”“每天”“工作时”等信息需要成为规范机器语义，它们必须分别遵守 §5.7 的时间语义、§10.5 的频率/重复模式语义与 `Context` 语义。

`Annotation` 不得成为这些结构化语义的唯一规范性表达。

#### 5.8.7 `Annotation` 不创建派生分析结果或校验器状态

`Annotation` 中的“严重不依从”“未来风险很高”等文本，不得自动使 PBDL-Core 获得风险标签、临床严重度、依从性评分、预测或推荐等语义。

这些信息仍应根据实际来源与结构化建模，归入来源描述的语义或 Core 外部的派生/应用层。

`Annotation` 不得用于重新引入旧版 `Behavior.validity_flag`，也不得替代校验错误、警告、Schema 违例或其他校验器/报告输出。

#### 5.8.8 `Annotation` 的身份与图结构边界

`Annotation` 不要求独立身份，不加入 `Subject` / `Behavior` / `Preference` 的文档内身份命名空间，也不是 `Relation` 端点。

§5.8 不新增 `Annotation→Annotation`、`Annotation→Relation`、`Relation→Annotation` 或其他 `Annotation` 图边。

`Annotation` 是附着于现有规范语义对象或断言的轻量辅助信息，而不是新的、具有身份的 Core 图实体。

#### 5.8.9 不包含隐藏思维链

PBDL-Core 不得要求模型暴露、存储或交换隐藏思维链（hidden chain-of-thought）、私有推理轨迹、逐 token 推理、内部草稿或其他隐藏模型推理过程，并将其作为规范性 `Annotation` 内容。

外部系统可以提供简洁解释、理由摘要或面向结果的 `Annotation`，但其 `source` / `generator` / `derivation` 必须能够与来源承载的文本保持可区分。

旧版 `reasoning_note` 中的 “reasoning” 不得被解释为 PBDL-Core 要求保存模型私有推理过程。

#### 5.8.10 缺少`Annotation` 与结构化语义优先级

`Behavior` / `Preference` 可以没有 `Annotation`。

缺少 `Annotation` 不得被解释为没有 `Context`、没有 `Provenance`、没有 `Evidence`、没有解释、断言已完全理解或断言不需要来源追踪。

它只表示没有提供额外的人类可读 `Annotation`。

如果 `Annotation` 与结构化规范语义冲突，符合规范的使用方不得仅根据 `Annotation` 静默覆盖结构化语义。

此类冲突需要由上游修正、校验/审阅或其他明确机制处理；§5.8 不定义冲突解析器。

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

除非由后续规范明确定义，否则任何 token、关键字、分隔符或字面量语法都不具有规范性。

## 7. 语法

当前语法仍有意保持不完整。

当前语法占位文件位于 [`grammar/pbdl.ebnf`](grammar/pbdl.ebnf)。

**TODO：** 定义 Patient / `Subject`、`Behavior`、`Preference`、`Context`、`Evidence` / `Provenance` 与 `Relation` 的具体语法。

## 8. 类型系统

§17 定义了规范对象模型的最小结构类型、必需/可选字段、基数、类型化引用归属与命名嵌套语义类型。

`VersionToken`、`EntityId`、`SubjectRef`、`CoreEntityRef`、`ActorRef`、`ExternalActorRef`、`DerivationKind`、`SourceDescriptor`、`GeneratorDescriptor`、`Evidence` 与引用表示的具体规范形式见本章与 §17。

`Text`、`TemporalValue`、`Coding` 与 `Confidence` 的规范定义分别见本章、§15 与 §17。

### 8.1 Text

`Text` 的规范表示是与 JSON 兼容的 Unicode 字符串。

`Text` 必须满足以下要求：

- 能解码为有效的 Unicode 标量值序列；
- 至少包含一个不属于 Unicode `White_Space` 属性的码点。

因此，空字符串与仅由空白字符组成的字符串不得作为符合规范的 `Text`。

规范化不得自动对 `Text` 执行以下操作：

- trim；
- case-fold；
- Unicode 规范化；
- 将其解释为 `Coding` 或术语 token。

`Text` 的规范相等性采用**精确的 Unicode 标量值序列相等**。

因此，即使两个码点序列在视觉上相似，只要其 Unicode 标量值序列不同，在没有额外明确规范化规则时也不得自动视为相等。

该规则使 `Evidence.content` 与 `Annotation.text` 无法用空值或仅空白字符的值伪造“存在内容”。

当前规范不定义 Markdown、HTML、rich-text 或自然语言本体语义。

### 8.2 TemporalValue

`TemporalValue` 的规范表示是受约束的字符串。其词法形式本身保留来源支持的时间精度，以及来源提供的时区或偏移量信息。

`TemporalValue` 必须精确符合以下一种形式。

#### 8.2.1 日期族形式

年精度：

    YYYY

其中 YYYY 为 0001..9999。

月精度：

    YYYY-MM

其中 MM 为 01..12。

日期精度：

    YYYY-MM-DD

其中日期必须是前推格里高利历（proleptic Gregorian calendar）中真实存在的日期。

日期族值不得携带时间、偏移量或时区后缀。

#### 8.2.2 日期时间形式

分钟精度：

    YYYY-MM-DDTHH:MM<zone?>

秒精度：

    YYYY-MM-DDTHH:MM:SS<zone?>

小数秒精度：

    YYYY-MM-DDTHH:MM:SS.F<zone?>

其中：

- HH = 00..23；
- MM = 00..59；
- SS = 00..59；
- leap-second 的词法值 60 不属于当前规范；
- F 为 1..9 位十进制数字，其位数本身属于需要保留的精度信息；
- 日历日期必须有效。

`<zone?>` 可以省略，或采用以下一种形式：

    Z
    +HH:MM
    -HH:MM
    [ZoneToken]
    Z[ZoneToken]
    +HH:MM[ZoneToken]
    -HH:MM[ZoneToken]

数值型偏移量范围为 -14:00..+14:00；绝对值为 14 小时时，分钟必须为 00。

`ZoneToken` 必须是非空、区分大小写的 token；字符仅限 ASCII 字母、数字、`.`、`_`、`+`、`-`、`/`，且不得包含空白字符、`[` 或 `]`。

方括号包围的 `ZoneToken` 只用于保留来源提供的时区标识符，例如 `[America/Los_Angeles]`；PBDL-Core 不得根据 `ZoneToken` 名称自行推导来源未提供的数值型偏移量。

来源未提供时区或偏移量时，规范化不得添加 `Z`、数值型偏移量或 `ZoneToken`。

来源提供数值型偏移量、时区标识符或二者时，规范表示必须保留来源实际提供的信息。

#### 8.2.3 无效形式

以下形式不属于规范的 `TemporalValue`：

- 只有时间的值；
- 携带时区或偏移量的仅日期值；
- 格里高利历中不存在的日期；
- 月、日或时钟组成部分格式错误的值；
- 尚未解析的相对时间表达；
- 为补齐精度而伪造的日期、时间或时区。

尚未解析的相对时间表达继续遵守 §5.7 与 §17：必须在规范化前可靠解析，或仅作为 `Evidence` / `Annotation` 保真保存，不得伪装成 `TemporalValue`。

#### 8.2.4 精度

时间精度完全由词法形式保留：

- `2026` 不等于把年份扩展成某个具体日期；
- `2026-09` 不等于 9 月 1 日；
- 分钟精度不等于秒精度；
- `.1`、`.10` 与 `.100` 保留不同的 fractional-second 精度。

规范化不得为了统一时间戳形状而添加来源未提供的组成部分。

#### 8.2.5 `TemporalValue` 规范信息相等

`TemporalValue` 的规范相等性采用**规范信息相等**，而不是物理时刻等价。

两个 `TemporalValue` 只有在完整词法字符串精确相同时才语义等价。

因此：

    2026-09-27T10:00Z

与：

    2026-09-27T18:00+08:00

即使两个值可能表示同一物理时刻，也不得视为规范信息相等，因为它们保留的局部词法值与偏移量信息不同。

同样：

- `Z` 与 `+00:00` 不属于规范信息相等；
- 缺少时区信息与存在时区信息不属于规范信息相等；
- `ZoneToken` 是否存在或其值不同，均不属于规范信息相等；
- 精度不同不属于规范信息相等。

实现可以提供独立的物理时刻比较操作，但该操作不得改写或替代规范信息相等，也不得为缺少偏移量或时区信息的值发明时区。

#### 8.2.6 `Interval` 校验的最小时间可比性

`Interval` 边界顺序采用保守的“明确晚于”判断。

日期族值可以在前推格里高利历上，按其精度对应的可能日期范围进行比较。

例如：

- `2026-10` 的最早可能日期晚于 `2026-09-15` 的最晚可能日期，因此作为 `start` / `end` 时可判定 `start` 明确晚于 `end`；
- `2026-09` 与 `2026-09-15` 的可能范围重叠，因此不能据此判定 `start` 明确晚于 `end`，也不得发明具体日期来强行比较。

对于日期时间值：

- 两者都有显式数值型偏移量时，可以基于偏移量将各自的精度范围映射到物理时刻范围后比较顺序；
- 两者都没有任何数值型偏移量或 `ZoneToken` 时，可以按本地民用日期时间的精度范围比较；
- 一方有数值型偏移量、另一方没有时，视为不可比较；
- 只有方括号 `ZoneToken` 而没有数值型偏移量时，不要求解析时区数据库或 DST，因此不据此拒绝其时间顺序；
- 日期族与日期时间族之间不强制比较顺序。

只有当 `start` 的**最早可能值**仍严格晚于 `end` 的**最晚可能值**时，才必须判定 `start` 明确晚于 `end`。

如果可能范围重叠，或当前信息不足以建立可比较顺序，校验器不得通过补造精度或时区信息来拒绝该 `Interval`。

本节只定义最小有效性边界，不要求实现完整的日期运算引擎。

### 8.3 BehaviorFrequency

`BehaviorFrequency` 是明确的带判别标记联合类型：

    BehaviorFrequency =
        ObservedCountFrequency
        | RateFrequency
        | RecurrenceFrequency
        | QualitativeFrequency

四种变体不得通过任意字符串合并为同一个频率字段。

所有变体都可以具有：

    provenance? : Provenance[1..*]

该局部 `provenance` 字段继续完全遵守 §17.10 的“继承当前完整集合、完全覆盖、禁止叠加合并、冗余时省略”规则。

#### 8.3.1 QuantitativeFrequencyPrecision

`ObservedCountFrequency`、`RateFrequency` 与 `RecurrenceFrequency` 使用必需的 `precision` token：

    "exact" | "approximate"

`"exact"` 表示规范的定量/重复模式陈述没有携带来源中的近似限定。

`"approximate"` 表示来源明确表达了约数、近似频率或近似的重复节奏。

`precision` token 不得替换 `Confidence`，使用方也不得把它解释为统计意义上的置信水平。

#### 8.3.2 FrequencyPeriod

`FrequencyPeriod` 的规范结构如下：

    FrequencyPeriod {
        value : positive integer
        unit  : "day" | "week" | "month" | "year"
    }

`value` 必须 >= 1。

§8.3–§8.4 不加入 `"hour"`：当前典型情况不需要小时级用药计划引擎；`day_part` 重复模式已覆盖当前规范的日内时段要求。需要小时级重复模式的来源，在当前规范中不得被偷偷改写成一天的分数。

§8.3–§8.4 不允许非整数的 `period.value`。若来源表达当前规范无法无损表示的非整数周期，规范化器不得舍入、重新缩放或发明等价持续时间；原始信息可以由 `Evidence` / `Annotation` 保真，并等待未来扩展。

`month` / `year` 表示日历周期概念，不得自动换算为固定天数。

`FrequencyPeriod` 相等要求 `value` 的数值精确相等，且 `unit` token 相同。

#### 8.3.3 ObservedCountFrequency

`ObservedCountFrequency` 的规范结构如下：

    ObservedCountFrequency {
        kind        : "observed_count"
        count       : non-negative integer
        precision   : "exact" | "approximate"
        window?     : Interval
        provenance? : Provenance[1..*]
    }

`count` 为必需字段，且必须 >= 0。

`count = 0` 合法，表示来源明确支持在所述观测语义下发生次数为零；不得解释为缺少频率信息。

`window` 可选。

允许只提供 `count`。例如，来源只说“漏服了 3 次”时，可以规范化为 `count = 3` 且省略 `window`，不得发明观测时间窗。

`window` 存在时使用 `Interval`；它表示观测或参考时间窗，不是 `rate` 的分母，也不得自动把 `count` 转成 `rate`。

#### 8.3.4 RateFrequency

`RateFrequency` 的规范结构如下：

    RateFrequency {
        kind        : "rate"
        value       : non-negative finite number
        period      : FrequencyPeriod
        precision   : "exact" | "approximate"
        provenance? : Provenance[1..*]
    }

`value`、`period`、`precision` 都是必需字段。

`value` 必须 >= 0 且为有限数值。

`RateFrequency` 表示“每个 `period` 平均发生 `value` 次”的频率值。

`period` 必须显式存在；只有裸 `value = 2` 时，不得解释为 `rate`。

观测到的 `count` 不得仅因为具有 `window` 就自动规范化成 `RateFrequency`。

#### 8.3.5 RecurrenceFrequency

`RecurrenceFrequency` 的规范结构如下：

    RecurrenceFrequency {
        kind              : "recurrence"
        period            : FrequencyPeriod
        precision         : "exact" | "approximate"
        times_per_period? : positive integer
        days_of_week?     : Weekday[1..*]
        day_part?         : DayPart
        provenance?       : Provenance[1..*]
    }

`period` 与 `precision` 都是必需字段。

`times_per_period` 若存在，必须 >= 1。

`times_per_period` 缺失只表示来源未提供每个 `period` 的发生次数，不得默认为 1。

`Weekday` 的规范 token：

    "mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun"

`days_of_week` 若存在：

- 集合必须非空；
- 不得出现重复的 `Weekday` token；
- 集合顺序不得具有语义含义；
- `period` 必须精确为 `{ value: 1, unit: "week" }`；
- `times_per_period` 必须缺失，以避免同时存在两个相互竞争的发生次数机制。

`days_of_week` 缺失表示未提供星期几的计划，不得解释为每个工作日。

`DayPart` 的规范 token：

    "morning" | "afternoon" | "evening" | "night"

`day_part` 可选；缺失表示未提供日内时段限定。

`DayPart` 表示来源描述的定性日内时段；§8.3–§8.4 不得为这些 token 暗中绑定统一的钟点阈值。

`day_part` 可以与每日重复模式或按 `days_of_week` 表达的每周重复模式共存；§8.3–§8.4 不引入具体钟点计划、RRULE 或 cron 语义。

`RecurrenceFrequency` 表达重复模式，不得自动生成具体的观测发生时间戳。

#### 8.3.6 QualitativeFrequency

`QualitativeFrequency` 的规范结构如下：

    QualitativeFrequency {
        kind        : "qualitative"
        value       : QualitativeFrequencyToken
        provenance? : Provenance[1..*]
    }

`QualitativeFrequencyToken` 使用以下规范小写 token：

    "never"
    "rarely"
    "occasionally"
    "sometimes"
    "often"
    "frequently"
    "usually"
    "intermittently"
    "always"

这些 token 表示来源描述的定性频率概念。

Core 不得为任一 token 绑定数值阈值、概率、`rate`、百分比或重复间隔。

token 列表顺序不得被解释为规范性的数值刻度或临床严重度顺序。

`"never"` / `"always"` 仍受所属对象的时间范围 / `Context` 范围限定；缺少范围不得自动升级为终身范围。

#### 8.3.7 `BehaviorFrequency` 内容相等

`BehaviorFrequency` 的**语义内容相等**明确忽略 `BehaviorFrequency.provenance`。

不同 `kind` 的变体不得语义等价。

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

完整 `BehaviorFrequency` 相等必须同时满足：

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

§8.3–§8.4 不新增序数/强度、引用值或列表/多选变体。

#### 8.4.1 CodedPreferenceValue

    CodedPreferenceValue {
        kind  : "coded"
        value : Coding
    }

`value` 必需。

当适用的术语或 `category` 契约提供可靠且不丢失来源语义的 `Coding` 时，规范化器应使用 `coded` 变体，而不是仅为方便退化为自由文本。

如果没有可靠的绑定规则，规范化器不得发明 `Coding`。

#### 8.4.2 TextPreferenceValue

    TextPreferenceValue {
        kind  : "text"
        value : Text
    }

`value` 为必需字段，并遵守 §8.1 的 `Text` 契约。

`Text` 变体用于来源保真：当来源中的偏好值无法可靠映射到 `Coding`、`boolean` 或 `number` 语义时，可以使用 `Text`。

`Text` 变体不得成为绕过结构化语义的后门。

如果规范性的 `category`/`value` 绑定规则明确要求某个可靠的 `coded` 值，规范化器不得仅为了避免术语映射而使用 `Text`。

使用方不得被迫通过 NLP 才能恢复本来可以可靠结构化的 `PreferenceValue`。

#### 8.4.3 BooleanPreferenceValue

    BooleanPreferenceValue {
        kind  : "boolean"
        value : boolean
    }

`value` 为必需字段。

`boolean` 变体只应在 `Preference.category` 的语义确实把 `value` 定义为二元选择或二元状态时使用。

例如，当 `category` 表示是否接受电话联系时，`value = false` 可以表示“不希望电话联系”。

`boolean` 值 `false` 是一个真实的 `PreferenceValue`，不得解释为缺少 `Preference`；缺少 `Preference` 断言也不得解释为 `false`。

规范化器不得仅因为旧版字符串看起来像 `"yes"` / `"no"`，就在缺少 `category` 或来源语义支持时猜测 `boolean`。

#### 8.4.4 NumericPreferenceValue

    NumericPreferenceValue {
        kind     : "number"
        operator : "eq" | "lt" | "lte" | "gt" | "gte"
        value    : finite number
        unit?    : Coding
    }

`operator` 与 `value` 都是必需字段。

`value` 必须是有限数值；NaN 与 ±Infinity 无效。

`operator` 保留数值型 preference 的比较语义。

因此，“等待时间不超过 30 分钟”需要 `operator = "lte"`，不能只保存裸数值 30。

`unit` 可选；但若来源或 `category` 语义表示有量纲数值，且来源提供了 `unit`，规范表示必须保留该 `unit`。

`unit` 使用已有的 `Coding`；§8.3–§8.4 不得新增任意 unit 字符串类型。

无量纲数值仅在以下情况合法：

- 来源明确表达无量纲数值；或
- 适用的 `Preference.category` 语义契约明确定义该 `value` 为无量纲。

当数值语义需要 `unit`、但来源没有提供时，规范化器不得猜测分钟、天、百分比或其他单位。

#### 8.4.5 偏好强度与序数边界

§8.3–§8.4 不新增偏好强度或序数变体。

例如“强烈偏好居家管理”中：

- “居家管理”如果有可靠的 `Coding`，可以进入 `CodedPreferenceValue`；
- “强烈”不得在当前规范中被发明成序数值、`Confidence` 或派生的偏好强度评分。

需要保留的原始强度措辞可由 `Evidence` / `Annotation` 保真；未来若确有需要，应由专门的 preference-strength 规范另行定义。

#### 8.4.6 引用与列表边界

`PreferenceValue` 不包含 `CoreEntityRef` 变体。

旧版或来源中 `Preference` 与 `Behavior` 的关联继续使用 §14 的 `Relation`，不得通过引用值形式的 `PreferenceValue` 绕回第二套链接机制。

`PreferenceValue` 也不包含通用列表或多选变体。

如果来源表达多个可独立成立的 `Preference` 断言，规范化器可以使用多个 `Preference` 实例；如果多值集合本身具有不可拆分语义，而当前联合类型无法无损表示，则不得发明列表语义，可保留来源材料并等待未来扩展。

#### 8.4.7 `PreferenceValue` 相等性

`PreferenceValue` 的相等性由 `kind` 判别字段决定。

不同 `kind` 不得语义等价。

`CodedPreferenceValue`：

- 使用 §15 的 `Coding` 规范信息相等。

`TextPreferenceValue`：

- 使用 §8.1 的 `Text` 相等性。

`BooleanPreferenceValue`：

- 使用精确布尔值相等。

`NumericPreferenceValue`：

- `operator` token 必须相同；
- `value` 使用有限数学数值的精确相等；
- `unit` 同时缺失，或按 §15 的 `Coding` 规范信息相等判定为语义等价。

当前规范不定义 `PreferenceValue` 的模糊相似度。

#### 8.4.8 旧版 `PreferenceValue` 迁移

旧版 `Preference.preference_value` 迁移必须保留来源支持的类型语义。

- 来源或绑定规则可靠支持 `Coding` → 可以使用 `coded`；
- 来源或 `category` 可靠支持 `boolean` → 可以使用 `boolean`；
- 来源可靠支持数值比较运算符 / `value` / `unit` 语义 → 可以使用 `number`；
- 来源只保留原始字符串，且无法可靠类型化 → 使用 text。

规范化器不得：

- 根据字符串外观猜测 `boolean`；
- 发明术语代码；
- 猜测 unit；
- 猜测数值比较运算符或数值刻度；
- 把缺乏可靠类型信息的旧版文本当作已经类型化的值。

### 8.5 Context

`Context` 是轻量嵌入式限定信息：

    Context {
        value       : ContextValue
        provenance? : Provenance[1..*]
    }

`value` 为必需字段。

`provenance` 可选，并继续遵守 §17.10 的“继承当前完整集合、完全覆盖、禁止叠加合并、冗余时省略”规则。

`Context` **不**具有独立身份，不进入文档根集合，也不是 `Relation` 端点。

#### 8.5.1 ContextValue

`ContextValue` 使用与 `PreferenceValue` **不同的**最小带标签联合类型：

    ContextValue =
        CodedContextValue
        | TextContextValue

§8.5–§8.6 不复用 `PreferenceValue`，因为 `Context` 不具有偏好比较符、偏好选择或偏好专属的 `value` 语义。

##### CodedContextValue

    CodedContextValue {
        kind  : "coded"
        value : Coding
    }

当适用的术语或 context 绑定规则能够可靠表达情境概念时，规范化器应使用 `coded` 变体。

例如，在有可靠 `Coding` 的前提下，可以表达旅行、工作环境、存在家庭支持、居家环境、通过特定渠道沟通或类似工作日的社会情境。

当前规范不定义这些具体术语代码或词汇。

##### TextContextValue

    TextContextValue {
        kind  : "text"
        value : Text
    }

`Text` 变体是保真回退。

当来源明确包含情境信息，但无法可靠映射到术语时，规范化器可以使用 `TextContextValue`。

如果适用的规范性绑定规则已经提供可靠 `Coding`，规范化器应使用 `coded` 变体，而不得仅为实现方便把所有 `Context` 降级为 `Text`。

规范化器不得为了避免 `Text` 回退而发明术语代码。

`TextContextValue` 不得成为任意元数据容器，也不得要求下游通过 NLP 才能恢复本可可靠结构化的全部 `Context` 信息。

§8.5–§8.6 不加入 `boolean` / `number` `ContextValue` 变体，因为 C1–C10 典型情况不需要它们；“存在家庭支持”等来源概念可以表示为 `coded` 情境值，无法可靠编码时使用 `Text` 保真回退。

#### 8.5.2 `Context` 语义边界

`Context` 表达共现、情境或背景限定，而不表达来源归因的理由、已验证的原因、`Provenance`、语义时间范围或工作流状态。

例如：

- “旅行期间漏服”在只具有共现情境语义时 → `Context(traveling)`；
- “因为旅行漏服”若来源明确表达理由 → `BehaviorFactor`，而不只是 `Context`；
- “恶心时停药”若只支持情境性共现 → `Context`；
- “因为恶心停药” → 来源归因的 `BehaviorFactor`。

“工作日”只有在来源把它作为社会或生活情境概念时才可以表示为 `Context`；如果其唯一语义是日历重复规则或日期筛选条件，则应使用适用的时间/频率语义，不得为了方便重复编码成 `Context`。

`Context` 不得创建 `Behavior↔Behavior`、`Behavior↔Preference` 或 `Preference↔Preference` 的显式实体链接；这些关系继续使用 `Relation`。

#### 8.5.3 `Context` 相等性

`Context` 的语义内容相等**不包含 `provenance`**。

两个 `Context` 的内容语义等价，当且仅当：

- `ContextValue.kind` 相同；
- `coded` 变体的值使用 §15 的 `Coding` 规范信息相等；或
- `text` 变体的值使用 §8.1 的 `Text` 相等性。

不同 `ContextValue.kind` 不得语义等价。

`Context` 的完整限定信息相等要求：

1. `Context` 内容相等；
2. 有效来源集合按 §17.10 的 `Provenance` 语义相等规则判定为语义等价。

`Behavior.contexts` / `Preference.contexts` 的集合顺序不得表示优先级、因果关系或其他语义顺序。

两个 `Context` 项如果完整限定信息相等，则在规范集合中属于冗余重复项；规范化必须至多保留一个。内容相同但有效来源信息不同的 `Context` 不属于完整信息相等的重复项。

当前规范不定义 `Context` 的模糊相似度。

### 8.6 BehaviorFactor

`BehaviorFactor` 定义如下：

    BehaviorFactor {
        role        : FactorRole
        factor      : FactorValue
        direction   : FactorDirection
        provenance? : Provenance[1..*]
    }

`role`、`factor`、`direction` 都是必需字段。

`provenance` 可选，并完全复用 §17.10 的嵌套 `provenance` 规则。

`BehaviorFactor` 是 `Behavior` 局部的非 Core `factor` 限定信息，不具有独立身份，也不是 `Relation` 端点。

#### 8.6.1 FactorRole

`FactorRole` 的规范 token：

    "reported_reason"
    "observed_association"
    "antecedent"
    "explanatory"

语义：

- `"reported_reason"`：来源明确将该因素描述为该 `Behavior` 的理由或原因归因；这是来源归因语义，不是已经验证的因果事实。
- `"observed_association"`：来源只支持该因素与 `Behavior` 的记录性/观测性关联或共现，不声称其为理由。
- `"antecedent"`：来源支持该因素在 `Behavior` 之前出现；时间上的先后不等于因果关系。
- `"explanatory"`：外部人工、模型、规则或分析过程给出的解释性因素。若该解释超出来源直接表达的内容，其有效 `provenance` 必须保持 `"inferred"` 派生语义。

`FactorRole` 不得使用 `"inferred"` 作为 `role`；DIRECT / INFERRED / UNDETERMINED 属于 `Provenance.derivation`。

§8.5–§8.6 不新增 `causes`、`causal_factor`、`verified_cause` 等因果角色。

#### 8.6.2 FactorDirection

`FactorDirection` 的规范 token：

    "factor_to_behavior"
    "behavior_to_factor"
    "unspecified"

`direction` 为必需字段，用来显式区分“来源支持某个方向”和“来源没有足够方向信息”。

`"factor_to_behavior"` 只表示来源支持的语义方向从 `factor` 所表示的因素指向所属 `Behavior`，不得自动表示该因素导致了 `Behavior`。

`"behavior_to_factor"` 同理只表示相反方向，不得自动表示 `Behavior` 导致了该因素。

`"unspecified"` 表示来源没有足够信息确定方向；规范化器不得通过旧版字段名、token 顺序、时间邻近性或 NLP 猜测补造方向。

对于 `"antecedent"` `role`，`direction` 必须为 `"factor_to_behavior"`，因为该 `role` 定义的是因素在所属 `Behavior` 之前出现。

对于 `"reported_reason"` `role`，`direction` 必须为 `"factor_to_behavior"`，因为来源归因表达的是因素被报告为所属 `Behavior` 的理由。

`"observed_association"` 与 `"explanatory"` 可以根据来源或推断支持使用任一 `direction` token，包括 `"unspecified"`。

方向与因果关系始终是不同维度。

#### 8.6.3 FactorValue

`FactorValue` 使用带标签联合类型：

    FactorValue =
        CodedFactorValue
        | TextFactorValue

##### CodedFactorValue

    CodedFactorValue {
        kind  : "coded"
        value : Coding
    }

当该因素可以可靠映射到术语，例如 dizziness / nausea 等来源概念时，规范化器应使用 `coded` 变体。

##### TextFactorValue

    TextFactorValue {
        kind  : "text"
        value : Text
    }

当该因素只有来源措辞、无法可靠映射到术语时，`TextFactorValue` 用于保真保存。

规范化器不得为该因素发明 `Coding`。

因素文本不得只被塞进 `Annotation`，再要求下游 NLP 恢复 `BehaviorFactor` 的机器语义。

§8.5–§8.6 不新增 Symptom Core 实体。

#### 8.6.4 `BehaviorFactor` 因果语义边界

`BehaviorFactor` 本身不得创建因果 `Relation`，也不得创建 `Relation.weight`。

以下情况都不等价于已经验证的因果关系：

- reported_reason；
- antecedent；
- observed_association；
- 方向；
- `inferred` / 解释性因素。

如果未来需要规范性的因果 `Relation` 词汇，必须由专门的 `Relation` 词汇规范定义；当前规范不做该设计。

#### 8.6.5 `BehaviorFactor` 与 `Relation` 的边界

`BehaviorFactor` 只用于 `Behavior` 局部的非 Core 因素。

如果该因素实际是已有的文档内 `Behavior` 或 `Preference` 实体，并且语义是显式的类型化实体关系，规范表示必须使用 `Relation`，而不能把该实体的 `display` / 标签降级成 `BehaviorFactor`。

`BehaviorFactor` 不得成为绕过 §14 的 `Relation` 端点或 `type` 契约的第二套实体链接机制。

#### 8.6.6 `BehaviorFactor` 相等性

`BehaviorFactor` 的语义内容相等**不包含 `provenance`**。

两个 `BehaviorFactor` 的内容语义等价，当且仅当：

- `role` token 相同；
- `direction` token 相同；
- `factor.kind` 相同；
- `coded` 变体的因素值使用 §15 的 `Coding` 规范信息相等；或
- `text` 变体的因素值使用 §8.1 的 `Text` 相等性。

因此，nausea + `reported_reason` 与 nausea + `observed_association` 不得语义等价。

`BehaviorFactor` 的完整限定信息相等要求：

1. `BehaviorFactor` 内容相等；
2. 有效来源集合按 §17.10 的 `Provenance` 语义相等规则判定为语义等价。

`Behavior.factors` 的集合顺序不得表示优先级、因果关系、时间顺序或其他语义顺序。

两个 `BehaviorFactor` 项如果完整限定信息相等，则在规范集合中属于冗余重复项；规范化必须至多保留一个。

当前规范不定义 `BehaviorFactor` 的模糊相似度。

仍为 **TODO** 的主要是：

- 类型兼容与转换规则；
- 未来的字节级确定性序列化规范；
- JSON Schema 与 DSL 语法。

## 9. Patient / Subject

`Subject` 表示 `Behavior` 与 `Preference` 所描述的主体，并作为文档内主体引用的稳定锚点。

`Subject` 不得被设计成完整电子病历中 Patient 资源的替代物。PBDL-Core 不负责保存完整的：

- 姓名
- 地址
- 电话
- 完整人口学资料
- 完整医疗档案

这些信息若存在于外部系统，可以由外部系统管理；PBDL 中 `Subject` 的最小职责，是为行为与偏好提供明确、稳定且可引用的主体身份。

每个 PBDL 文档必须至少包含一个 `Subject`，也可以包含多个 `Subject`。

每个 `Subject` 必须具有文档内身份。

每个 `Behavior` 与 `Preference` 必须能够解析到恰好一个 `Subject`。

§17 规定规范 `Subject` 仅包含必需的 `id` 字段；`EntityId` 词法约束见 §17.3。`Subject` 隐私表示、外部标识符绑定方式与 DSL 表层语法仍为 **TODO**。

## 10. Behavior

`Behavior` 表示对某个 `Subject` 已描述或已断言的行为、未发生行为或行为状态。

它用于回答类似以下问题：

> 这个主体做了什么、没有做什么，或表现出了什么行为状态？

`Behavior` 必须绑定到恰好一个 `Subject`，并且必须具有稳定的文档内身份。

`Behavior` 本身不等价于：

- 诊断；
- 风险结果；
- recommendation；
- 因果解释；
- `Preference`；
- 治疗路径步骤。

`Behavior` 的身份表示一个具体实例，而不是其类型或显示标签。因此，`Behavior` 的 `type` 不得自动充当 `Behavior` 身份。

### 10.1 旧版 `executor` 兼容性

历史 `Behavior.executor` 的语义能力继续保留。

`Subject` 与 `Behavior` 的执行者/参与者不是同一个概念：

- `Subject` 表示“这条 `Behavior` / `Preference` 描述围绕谁”；
- executor / actor 表示“谁执行了该行为或参与了该动作”。

最常见的情况下，两者可以是同一人；但历史设计也可能需要表达照护者等其他参与者。

当前规范不引入完整 Participant 模型，也不在此处定义 `executor` 的最终字段类型。后续规范不得仅因为 `Behavior` 已绑定 `Subject` 就无条件删除历史 `executor` 语义。

每个符合规范的 `Behavior` 实例必须实际具有至少一条 `provenance` 关联链路，使其来源能够被追踪。仅仅“语言理论上支持来源追踪”不足以满足该要求。

### 10.2 `Behavior` 时间语义

`Behavior` 可以具有语义时间范围，用于描述其语义内容发生、持续或适用的时间范围。

历史 `Behavior.temporal_scope` 的时间表达能力继续保留，其规范方向是映射到共享 Core 时间抽象，而不是沿用旧字符串表示。

`Behavior` 缺少语义时间时，不得解释为永久行为、当前行为或反复行为；它只表示该 `Behavior` 的语义时间未指定。

### 10.3 诱因/症状关联语义

§10.3 保留历史 `Behavior.behavior_trigger` 与 `Behavior.symptom_triggered` 所表达的“原因 / 诱因 / 症状关联”能力，但不继承旧版字段名中 `trigger` / `triggered` 的默认因果含义。

旧版 `trigger` / `triggered` 命名不得单独建立以下任一语义：

- A 导致 B；
- A 在临床意义上导致 B；
- A 是经过验证的 B 的因果因素。

字段名称本身不得被视为因果证据。

§10.3 至少区分以下三类非等价语义情况。

#### 10.3.1 来源明确归因的理由

当来源明确把某因素描述为 `Behavior` 的原因、理由或诱因时，规范语义可以保留“该来源把 X 归因为或描述为 Y 的原因/理由”这一来源归因语义。

例如患者明确说“因为头晕，我停药了”，可以表示“患者报告头晕是其停药理由”。

来源归因的理由不得被规范语义自动等价为已经验证的因果 `Relation`。

如果来源本身明确表达该原因，而 LLM / NLP 只进行忠实抽取、解析、规范化或术语映射，没有新增来源未表达的解释，该结构化结果仍可以具有 `DIRECT` 来源语义。

来源归因所对应的来源身份必须能够通过 §13 的 `Provenance` 保持可追踪。

#### 10.3.2 观测或记录的关联与前置关系

如果来源只记录某因素与 `Behavior` 共现、在其之前出现、在相近 `Context` 中出现，或存在记录上的关联，但来源没有明确声称“这是 `Behavior` 的原因”，规范语义不得自动把该信息升级为来源归因的理由。

观测或记录到的关联或前置关系，不得自动成为因果断言。

特别地，时间上的先后只说明顺序。“A 先于 B”不得自动推出“A 导致 B”。

#### 10.3.3 推断解释

如果来源本身没有明确表达原因，但 LLM、ML 模型、规则引擎、分析过程或其他推导过程根据输入生成“X 可能解释/导致 Y”之类的解释，该信息属于 INFERRED 解释性信息。

INFERRED 解释不得静默表示为 DIRECT 来源归因的理由，也不得伪装成已经验证的因果关系。

DIRECT / INFERRED 的判断继续遵守 §13：依据语义内容是否相对于来源内容经过推导，而不是处理链路中是否出现 LLM、NLP、模型或工具。

#### 10.3.4 旧版 `behavior_trigger` 兼容性

历史 `Behavior.behavior_trigger` 的表达能力继续保留。

规范转换不得仅因为旧版字段名为 `behavior_trigger` 就赋予因果语义。

只有来源语义足够明确时，旧版值才可以解释为更具体的来源归因理由、观测到的前置关系、情境关联或推断解释等语义类别。

如果旧版值的真实含义不清楚，规范转换不得擅自升级为报告的/来源归因的理由或因果解释。

当前规范不定义这些未来类别的表层名称、具体字段或 enum。

#### 10.3.5 旧版 `symptom_triggered` 兼容性与方向

历史 `Behavior.symptom_triggered` 的表达能力继续保留，但该旧版字段名本身存在方向歧义，例如：

- 症状 → 行为；
- 行为 → 症状；
- 症状与行为仅有关联，而来源没有明确方向。

`symptom_triggered` 字段名不得单独决定语义方向。

如果规范语义需要表达症状相关方向，该方向必须有来源内容支持。

如果来源不支持方向，规范化不得发明方向。

方向与因果关系是两个不同维度：

- 症状先于行为，不得自动推出症状导致行为；
- 症状晚于行为，不得自动推出行为导致症状。

§10.3 不新增 Symptom 一级 PBDL-Core 实体，也不修改 `Relation` 端点矩阵。症状相关信息的最终结构归属尚未定义；未来可以由 `Behavior` 局部结构化信息、`Context`、外部 coded 概念、扩展或其他结构承担。

当前规范不定义新的规范性 `Relation` 词汇。`related_to`、`associated_with`、`reported_reason_for`、`precedes`、`follows` 等仍是非规范性候选，除非后续规范另行定义。

§17 将 `Behavior` 局部、非 Core 实体的诱因、症状或理由关联归入 `Behavior.factors`；若两端均为允许的 Core 实体，且表达显式类型化实体关系，则仍使用 `Relation`。

`BehaviorFactor` 的具体表示见 §8.6：

- `role` = `reported_reason` / `observed_association` / `antecedent` / `explanatory`；
- `factor` = coded / text `FactorValue`；
- `direction` = `factor_to_behavior` / `behavior_to_factor` / `unspecified`；
- `provenance?` 继续复用 §17.10。

旧版 `behavior_trigger` / `symptom_triggered` 的规范化必须依据真实来源语义选择 `Context`、`BehaviorFactor` 或 `Relation`，不得仅根据旧版字段名猜测理由、方向或因果关系。

规范性 `Relation` 词汇、具体 symptom 术语规范、JSON Schema 与 DSL 语法尚未定义。

### 10.4 旧版 `communication_status` 兼容性

历史 `Behavior.communication_status` 的表达能力继续保留，但单一旧版字段混合了多种不同语义。规范转换不得仅凭 `communication_status` 字段名决定其规范语义类别，也不得默认把这些语义继续压成一个通用 `Behavior` 状态。

旧版 `communication_status` 的语义至少分为以下四类情况。

#### 10.4.1 实际沟通 `Behavior`

如果来源描述 `Subject` / actor 实际实施或没有实施某个沟通行为，例如：

- 患者告诉医生自己漏服了药；
- 患者给护士打电话报告副作用；
- 患者没有告诉医生自己已经停药；

这首先属于观测或报告的沟通行为，而不是单纯的工作流状态。

只要该信息满足 `Behavior` 的既有语义边界，就可以作为 `Behavior` 语义内容表达。

“患者告诉医生 X”与“X 被医生记录进 EHR”不是同一个概念；前者描述沟通行为，后者若表达信息来源、记录过程或进入系统的路径，则属于 `Provenance` 语义。

当前规范不定义沟通行为的具体行为类型、参与者、接收者或渠道字段。既有 `Behavior.executor` 继续遵守本节兼容边界；当前规范不新增 Participant 一级 Core 实体。

#### 10.4.2 沟通情境信息

如果旧版 `communication_status` 的真实语义是在限定另一个 `Behavior` / `Preference` 所处的沟通情境，例如“该漏服行为已经向临床人员披露”或“该偏好尚未向家属沟通”，这类信息可以保留为候选的情境/沟通限定信息。

这类语义必须与实际沟通 `Behavior`、`Provenance` 信息以及工作流/应用状态保持可区分。

符合规范的 `Behavior` 不保留 `communication_status` 字段，并继续按实际沟通 `Behavior`、`Context`、`Provenance`、工作流或应用状态四类语义分流。

§8.5 规定 `Context` 可以使用 coded / text `ContextValue` 表达沟通情境概念，例如 `communication-via-WeChat`；这不得解释为工作流状态，也不重新引入 `communication_status : string`。

具体的沟通词汇与 Communication 扩展尚未定义。

#### 10.4.3 沟通相关 `Provenance`

如果旧版 `communication_status` 实际想表达：

- 谁报告或记录了这条信息；
- 信息从哪个来源或渠道进入系统；
- 谁抽取、生成或记录了该信息；
- 信息何时被记录、抽取或生成；

这些语义属于 §13 的 `Provenance`，而不是通用 `Context`。

规范转换不得为了保留旧版 `communication_status` 而复制、覆盖或混淆已经属于 `Provenance` 的语义。

#### 10.4.4 工作流与应用状态

如果旧版 `communication_status` 实际表示 `pending review`、`reviewed`、`acknowledged`、`escalated`、`assigned`、`notified`、`message sent`、`task completed`、`closed` 等软件或业务流程状态，这些信息默认属于工作流/应用层。

PBDL-Core 不得默认把此类工作流或应用状态当作患者自身 `Behavior` 的内在语义状态。

历史能力可以由未来扩展、应用元数据或外部工作流系统继续承载；当前规范不定义该扩展。

#### 10.4.5 沟通不等于事实认证

信息已经“沟通”，不得自动等价为信息已经“验证”。

同样，`acknowledged` 不得自动等价为 `agreed`、`verified` 或 `true`。

例如，患者已经告诉医生“我每天都按时服药”，只说明发生过报告或沟通，不表示该内容已经被认证为现实真值。该边界继续遵守 §13 的原则：PBDL 记录有来源的信息，而不是认证后的绝对真值。

如果来源同时包含沟通行为、其他 `Behavior` 和来源归因的理由，规范转换不得仅压缩成一个 `communication_status` 而丢失其余可区分语义；旧版迁移必须以实际来源含义为准。

### 10.5 `Behavior` 频率与重复模式语义

`Behavior` 语义内容可以描述：

- 一个具体发生记录；
- 一个 behavior 状态；
- 来源明确描述的汇总或重复行为模式。

规范语义必须保留来源描述的是具体发生记录、已观察发生记录的汇总，还是重复/定性模式。

规范化不得仅因为来源描述了模式，就自动展开出来源没有提供的具体观测发生时间戳；也不得仅因为存在若干独立发生记录，就自动把它们压缩为重复模式。

#### 10.5.1 参考时间窗内的观测或报告计数

来源可以描述一个参考时间窗中实际观察或报告的发生次数，例如“过去 7 天漏服 3 次”。

这表示在该参考时间窗中存在 count 信息。

观测或报告的计数在参考时间窗内，不得仅通过规范化自动变成重复规则或稳定的频率模式。

例如：

- “过去 7 天漏服 3 次”不得自动等价为“每周固定漏服 3 次”；
- “漏服 3 次”在没有参考周期时，不得被转换为 `3/week`、`3/month` 或其他频率值。

计数、频率值与重复模式是不同语义。当前规范不定义额外的 rate 字段。

#### 10.5.2 重复或周期模式

如果来源明确描述某项 `Behavior` 具有重复模式，例如“每天吸烟”“每周运动三次”“每天早晨测血压”，规范语义可以保留该周期性或重复模式。

重复模式不得被强制展开成未来或过去的具体观测发生时间戳。

“每天”描述的是模式，不表示来源已经观察或确认每一天都存在一个具体 occurrence。

如果多个独立发生记录被外部模型或分析过程总结为重复模式，而来源本身没有表达该模式，则该模式属于 `INFERRED` 来源语义。

#### 10.5.3 定性频率

来源可以使用 `often`、`sometimes`、`rarely`、`frequently`、`occasionally`、`intermittently` 等定性频率或模式信息。

规范化不得仅为了数值化或处理方便，把定性频率擅自映射到来源未提供的具体阈值、概率、rate 或重复间隔。

例如：

- `often` 不得无来源依据地变成 `>= 5 times/week`、`70%` 或 `daily`；
- `intermittent` 不得自动变成 `every N hours` 或固定的 `N times/week`。

#### 10.5.4 精确、近似与定性表达

规范化必须在语义层面保留频率信息究竟是精确、近似还是定性。

例如：

- “每周大约 3 次”不得被转换为“每周恰好 3 次”；
- “几乎每天”不得被转换为“严格每天一次”；
- “偶尔”不得被转换为来源未提供的固定 rate。

当前规范不定义额外的近似字段。

#### 10.5.5 预期或处方计划不等于实际`Behavior` 频率

预期或处方计划与实际患者 `Behavior` 的频率必须保持可区分。

例如，“医生要求每天服药两次”描述的是预期或处方用药计划，不表示患者实际每天服药两次。

规范语义不得仅根据预期或处方计划自动生成实际 `Behavior` 的频率。

反过来，实际 `Behavior` 的频率也不得自动解释成处方计划。

即使同时知道处方计划与实际 `Behavior` 频率，PBDL-Core 也不得因此自动生成依从性百分比、依从性差、不依从或其他派生依从性判断。

§10.5 不定义 Prescription、Regimen 或依从性分析模型。

#### 10.5.6 分母与频率值边界

当来源只提供发生次数而没有参考周期时，规范化不得发明频率值。

当来源缺少预期机会次数、应服剂量或其他分母时，规范化不得发明依从性比率、依从性百分比、不依从率或其他比例。

例如，“过去 7 天漏服 3 次”只直接支持漏服计数与参考时间窗；它本身不提供该期间应服药的总次数。

#### 10.5.7 发生记录不会自动建立重复模式

若来源只提供多个具体发生记录，规范转换不得自动宣称存在 recurring 模式。

例如，Monday、Tuesday、Wednesday 各记录一次 exercise，不自动等价为“患者每天运动”。

如果来源明确总结为“每天”，可以保留来源描述的模式；如果模式是模型、规则或分析过程根据发生记录推断所得，则该模式必须保留 `INFERRED` 来源语义，并不得静默表示为 `DIRECT` 来源描述的频率。

如果 LLM / NLP 只忠实抽取来源已经明确表达的频率/重复模式，例如“我基本每天都会测血压”，结果仍可以属于 `DIRECT` 来源语义。

#### 10.5.8 未提供频率信息及其范围

`Behavior` 可以没有频率/重复模式信息。

缺少频率/重复模式信息不得被解释为：

- 发生一次；
- 只发生一次；
- 不重复；
- 不规律；
- 连续发生；
- 每天发生；
- 未知但频繁。

它只表示规范语义没有提供 repetition / 频率信息。

频率/重复模式不得成为所有 `Behavior` 的强制属性。

`never`、`always` 等具有强范围含义的频率表达，不得在缺少来源支持的时间或情境范围时自动解释为终身范围、从出生至今或未来永久成立。

#### 10.5.9 持续时间、`Context`、理由与`Provenance` 的边界

持续时间或时间范围必须与频率保持可区分。

“持续 3 小时”描述持续时间或时间范围；“每 3 小时一次”描述重复间隔或模式。§10.5 不定义完整的持续时间运算。

频率/重复模式信息属于 `Behavior` 语义内容的限定，但它与 `Context`、来源归因的理由和 `Provenance` 是不同维度。

例如，“工作日经常忘记服药”可以同时包含定性频率与工作日 `Context`；若来源另说“因为工作忙所以忘记”，还包含 §10.3 的来源归因理由。规范语义不得把这些语义压成一个频率字符串。

频率断言继续继承该 `Behavior` 的 §13 来源可追踪性；“谁报告该频率”或“谁根据日志推断该模式”属于 `Provenance`，而不是频率值本身。

§10.5 不把重复模式语义契约扩展到 `Preference` 或 `Relation`。若未来出现明确需求，应另行审议。

§17 规定 `Behavior.frequencies : BehaviorFrequency[0..*]` 作为独立的结构化限定信息，并允许在必要时具有局部 `provenance`。

§8.3 进一步规定：

- `observed_count` / `rate` / `recurrence` / qualitative 四种带判别标记的变体；
- 只有 count 的观测表示；
- `FrequencyPeriod`；
- 精确/近似 `precision` token；
- 每周星期计划与有限的 `day_part` token；
- 定性频率 token 集合；
- `BehaviorFrequency` 语义内容相等与完整限定信息相等。

持续时间运算、小时级重复模式、RRULE / cron、`Preference` 重复模式、JSON Schema 与 DSL 语法尚未定义。

### 10.6 旧版 `reasoning_note` 兼容性

历史 `Behavior.reasoning_note` 的人类可读说明能力继续保留，但其规范语义归属统一为 §5.8 的 `Annotation` 语义。

旧版 `reasoning_note` 不得因为字段名中的 “reasoning” 被解释为 PBDL-Core 自己执行并认证了正确推理、临床推理、已验证解释或因果推理。

如果旧版 `reasoning_note` 忠实承载来源已经明确表达的说明，其 `Annotation` 可以具有 `DIRECT` 来源语义。

如果人工标注者、模型、规则引擎或分析过程新增了来源未表达的解释，规范表示必须保持其真实的人工撰写或 `INFERRED` 派生语义区分；模型生成的新解释不得冒充 `DIRECT` 来源文本。

旧版 `reasoning_note` 不得替代结构化 `Behavior` 语义、必需的 `Provenance`、`Evidence`、§10.3 的理由/因果边界或派生结果边界。

§5.8 不得被解释为要求保存模型的隐藏思维链或私有推理轨迹。

§17 规定旧版 `reasoning_note` → `Behavior.annotations`，且 `Annotation` 采用轻量嵌入结构；更细的序列化以及作者/生成者表示仍留待后续定义。

## 11. Preference

`Preference` 表示某个 `Subject` 对选项、属性、治疗特征或结果所表达或推断出的倾向、选择、优先级、厌恶或偏好。

`Preference` 必须绑定到恰好一个 `Subject`，并且必须具有稳定的文档内身份。

`Preference` 本身不等价于：

- 观测到的 `Behavior`；
- 临床推荐；
- 风险结果；
- 冲突结果；
- 客观约束或障碍。

现实信息中可能存在客观约束或障碍，但当前规范不新增 `Constraint` 一级 Core 实体。相关语义边界保留为未来设计问题。

`Preference.category` 或显示标签不得自动充当 `Preference` 身份。

### 11.1 旧版 `associated_behavior` 兼容性

历史 `Preference.associated_behavior` 所表达的“偏好与行为之间存在关联”继续保留兼容价值，但其规范归属由 §14 的 `Relation` 规则承担。

在 PBDL 的规范语义中，`Preference.associated_behavior` 不得继续作为与 Core `Relation` 平行的第二套一级关联机制。

旧版 `Preference.associated_behavior` 必须规范化为显式的 Preference–Behavior `Relation`。

因此，历史字段继续作为旧版兼容输入概念保留，但符合规范的 `Preference` 不再同时维护：

- 专用的 `associated_behavior` 链接；
- 与其表达同一语义的 `Relation`。

如果旧输入使用自由文本 `Behavior` label 表达 `associated_behavior`，规范转换必须先将其解析到恰好一个 `Behavior` 身份。

- 0 个匹配：未解析 / 无效；
- 多个匹配：歧义 / 无效。

规范转换不得通过数组位置、最近文本、第一个匹配或 LLM 猜测来静默选择一个 `Behavior`。

旧版 `associated_behavior` 本身只证明来源声明 `Preference` 与某个 `Behavior` 存在某种关联。它不得自动意味着 `Preference` 导致 `Behavior`、`Behavior` 导致 `Preference`、`Preference` 源自 `Behavior`、`Preference` 与 `Behavior` 冲突，或 `Preference` 解释了 `Behavior`。

如果旧版或来源材料支持更具体的关系含义，规范语义应保留来源支持的最具体语义；但规范化不得生成来源没有支持的更强 `Relation` 类型。

当前规范不定义该 `Relation` 的具体规范类型代码或词汇 token。

每个符合规范的 `Preference` 实例必须实际具有至少一条 `provenance` 关联链路，使下游能够判断该 `Preference` 是直接表达还是外部推断所得。

直接表达与推断出的 `Preference` 可以具有相同的 `category` 与 `value`，但其 `provenance` 语义必须保持可区分，不得仅依赖自然语言 note 来判断。

### 11.2 `Preference` 时间语义

`Preference` 可以具有语义时间范围，用于描述其适用时间范围。

`Preference` 的表达时间、记录时间、抽取时间或生成时间属于 `Provenance` 时间；这些时间不得自动替代 `Preference` 的适用时间。

`Preference` 缺少语义时间信息时，不得解释为永久偏好。

不同时期的不同 `Preference` 信息可以作为不同 `Preference` 实例共存，例如某一时期拒绝注射、另一时期接受注射。

历史 `Preference` 正式字段表虽然没有独立 `temporal` 字段，但 v1 Core 可以表达 `Preference` 的时间适用范围，以避免把可随时间变化的偏好误解为永久状态。

### 11.3 旧版 `note` 兼容性

旧版 `Preference.note` 的兼容能力继续保留。

其历史人类可读说明能力继续保留，并在规范语义归属上统一解释为 §5.8 的 `Annotation` 语义。

`Preference.note` 不得承担 `preference_category`、`preference_value` 或其他结构化 `Preference` 机器语义的唯一表达。

例如，仅有 `note = "不喜欢打针"` 不得被视为规范结构化 `Preference` 语义内容的替代品。

`Preference` 的 `Annotation` 不得自动成为 `Evidence` 或 `Provenance`，也不得仅凭文本内容创建新的 `Behavior`、`Preference`、`Relation`、`Context`、因果断言或派生结果。

§17 规定旧版 `Preference.note` → `Preference.annotations`，并定义 `Annotation` 的最小 `text` + `provenance` 字段；更细的序列化以及作者/生成者表示仍留待后续定义。

`Preference` 的规范字段见 §17；`SourceDescriptor` / `Evidence` 与 `Confidence` 的具体表示见 §17.8；`PreferenceValue` 的 `coded` / `text` / `boolean` / `number` 带标签联合类型见 §8.4。

### 11.4 `PreferenceValue` 表示边界

`Preference.value` 必须使用 §8.4 的 `PreferenceValue`，不得使用任意无类型 JSON 或无标签字符串作为规范机器值。

`TextPreferenceValue` 是在词汇或类型无法可靠恢复时使用的保真回退，不是规避结构化语义的默认逃生口。

`boolean` 值 `false` 是明确的 value，不等于缺少 `Preference`。

`NumericPreferenceValue` 必须显式保留比较运算符；有量纲数值的 `unit` 不能被猜测。

§8.3–§8.4 不定义 `Preference` 重复模式、`Preference` 冲突、序数/强度分析、多选引擎、JSON Schema 或 DSL 语法。

## 12. Context

`Context` 的最小语义职责与具体规范表示见 §8.5 与 §12。

`Context` 用于表达解释某个 `Behavior` / `Preference` 时，与其发生、成立或被理解相关的情境背景或条件限定。它的职责是**限定语义解释**，而不是证明原因、执行推理、记录来源或承载软件工作流。

`Context` 的规范结构如下：

    Context {
        value       : ContextValue
        provenance? : Provenance[1..*]
    }

`ContextValue` 是 `coded` / `text` 带标签联合类型，详见 §8.5。

### 12.1 `Context` 不是兜底容器

`Context` 不得被当作“无法分类的信息都放进 Context”的默认兜底容器。

已经具有明确语义职责的信息，不得仅为了结构便利而重新解释为通用 `Context`：

- 信息从哪里来、如何产生，属于 §13 的 `Provenance`；
- `Behavior` / `Preference` / `Relation` 何时发生、成立或适用，属于 §5.7 的时间语义；
- 来源归因的理由、观测到的前置关系与推断解释，继续使用 §10.3 / §8.5–§8.6 的 `BehaviorFactor` 语义；
- 风险、冲突、推荐、评分、因果推断等派生分析属于 Core 外部的派生/应用结果；
- 工作流或应用状态默认属于 Core 外。

`Context` 不得作为绕过既有 `Provenance`、时间语义、`BehaviorFactor` / reason 或派生分析边界的替代容器。

### 12.2 `Context` 不建立因果关系

某因素被表示为 `Context`，不得自动表示该因素导致 `Behavior`、导致 `Preference` 或在临床意义上解释某个结果。

例如，`Behavior` 发生在 traveling context 中，只说明该 `Behavior` 具有 traveling 情境限定；不得自动推出 traveling 导致了该 `Behavior`。

如果来源明确表达“因为旅行忘记服药”，应使用 `BehaviorFactor` 的 `reported_reason` 语义，而不能仅靠 `Context` 获得理由或因果语义。

`Context` 不得仅因为某因素影响或限制行为，就自动把它定义为 objective `Constraint` / `Barrier`。

### 12.3 `Context` 保真回退

当情境概念可以可靠映射到术语时，规范化器应使用 `CodedContextValue`。

当来源包含情境信息，但无法可靠映射到术语时，`TextContextValue` 提供保真回退。

规范化器不得发明术语代码。

`Text` 回退不得让所有 `Context` 退化成自由文本，也不能成为任意元数据容器。

### 12.4 `Context` 与时间/频率语义边界

日历或日期时间形式的语义时间范围属于 `TemporalExtent`。

`Behavior` 的重复模式或星期计划属于 `BehaviorFrequency`。

“工作日”只有在来源语义是社会或生活情境概念时才可以作为 `Context`；如果它只是重复规则或日历筛选条件，则不得为了实现方便重复编码成 `Context`。

`Context` 不定义规则或谓词引擎。

### 12.5 未提供`Context`

`Behavior` / `Preference` 可以没有显式 `Context` 信息。

缺少 `Context` 不得被解释为：

- context-free；
- 普遍适用；
- unconditional；
- 在任何环境都成立。

它只表示当前规范语义没有提供额外的情境限定。

### 12.6 `Context` 的身份、引用与集合边界

`Context` 不要求独立身份，不加入 `Subject` / `Behavior` / `Preference` 的文档内身份命名空间，不进入根集合，也不成为 `Relation` 端点。

`Behavior.contexts` / `Preference.contexts` 的集合顺序不得产生语义优先级。

完整信息相等的 `Context` 重复项如何规范化，见 §8.5.3。

§8.5–§8.6 不新增共享 `Context` 身份、`ContextRef`、`Constraint` / `Barrier` 实体或 Communication 实体。

`Context` 的 JSON Schema 与 DSL 语法尚未定义。

## 13. `Evidence` 与 `Provenance`

`Provenance` 与 `Evidence` 的最小语义边界见 §13。

### 13.1 `Provenance`

`Provenance` 回答：

> “这条 `Behavior` / `Preference` / `Relation` 断言是怎么来的？”

`Provenance` 描述信息或语义断言的来源与产生路径。其语义必须足以让下游判断该信息来自什么来源或通过什么方式产生，并能够区分来源直接描述的信息与外部推断得到的信息。

概念上，`Provenance` 可以涉及：

- 来源类型；
- 来源身份或外部引用；
- 产生方式；
- 记录、抽取或生成该信息的主体 / 系统；
- 在必要时用于来源解释的时间信息；
- 该信息是否经过推断。

以上描述的是语义职责，不是字段列表或 Schema。

每个符合规范的 `Behavior` 必须至少具有一条 `provenance` 关联链路。

每个符合规范的 `Preference` 必须至少具有一条 `provenance` 关联链路。

每个符合规范的 `Relation` 断言必须至少具有一条 `provenance` 关联链路，或具有等价的可追踪来源语义。

`Relation` 断言的 `provenance` 不得由 `source` 端点或 `target` 端点的 `provenance` 自动替代。`Relation` 断言的来源追踪详细规则见 §14.7。

同一个 `Behavior`、`Preference` 或 `Relation` 断言可以具有多条 `provenance` 关联链路。

多条 `provenance` 不得被解释为该信息自动“更真实”或自动具有更高可信度。PBDL-Core 不负责证据加权、来源排序或真值裁决。

### 13.2 Evidence

`Evidence` 回答：

> “有什么材料支持、承载或记录了这条信息？”

`Evidence` 可以是支撑某项 `Behavior` / `Preference` 表示的材料或外部引用，例如：

- EHR 文本片段；
- 问卷回答；
- 访谈记录；
- 设备观测；
- 外部文档引用。

`Evidence` 与 `Provenance` 相关但不同。

`Provenance` 说明“信息如何产生以及从哪里来”；`Evidence` 说明“有哪些材料支持或承载该信息”。

`Evidence` 可以作为 `Provenance` 指向或关联的支持材料，但二者不得被视为完全同义的概念。

§17 规定 `Evidence` 为可选的 `Provenance.evidence` 嵌入集合，且不要求 `Evidence` 身份；具体字段与 `locator`/`content` 表示见 §17.8.5。

### 13.2.1 `Provenance` 时间边界

与 `Provenance` 相关的时间可以对应报告、记录、观测、抽取或生成等不同事件角色。

这类 `Provenance` 时间不得自动承担 `Behavior` / `Preference` / `Relation` 的语义时间范围。

同一条信息的语义时间与 `Provenance` 时间可以不同，也可以只提供其中之一。

§17 的 `Provenance` 不提供无角色的通用顶层 `time` 字段，因为单一 `TemporalValue` 无法在 `source` 与 `generator` 共存时无歧义地区分报告、记录、观测时间与抽取、生成时间。

§17.8.3 / §17.8.5 规定来源、报告、记录或观测相关时间的具体归属：使用角色明确的 `SourceTimeEvent`，并由 `SourceDescriptor` 或具体 `Evidence` 项承载。

§17.8.4 规定抽取或生成相关时间的具体归属：使用 `GeneratorDescriptor` 下角色明确的 `GeneratorTimeEvent`。

如果未来需要 `Provenance` 层级的事件时间线，应采用具有显式 `role` 语义的结构，不得重新引入无角色的通用 `Provenance` 时间。

### 13.3 DIRECT 与 INFERRED

`Provenance` 至少区分两类必须可区分的语义；具体表层 enum 名称当前规范不定义。

DIRECT / INFERRED 判断的是**结构化语义内容相对于来源内容的产生方式**，而不是处理链路中是否使用了某种模型或工具。

使用 LLM、NLP 或其他工具进行抽取、解析、规范化、术语映射或序列化转换，本身不得自动使该信息成为 INFERRED。

如果结构化语义忠实表示来源中已经明确报告、记录或观测到的内容，即使抽取或标准化过程由 LLM / NLP 完成，该信息仍可以属于 DIRECT。

只有当结构化语义内容超出来源直接表达、记录或观测的内容，并由模型、规则、分析过程或其他推导过程生成时，该信息才属于 `INFERRED` 来源语义。

#### DIRECT

DIRECT 表示信息直接来自某个来源的报告、记录或观测，例如：

- 患者自述；
- 问卷回答；
- 临床人员记录；
- 设备观测；
- 人工录入。

DIRECT 不得被解释为“已经证明绝对真实”。它只表示 PBDL 没有把该项语义标记为由外部推理过程生成的结论。

#### INFERRED

INFERRED 表示信息由 LLM、ML 模型、规则引擎、分析过程或其他推断过程根据其他输入生成。

INFERRED 信息不得静默表示成 DIRECT 或来源直接描述的信息。

规范语义表示必须使下游能够区分 `DIRECT` 与 `INFERRED` 来源语义，而不能仅通过自由文本说明猜测。

对于 Preference：

- 来源明确表达“我不想每天打针”，LLM 仅将其结构化抽取为“对注射的厌恶”时，仍可属于 DIRECT / expressed `Preference`；
- 来源没有明确表达该偏好，而模型根据多项行为记录推断“患者可能偏好低治疗负担方案”时，属于 INFERRED `Preference`。

即使两者最终具有相同的 `category` 或 `value`，其 `provenance` 语义仍必须保持可区分。

### 13.4 冲突来源与多来源

如果多个来源支持的是同一项结构化语义，一个 `Behavior` / `Preference` 可以关联多条 `provenance`。

如果不同来源表达的语义内容实质不同或相互冲突，规范表示不得通过 `provenance` 合并、对象折叠或其他方式丢失、掩盖这些冲突，或使冲突语义变得不可区分。

默认情况下，这些冲突内容应保持为不同的 `Behavior` / `Preference` 实例；未来若采用其他表示方式，也必须保持各项冲突语义可区分。

例如：

- 患者自述规律服药；
- 设备或记录显示存在漏服；

二者可以并存，但不应因为主体相同就被静默压缩成一个单一 `Behavior`，再仅附加两个 `provenance` 来源。

PBDL-Core 不负责自动裁决冲突，不在 §13 设计 ConflictAnalysis。

### 13.5 旧版来源字段兼容性

历史 `Behavior.evidence_source` 的来源追踪能力继续保留，但其规范方向是映射到统一的 `Provenance` / 来源语义，而不是把单一字符串字段定义为最终模型。

历史 `Preference.source_type` 同样收敛到统一的 `Provenance` / 来源语义。

`Behavior` 与 `Preference` 不应长期维护两套彼此独立、语义重复的来源机制。

`evidence_source` 与 `source_type` 的历史兼容意义继续保留；§17 规定其规范归属统一进入 `Provenance`，不再保留旧版平行字段。

### 13.6 `Confidence` 边界

置信信息不得成为所有 `Preference` 的强制属性。

`DIRECT` 的自述信息不得被迫赋予模型式置信信息。

如果置信信息用于 `INFERRED` 信息，其语义必须能够说明：

- 置信信息由谁或什么系统生成；
- 置信信息衡量什么；
- 置信信息对应哪个推断过程、模型或分析过程。

规范的 `confidence` 字段归属于可选的 `Provenance.confidence`；`value` + `metric` + 可选 `scale` 的最小具体契约与相等性见 §17.8.6。校准框架、阈值策略、度量名称的词汇治理、JSON Schema 与 DSL 序列化尚未定义。

历史 `Preference.confidence_score` 因此继续保留为待细化概念，但不得被解释为所有 `Preference` 的 Core 必需属性。

### 13.7 `Provenance` 身份

`Provenance` 自身仍不要求独立的文档内身份。

当前要求携带来源信息的规范语义断言至少包括：

- `Behavior`；
- `Preference`；
- `Relation` 断言。

§14 新增的 `Relation` 断言来源追踪要求，不得被解释为 `Provenance` 因此必须具有身份，也不得被解释为 `Relation` 因此必须具有身份。

当前仍没有 Core 场景要求其他实体通过稳定的 Core 引用指向某个 `Provenance` 实例。

`Provenance` 的最小字段与嵌入式附着方式见 §17；`SourceDescriptor` / `GeneratorDescriptor` / `Evidence`、嵌套 `provenance` 相等性与继承、`Confidence` 语义以及基于 `Text` / `TemporalValue` / `Confidence` 的来源相等性均在相关小节定义。共享 `Provenance` 身份、来源链式追踪、JSON Schema 与 DSL 序列化仍为 **TODO**。

## 14. Relations

`Relation` 用于在两个允许作为 `Relation` 端点的 PBDL 语义实体之间显式表达语义联系。

`Relation` 的最小语义组成如下：

- `source` 端点；
- `target` 端点；
- 关系类型概念。

`Relation` 的抽象语义见 §14；规范字段 `source` / `target` / `type` / `temporal` / `provenance` / `annotations` 与 `CoreEntityRef` 引用结构见 §17。JSON Schema 与 DSL 语法尚未定义。

`Relation` 的 `source` 与 `target` 必须是实体引用，并且必须分别解析到恰好一个允许的端点实体。

未定义引用是无效的。

歧义引用是无效的。

自由文本标签不得直接充当规范性的 `Relation` 端点引用。历史字符串标签可以作为旧版输入，但在形成规范语义之前，必须解析到明确的实体身份。

### 14.1 Core 允许的端点

PBDL-Core 的 `Relation` 允许以下端点组合：

- `Behavior` → `Behavior`
- `Behavior` → `Preference`
- `Preference` → `Behavior`
- `Preference` → `Preference`

PBDL-Core 不允许 `Subject` 作为 Core `Relation` 端点。

PBDL-Core 不允许 `Relation` 作为 `source` 或 `target`，因此不支持 `Relation→Relation` 或实体→`Relation`。

### 14.2 `Relation` 时间语义

`Relation` 可以具有语义时间范围，用于描述该 `Relation` 本身成立或适用的时间范围。

历史 `Relation.temporal` 的时间能力继续保留，其规范方向是映射到共享 Core 时间抽象，而不是沿用旧字符串表示。

`Relation` 的时间元数据与 `Relation` 类型语义是不同维度。

`Relation` 的时间元数据不得自动解释为 `precedes`、`follows`、之前、之后或其他顺序关系。

如果未来 `Relation` 词汇定义 `precedes`、`follows` 等类型，其先后语义属于 `Relation` 类型本身，而不是时间元数据的隐式解释。

对于历史 `Relation.temporal` 中混合了“适用时间”和“关系先后类型”的数据，规范转换不得在未区分真实含义时直接把旧值视为单一时间范围。

### 14.3 `Relation` 身份

`Relation` 在 v1 Core 最小模型中**不要求自身具有身份**。

这是因为当前没有已定义的 Core 引用需要指向 `Relation` 本身，且 `Relation` 也不是允许的 `Relation` 端点。

未来若 `Evidence` / `Provenance`、扩展或其他明确使用场景需要稳定引用 `Relation`，后续规范可增加 `Relation` 身份要求；当前规范不提前定义。

### 14.4 `Relation.type` 默认不表示因果关系

`Relation` 类型概念用于说明 `source` 与 `target` 之间“是什么关系”，但不得仅因为该类型存在或其名称看似有因果含义，就把它解释为因果关系。

PBDL-Core 当前不将`causal_effect` 定义为默认关系，也不把未经证据支持的因果权重作为 Core 的默认能力。

`Relation` 的语义时间范围与 `Relation.type` 顺序语义相互独立，见 §5.7。

§8.2 已定义以下 `TemporalValue` 规则：

- `TemporalValue` 的词法形式；
- 时间精度保留；
- 数值型偏移量 / `ZoneToken` 表示；
- 规范信息相等；
- `Interval` 的最小可比性。

因此，上述 `TemporalValue` 表示细节不再属于本节 TODO。

仍为 **TODO** 的是：

- 最终 JSON Schema 集成；
- DSL 语法与序列化；
- 规范性 `Relation` 词汇与具体关系类型代码；
- 逆关系约定；
- 派生 relation-strength 工件结构；
- `Relation` 词汇的序列化。

### 14.5 显式 `Relation` 边界

`Relation` 表示两个允许端点之间由规范语义**显式声明**的类型化语义联系。

仅仅因为两个实体：

- 属于同一 `Subject`；
- 同时出现或时间相近；
- 具有相同 `Context`；
- 出现在同一 `Evidence` 或来源材料中；
- 出现在同一句话或相邻字段；
- 使用相同的术语代码或类别；

规范化不得自动创建 `Relation`。

如果上游模型、规则引擎或分析过程基于这些信息推断存在 `Relation`，该 `Relation` 属于 INFERRED 关系断言，并继续遵守 §13 的 `provenance` / `derivation` 边界。

### 14.6 `Relation.type` 语义契约与方向性

每个符合规范的 `Relation` 必须使用具有稳定、机器可解释语义定义的关系类型。

`Relation` 类型定义 `source` / `target` 在关系中的语义角色，并且必须让符合规范的实现能够判断其方向性，例如有向、对称或非定向。

每个规范性关系类型定义必须明确允许的端点语义角色或端点种类。具体关系类型可以比全局端点矩阵更严格，但不得扩大该矩阵允许的 Core 端点组合。

每个规范性关系类型定义必须明确其因果语义状态：要么明确承载因果语义，要么明确属于非因果语义。

如果关系类型定义没有明确赋予因果语义，符合规范的使用方不得根据类型名称、方向性、端点顺序或其他隐式线索把它解释为因果关系。

`Relation` 类型不得只是一段自由文本说明、显示标签或 UI 文案。

符合规范的 `Relation` 必须使用其语义由适用的 PBDL 词汇或术语 binding 定义的关系类型。未定义或仅自由文本描述的关系类型语义不得被当作规范性机器语义。

当前规范不定义完整的 `Relation` 词汇、具体代码、序列化形式或开放/封闭词汇策略，也不新增具体因果关系类型。`Relation` 的规范结构字段见 §17；规范关系词汇仍待专门定义。

对于有向关系类型，交换 `source` / `target` 会改变或破坏该关系类型所定义的语义。

对于对称或非定向关系类型，交换端点顺序不得被解释为不同的关系语义。

在不知道关系类型的方向性语义时，规范化不得自行猜测、反转或重排端点。

`source → target` 的端点顺序本身不得自动建立因果关系、时间先后、影响、优先级、evidence-for 或 parent/child 语义；这些语义只能由关系类型定义明确规定。

有向 `Relation` 不得因为具有方向性就自动等价为因果 `Relation`。

### 14.7 `Relation` 断言的 `Provenance`

每个符合规范的 `Relation` 断言必须具有至少一条 `provenance` 关联链路，或具有等价的可追踪来源语义。

`Relation` 断言的 `provenance` 不得由 `source` 端点或 `target` 端点的 `provenance` 自动替代。

端点断言与关系断言是不同的语义陈述。例如：

- `Behavior` A 可以来自设备观测；
- `Preference` B 可以来自患者自述；
- A 与 B 之间的关系可以由模型推断。

此时两个端点可以分别具有 `DIRECT` 来源语义，而 `Relation` 断言本身仍属于 `INFERRED`。

`Relation` 断言的 DIRECT / INFERRED 判定继续遵守 §13：依据关系语义内容是否相对于来源内容经过推导，而不是处理链路中是否使用了 LLM、NLP 或其他工具。

如果来源明确表达某个 `Relation`，而 LLM / NLP 只是忠实抽取该关系、没有新增语义推断，则该 `Relation` 断言可以属于 DIRECT，即属于来源描述的关系。

如果 `Relation` 来自模型、规则引擎、统计过程或其他分析推断，它必须保持 `INFERRED` 来源语义，不得静默表示为 `DIRECT` 来源描述的 `Relation`。

如果 `Relation` 表达来源归因的理由，它仍继续遵守 §10.3：来源归因的理由不等价于已经验证的因果关系。

同一个 `Relation` 语义断言可以具有多条 `provenance` 关联链路，但更多 `provenance` 不得自动意味着该 `Relation` 更真实、更强或更具有因果性。

### 14.8 不同 `Relation` 断言与去重

相同端点对不代表相同的 `Relation` 断言。

不同的：

- 关系类型；
- direction；
- 时间适用范围；
- `DIRECT` / `INFERRED` 派生语义；
- 来源追踪所支持的含义；

这些差异都可以使 `Relation` 断言在语义上不同。

语义上不同的 `Relation` 断言必须保持可区分；规范化不得仅因为 `source` / `target` 相同就静默合并。

规范化可以合并真正语义等价、端点相同、`type` 相同、方向相同、时间适用范围相同，且合并不会丢失 `provenance` 或 `derivation` 差异的重复 `Relation` 断言。

当前规范不定义具体去重算法。

### 14.9 `Relation` 身份规则保持不变

§14 不改变身份规则：`Relation` 在当前 v1 Core 最小模型中仍然不要求自身具有身份。

新增的 `Relation` 来源追踪要求不得被解释为 `Relation` 因此获得必需身份。

`Relation` 仍不得作为 `Relation` 端点，端点矩阵保持不变。

### 14.10 `Relation` 时间语义独立性

`Relation` 的语义时间范围继续表示该 `Relation` 本身何时成立或适用。

`TemporalExtent`、关系类型与方向性是三个不同维度。

存在时间元数据不得自动把关系类型推断为 `precedes` / `follows`；关系类型有方向性，也不得自动生成时间顺序语义。

### 14.11 `Relation.weight` 仍属于派生结果

历史 `Relation.weight` 的处置结论保持为 **MOVE_DERIVED**。

`Relation.weight` 不得重新成为默认 PBDL-Core `Relation` 的内在语义强度。

旧 `weight` 可能代表相关系数、模型评分、排序权重、类似置信信息的值、关联强度、因果效应估计等彼此不同的语义，Core 不能把它们视为一个统一概念。

如果外部分析提供关系强度、统计量、评分或效应估计，该结果属于派生/分析工件。其度量含义、派生方法、模型/算法、来源追踪、版本与适用端点/关系需要由未来的派生结果规范明确；§14 不定义该 Schema。

来源描述的定性强度与派生的数值型关系强度必须保持可区分。

例如，来源中的“患者强烈偏好口服药”不能仅因为出现“强烈”就被转换成 `Relation.weight = 0.9`；文本中的“二者高度相关”也不能在没有统计定义时被伪造成数值型关系权重。

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

`system`、`code`，以及存在时的 `version` 必须是非空字符串。

Core 不得要求 `system` 一定是 URI；具体术语绑定规范可以进一步约束 `system`，但 Core 不做该假设。

`Coding` 的机器语义身份为：

    Coding identity = system + code

`display` 只是人类可读表示，不得改变 `Coding` 的机器身份。

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

因此，相同 `system + code`、不同 `version` 的 `Coding` 仍共享基本机器身份，但不得视为规范信息相等。

不同 `display` 也不得改变机器身份，但会使规范信息表示不相等。

Core 不得自动对 `system` / `code` / `version` 执行 trim、case-fold、URI-normalize 或术语规范化。

当前规范不定义任何具体 SNOMED CT、LOINC、ICD 或其他医学术语代码。

## 16. 语义约束

当前规范的语义约束如下：

1. PBDL-Core 必须区分来源直接描述的信息与外部推断、分析或计算得到的信息。
2. PBDL-Core 不得因为信息被写入 PBDL，就宣称该信息在现实世界中已经被认证为绝对真实。
3. 一个 PBDL 文档必须至少包含一个 `Subject`，并可以包含多个 `Subject`。
4. `Subject`、`Behavior` 与 `Preference` 必须具有文档内身份。
5. `Subject`、`Behavior` 与 `Preference` 共享同一个文档内身份命名空间；其标识符必须在所属 PBDL 文档内唯一。
6. 数组位置或列表顺序不得充当规范性身份标识符。
7. `Behavior` 与 `Preference` 必须各自绑定到恰好一个 `Subject`。
8. 每个符合规范的 `Behavior` 必须实际具有至少一条 `provenance` 关联链路。
9. 每个符合规范的 `Preference` 必须实际具有至少一条 `provenance` 关联链路。
10. 规范语义表示必须能区分 `DIRECT` 与 `INFERRED` 来源语义。判断依据是结构化语义内容相对于来源内容是否经过推导，而不是处理链路中是否使用过 LLM、NLP、模型或其他工具。
11. 仅使用工具进行抽取、解析、规范化、术语映射或序列化转换，不得自动使信息成为 INFERRED。
12. INFERRED 信息不得静默表示成 DIRECT 或来源直接描述的信息。
13. 同一个 `Behavior` / `Preference` 可以具有多条 `provenance` 关联链路，但多来源不得自动表示更高真值或可信度。
14. 如果不同来源表达的语义内容实质不同或冲突，规范表示不得通过 `provenance`/`source` 合并、对象折叠或其他方式丢失、掩盖这些冲突，或使冲突语义不可区分。默认情况下，应使用彼此分离的 `Behavior` / `Preference` 实例。
15. `Provenance` 与 `Evidence` 不得被当作完全同义的概念。
16. 置信信息不得成为所有 `Preference` 的强制属性；`DIRECT` 的自述信息不得被迫赋予模型式置信信息。
17. `Provenance` 在 §13 中不要求独立身份。
18. 语义时间与 `Provenance` 时间不得视为同一个时间概念；`Provenance` 中的报告时间不得自动替代 `Behavior` / `Preference` / `Relation` 的语义时间。
19. `Behavior`、`Preference` 与 `Relation` 应使用共享的 Core 时间抽象表达语义时间范围。
20. Core 时间抽象至少支持 `Instant`、`Interval` 与未提供语义时间三种最小语义情况。
21. `Interval` 必须至少具有一个有效边界；若 `start` 与 `end` 同时存在且可比较，`start` 不得晚于 `end`。
22. 单边界 `Interval` 中未提供的另一侧边界只表示该边界未提供，不得自动解释为永久、ongoing、一直延伸到现在或未来、从无限过去开始，或数学意义上的无界区间。
23. 缺少语义时间信息不得被解释为永久、当前、始终、反复或“时间不重要”。
24. 规范化必须保留来源实际支持的时间精度，不得发明来源未提供的时间精度。
25. 来源未提供时区或偏移量时，规范化不得凭空补充；来源已经提供时，规范表示必须能够保留。
26. 规范语义中保留的相对时间表达必须具有明确锚点；没有明确锚点的裸相对时间不得被假装成唯一确定的绝对时间范围。
27. `Relation` 的时间元数据不得自动承担 `precedes` / `follows` 等 `Relation` 类型的顺序语义。
28. `Behavior` 的 `type`、`Preference` 的 `category`、显示标签与 `Relation` 类型不得自动充当实体实例身份。
29. Core 引用必须在当前文档的引用范围内解析到恰好一个实体。
30. 未定义引用与歧义引用均无效。
31. `Relation` 的 `source` / `target` 必须使用明确的实体引用，不能使用未解析的自由文本标签。
32. Core `Relation` 端点只允许 `Behavior` 与 `Preference`；`Subject` 与 `Relation` 都不是允许的 `Relation` 端点。
33. `Relation` 在 v1 Core 最小模型中不要求身份，并且不得作为 `Relation` 端点。
34. PBDL-Core 不得把未经证据支持的因果权重作为来源直接描述的信息或默认 Core 语义。
35. Treatment Pathway 不属于 PBDL-Core。
36. 旧版 `trigger` / `triggered` 命名不得单独建立因果语义；字段名称本身不得被视为因果证据。
37. 来源归因的理由必须与已经验证的因果语义保持可区分；规范语义不得自动把“某来源声称 X 是 Y 的原因/理由”升级为已经验证的因果 `Relation`。
38. 观测或记录到的关联、共现或时间前置关系，不得自动升级为来源归因的理由或因果断言；时间上的先后不得自动推出因果关系。
39. INFERRED 解释不得静默表示为 DIRECT 来源归因的理由，并继续遵守 §13 关于语义派生的 DIRECT / INFERRED 判定规则。
40. 如果来源不支持症状相关方向，规范化不得从 `symptom_triggered` 字段名或时间顺序中发明方向；已知方向也不得自动等价为因果关系。
41. `Context` 不得自动建立因果关系；情境限定不得自动等价为理由、因果解释或已经验证的因果效应。
42. `Behavior` / `Preference` 缺少显式 `Context` 时，不得解释为无情境、普遍适用或无条件；它只表示未提供额外的情境限定。
43. `Context` 不得作为 `Provenance`、语义时间、诱因/理由语义、派生分析或工作流/应用状态的默认替代容器。
44. 旧版 `communication_status` 不得仅凭字段名决定规范语义类别，也不得默认定义为单一通用 `Behavior` 状态。
45. 实际沟通 `Behavior`、沟通情境元数据、`Provenance` 信息与工作流/应用状态必须保持语义可区分。
46. `communicated` / `reported` / `acknowledged` 不得自动等价为 `verified`、`true`、`agreed` 或来源内容已经得到事实认证。
47. `Behavior` 的频率/重复模式必须与 §5.7 的语义时间范围保持可区分；持续时间或适用区间不得自动等价为重复模式。
48. 观测或报告的发生次数在参考时间窗内不得自动等价为重复模式或稳定重复规则。
49. 定性或近似频率不得通过规范化擅自数值化、阈值化或提高到来源未提供的精确度。
50. 预期或处方计划不得自动表示实际患者 `Behavior` 的频率；实际 `Behavior` 频率也不得自动表示处方计划。
51. Recurring 模式不得通过规范化自动展开成来源没有提供的虚构具体观测发生记录。
52. 多个观测发生记录不得自动总结为重复模式；若模式来自外部推断，该模式必须保留 `INFERRED` 来源语义，并不得静默表示为 `DIRECT` 来源描述的频率。
53. 缺少频率/重复模式信息不得被解释为发生一次、只发生一次、不重复、不规律、连续发生或任何具体重复模式。
54. 规范化不得在缺少参考周期时发明频率值，也不得在缺少分母或预期机会次数时发明依从性比率、依从性百分比或其他比例。
55. 频率/重复模式语义不得成为所有 `Behavior` 的强制属性。
56. 不得仅因为实体共现、属于同一 `Subject`、时间相近、`Context` 相同或共享来源材料，就隐式创建 `Relation`。
57. `Relation` 类型必须具有定义明确的机器语义，并决定端点角色与方向性；`source` / `target` 顺序本身不得建立因果关系、时间先后、重要性或其他未由关系类型定义的语义。
58. 有向 `Relation` 不得自动等价为因果 `Relation`；对于对称或非定向关系类型，交换端点顺序不得被解释为不同的关系语义。
59. 旧版 `Preference.associated_behavior` 在规范语义中必须统一表示为显式的 Preference–Behavior `Relation`，不得继续形成与 `Relation` 平行的规范链接机制。
60. 旧版 `associated_behavior` 引用必须解析到恰好一个 `Behavior` 身份；未定义、未解析或歧义映射都无效，规范转换不得静默猜测目标。
61. 规范转换不得仅凭旧版 `associated_behavior` 发明比来源支持更强的关系语义。
62. 每个符合规范的 `Relation` 断言必须具有至少一条 `provenance` 关联链路或等价的可追踪来源语义；端点 `provenance` 不得自动替代 `Relation` 断言的 `provenance`。
63. `INFERRED` `Relation` 断言不得静默表示为 `DIRECT` 来源描述的 `Relation`，即使其端点分别具有 `DIRECT` 来源语义。
64. 语义上不同的 `Relation` 断言不得仅因为端点相同而被静默合并；关系类型、方向、时间适用范围以及 `derivation` / `provenance` 的差异都必须得到保留。
65. `Relation.weight` 不得作为默认 Core `Relation` 的内在语义强度；派生的数值型强度或统计量必须与来源描述的关系语义保持可区分。
66. 未定义或仅自由文本描述的关系类型语义，不得被当作规范机器语义。
67. `Annotation` 不得作为已有结构化规范机器语义的唯一替代载体；符合规范的使用方不得被迫解析自由文本 `Annotation` 才能确定核心机器语义。
68. `Annotation.text` 不得自动创建新的 `Behavior`、`Preference`、`Relation`、`Context`、因果断言、风险结果、推荐或其他派生分析结果。
69. `Annotation` 不得替代必需的 `Provenance`；`source` / `generator` / DIRECT / INFERRED `derivation` 不得只通过自由文本说明表达，再要求下游猜测。
70. 旧版 `Behavior.reasoning_note` 与 `Preference.note` 在规范语义归属上统一为 `Annotation` 语义，但 `Annotation` 不得因此获得必需身份或 `Relation` 端点地位。
71. 模型或分析过程在来源未表达的基础上生成的解释性 `Annotation` 必须保持 `INFERRED` 派生语义，并不得伪装为 `DIRECT` 来源文本；忠实抽取或规范化本身不得自动使 `Annotation` 成为 `INFERRED`。
72. `Annotation` 不得自动等价于 `Evidence`，也不得仅凭文本内容建立因果关系或 `Relation`。
73. `Annotation` 与结构化规范语义冲突时，符合规范的使用方不得仅根据 `Annotation` 静默覆盖结构化语义。
74. PBDL-Core 不得要求隐藏思维链、私有模型推理轨迹、内部草稿或其他隐藏模型推理过程作为规范性 `Annotation` 内容。

跨文档身份/引用协议、沟通词汇、`Constraint` / `Barrier` 模型、规范性关系词汇、代码、逆关系约定、派生关系强度工件 Schema、JSON Schema、DSL 语法与术语词表仍为 **TODO**。

## 17. 规范对象模型

本节定义 PBDL-Core 的字段级规范对象模型。

本节定义规范对象图、字段归属、必需/可选属性、基数、嵌套限定信息归属、类型化引用归属、必需 `provenance` 的附着方式，以及旧版字段到规范表示的归属。

本节**不定义** JSON 序列化形式、JSON Schema、DSL 语法或实现规范。

[schema/pbdl-v1.schema.json](schema/pbdl-v1.schema.json) 仍只是 JSON Schema Draft 2020-12 占位文件；本节不得被解释为已经修改或定义该 Schema 文件。

### 17.1 规范根对象：`PBDLDocument`

规范根对象名为 `PBDLDocument`。

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| `pbdl_version` | `VersionToken` | 1 | 必需 |
| `subjects` | `Subject` | 1..* | 必需集合 |
| `behaviors` | `Behavior` | 0..* | 必需集合，可以为空 |
| `preferences` | `Preference` | 0..* | 必需集合，可以为空 |
| `relations` | `Relation` | 0..* | 必需集合，可以为空 |

规范文档必须通过 `pbdl_version` 显式声明 PBDL 版本。

`VersionToken` 是受约束的字符串词法 token。

当前 PBDL 1.0 文档的 `pbdl_version` 必须精确为：

    "1.0"

`VersionToken` 只表示 PBDL 语言或规范模型版本，不得携带实现构建号、git SHA、模型版本、Schema URI 或产品版本。

当前规范不允许实现自行定义的版本 token 冒充 PBDL 版本。未来 PBDL 版本应由对应规范显式定义新的规范 token。

`PBDLDocument` 不得增加文档级风险、推荐、Pathway、工作流状态、全局 `Annotation` 容器或任意全局元数据容器作为 §17 的 Core 字段。

### 17.2 根集合顺序

`subjects`、`behaviors`、`preferences`、`relations` 的集合位置不得承担实体身份。

除非未来某个嵌套类型另行定义顺序语义，规范集合顺序不得被下游解释为：

- 优先级；
- 因果关系；
- 时间顺序；
- 排名；
- 语义身份。

上述根集合在语义模型中均为顺序无关。字节级确定性数组排序 **不属于**当前语义规范模型；该能力明确留给未来的确定性序列化规范，见 §22.11。

### 17.3 Subject

`Subject` 的规范字段清单：

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| `id` | `EntityId` | 1 | 必需 |

§17 不给 `Subject` 增加姓名、年龄、性别、地址、电话、完整人口统计信息、完整 EHR 记录、`annotations`、`provenance`、`context` 或工作流元数据。

`Subject` / `Behavior` / `Preference` 继续共享文档内身份命名空间。

`EntityId` 是非空、区分大小写的 ASCII 词法 token：

    [A-Za-z_][A-Za-z0-9._-]*

`EntityId` 必须满足该词法形式。

`EntityId` 不要求 UUID，不承载全局身份，也不得由 `display`、`type`、`Coding.code` 或集合位置派生。

`Subject` / `Behavior` / `Preference` 继续共享同一个文档内 `EntityId` 命名空间。

### 17.4 Behavior

`Behavior` 的规范字段清单：

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| `id` | `EntityId` | 1 | 必需 |
| `subject` | `SubjectRef` | 1 | 必需 |
| `type` | `Coding` | 1 | 必需 |
| `executor` | `ActorRef` | 0..1 | 可选 |
| `temporal` | `TemporalExtent` | 0..1 | 可选 |
| `frequencies` | `BehaviorFrequency` | 0..* | 可选集合 |
| `contexts` | `Context` | 0..* | 可选集合 |
| `factors` | `BehaviorFactor` | 0..* | 可选集合 |
| `provenance` | `Provenance` | 1..* | 必需 |
| `annotations` | `Annotation` | 0..* | 可选集合 |

规范字段 `type` 正式承担旧版 `behavior_type` 的结构化机器语义：

- 旧版 `Behavior.behavior_type` → `Behavior.type`。

规范模型不得同时保留 `type` 与 `behavior_type` 两套平行字段。

#### 17.4.1 `Behavior.type`

`Behavior.type` 使用 §15 已定义的 `Coding` 语义类型。

`Coding` 的概念职责保持不变：

- `code + system` 承担机器语义身份；
- display 为人类可读展示；
- `version` 为可选信息。

`Coding` 的规范对象结构与相等性见 §15；JSON Schema 与 DSL 序列化尚未定义。

`Behavior.type` 必须承担结构化机器语义，不得由 `Annotation` 替代。

#### 17.4.2 `Behavior.executor`

`executor` 保留旧版 `executor` 的语义能力，并采用可选的 `ActorRef`。

`executor` 表示谁执行或参与 `Behavior`；它不得等价于 `Subject` 的归属关系。

`ActorRef` 的规范联合类型如下：

    ActorRef = SubjectRef | ExternalActorRef

`SubjectRef` 变体使用 §17.7 定义的规范引用对象：

    { "ref": EntityId }

`ExternalActorRef` 变体使用与 `SubjectRef` 结构互斥的对象：

    {
        "kind": "person" | "device" | "software" | "other",
        "external_id"?: {
            "system": string,
            "value": string
        },
        "display"?: Text,
        "role"?: Text
    }

`ExternalActorRef.kind` 为必需字段。

`external_id`、`display`、`role` 均可选。

若 `external_id` 存在，其 `system` 与 `value` 必须是非空字符串。`external_id` 表示外部命名空间中的稳定标识符，**不属于** PBDL Core `EntityId` 命名空间。

`display` / `role` 仅用于人类可读描述，不得单独建立稳定的 actor 身份。

照护者或临床人员通常可以使用 `kind = "person"`，并通过 `role` / `display` 描述；设备使用 `kind = "device"`；外部软件或系统使用 `kind = "software"`。

`ActorRef` 联合类型按对象结构进行判别：

- 含必需 `ref` 且不含 `ExternalActorRef` 字段的对象 → `SubjectRef`；
- 含必需 `kind` 且不含 `ref` 的对象 → `ExternalActorRef`。

同时含 `ref` 与 `kind` 的 `ActorRef` 必须视为无效的规范表示。

`ExternalActorRef` 是不具有 Core 身份的嵌入式描述结构，不进入 `Subject` / `Behavior` / `Preference` 的文档内身份命名空间，也不成为 `Relation` 端点。

如果来源提供稳定的 `external_id`，该外部身份可以用于表达多个 `Behavior` 中的同一外部 actor。

如果只有 `display` / `role` 而没有 `external_id`，符合规范的使用方不得因为文本相同，就断言多个 `Behavior` 描述的是同一个稳定 actor 实例。

当前规范不新增 Actor / Participant 一级实体、Participant 身份命名空间或 Participant `Relation` 端点。

#### 17.4.3 `Behavior.temporal` 与 `TemporalExtent`

`Behavior.temporal` 是可选的单个 `TemporalExtent`。

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

`Instant.at` 为必需字段。

`Interval` 的 `start` / `end` 至少一个存在。

`TemporalExtent.provenance` 可选；一旦存在，集合必须至少包含一个 `Provenance`，显式空集合无效。

`TemporalExtent` 具有可选的局部 `provenance`。

原因是所属对象的 `provenance` 无法无损覆盖以下情况：

- `Behavior` 为 DIRECT，但 `temporal` 来自另一来源；
- `Behavior` 为 DIRECT，但 `temporal` 由模型推断；
- `Preference` 所属对象的 `provenance` = {P1,P2}，但 `temporal` 仅由 P1 支持；
- `Relation` 断言为 DIRECT，但时间适用范围为 INFERRED。

`TemporalExtent.provenance` 必须完整复用 §17.10 的继承、覆盖、相等性与规范省略规则：

- 局部字段缺失 → 继承直接所属对象当前适用的完整 `provenance` 集合；
- 局部字段存在 → 完全覆盖继承；
- 不允许叠加合并；
- 显式局部集合与继承得到的完整集合语义等价 → 规范形中省略。

当前规范不得为时间 `provenance` 发明第二套机制。

`TemporalValue` 的词法约束、精度、时区保留与相等性见 §8.2。

§5.7 允许带锚点保留相对时间，或在规范化前将其解析。§17 对规范表示施加更严格要求：`TemporalExtent` 的结构化边界必须是 §8.2 定义的合法 `TemporalValue`。

如果上游能够基于明确锚点，将相对时间表达可靠解析为 `Instant` / `Interval`，则可以规范化。

如果不能可靠解析，规范化不得发明绝对时间或把未解析的相对时间表达伪装成 `TemporalExtent`。

原始相对时间措辞可以通过 `Evidence` / `Annotation` 保真保存，但不得作为结构化 `TemporalExtent`。

当 `Interval` 同时具有 `start` 与 `end` 时，顺序有效性使用 §8.2.6 的保守可比性规则。

`TemporalExtent` 的内容相等与完整规范信息相等统一按 §22.9.1 处理。

#### 17.4.4 `Behavior.frequencies`

`Behavior.frequencies` 为可选的 `BehaviorFrequency[0..*]`。

`BehaviorFrequency` 的具体带判别标记联合类型、有效性与相等性见 §8.3。

`Behavior.frequencies` 集合可以同时包含不同变体，例如：

- `recurrence` = 每天一次；
- observed_count = 上周发生 3 次。

二者表达不同的语义维度，不得因为指向同一个 `Behavior` 就互相覆盖或自动去重。

规范表示不得使用 `frequency: "每天两次"` 等任意字符串作为最终机器语义的替代。

每个 `BehaviorFrequency` 变体可以携带局部 `provenance`。

`BehaviorFrequency` 的局部 `provenance` 完全遵守 §17.10：

- 局部字段缺失 → 继承直接所属对象当前适用的完整 `provenance` 集合；
- 局部字段存在 → 完全覆盖继承；
- 不允许叠加合并；
- 冗余的显式局部集合 → 规范形中省略。

若 `ObservedCountFrequency.window` 自身携带 `TemporalExtent.provenance`，也独立遵守同一套 §17.10 规则。

处方或预期计划不得规范化成实际 `BehaviorFrequency`，除非当前 `Behavior` 断言本身描述的就是遵循计划或处方的行为语义。

#### 17.4.5 `Behavior.contexts`

`Behavior.contexts` 为可选的 `Context[0..*]`。

`Preference.contexts` 同样使用 §8.5 定义的 `Context` 类型。

`Context` 不是具有身份的实体，不进入文档根集合，也不是 `Relation` 端点。

`Context` 的具体字段如下：

    Context {
        value       : ContextValue
        provenance? : Provenance[1..*]
    }

`ContextValue`、相等性与 text 回退见 §8.5。

`Context` 的局部 `provenance` 完全遵守 §17.10：

- 局部字段缺失 → 继承直接所属对象当前适用的完整 `provenance` 集合；
- 局部字段存在 → 完全覆盖继承；
- 不允许叠加合并；
- 冗余的显式完整集合 → 规范形中省略。

如果 `Context` 只由所属对象 `provenance` 的真子集支持，则局部 `provenance` 必须存在。

`Context` 集合顺序不得表示优先级、因果关系或时间顺序。

`Context` 不得成为任意元数据容器，也不得替代 `TemporalExtent`、`BehaviorFrequency`、`BehaviorFactor`、`Provenance`、`Relation` 或工作流/应用元数据。

#### 17.4.6 `Behavior.factors`

`Behavior.factors` 为可选的 `BehaviorFactor[0..*]`。

`BehaviorFactor` 的具体类型见 §8.6：

    BehaviorFactor {
        role        : FactorRole
        factor      : FactorValue
        direction   : FactorDirection
        provenance? : Provenance[1..*]
    }

`BehaviorFactor` 承载 `Behavior` 局部、非 Core 因素语义，包括来源归因的理由、观测关联、前置关系、外部解释性因素与旧版症状相关方向。

`BehaviorFactor` 不得成为通用的 `Relation` 替代机制。

如果该因素实际是当前文档中的 `Behavior` / `Preference` 实体，并表达显式类型化实体关系，规范模型必须使用 `Relation`。

`BehaviorFactor` 必须是结构化限定信息，而不是任意推理字符串。

`BehaviorFactor` 的局部 `provenance` 完全遵守 §17.10。

特别地，如果所属 `Behavior` 为 `DIRECT`，而解释性因素来自模型或分析推断，则该因素必须显式写出局部 `provenance`，使有效 `derivation` 保持 `"inferred"`，不能继承成所属对象的 `DIRECT`。

`FactorRole`、`FactorDirection`、`FactorValue`、因果边界与相等性详见 §8.6。

#### 17.4.7 旧版 `Behavior` 字段归属

符合规范的 `Behavior` 不得保留 `communication_status` 字段。

旧版 `communication_status` 按实际语义规范化为：

- 实际沟通行为 → `Behavior`；
- 沟通情境限定 → `Context`；
- 来源或报告信息 → `Provenance`；
- 工作流或应用状态 → Core 外。

符合规范的 `Behavior` 不得保留 `risk_tag`、`validity_flag` 或 `reasoning_note`：

- `risk_tag` → 派生/应用结果；
- `validity_flag` → 校验器/报告输出；
- `reasoning_note` → `annotations`。

其他主要旧版字段映射如下：

| 旧版字段 | 规范字段归属 |
|---|---|
| `behavior_type` | `Behavior.type` |
| `executor` | `Behavior.executor` |
| `temporal_scope` | `Behavior.temporal` |
| `evidence_source` | `Behavior.provenance` |
| `behavior_trigger` / `symptom_triggered` | 来源只支持情境性或共现限定时使用 `Context`；来源支持 `Behavior` 局部、非 Core 的理由/关联/前置关系/解释/方向语义时使用 `Behavior.factors`；两端均为 Core 实体且语义为显式类型化关系时使用 `Relation` |

### 17.5 Preference

`Preference` 的规范字段清单：

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| `id` | `EntityId` | 1 | 必需 |
| `subject` | `SubjectRef` | 1 | 必需 |
| `category` | `Coding` | 1 | 必需 |
| `value` | `PreferenceValue` | 1 | 必需 |
| `temporal` | `TemporalExtent` | 0..1 | 可选 |
| `contexts` | `Context` | 0..* | 可选集合 |
| `provenance` | `Provenance` | 1..* | 必需 |
| `annotations` | `Annotation` | 0..* | 可选集合 |

`PreferenceValue` 的具体带标签联合类型、有效性、迁移与相等性见 §8.4。

旧版字段归属：

| 旧版字段 | 规范字段归属 |
|---|---|
| `preference_category` | `Preference.category` |
| `preference_value` | `Preference.value` |
| `source_type` | `Preference.provenance` |
| `confidence_score` | 仅在 `Provenance.confidence` 的语义以及生成过程或推断过程都可以说明时使用 |
| `associated_behavior` | `Relation` |
| `note` | `Preference.annotations` |
| `preference_conflict_flag` | 派生 `ConflictAnalysis` / 应用结果 |

符合规范的 `Preference` 不得继续保留 `source_type`、`confidence_score`、`associated_behavior`、`note`、`preference_conflict_flag`、`preference_category` 或 `preference_value` 作为与新字段归属平行的旧版字段。

旧版 `confidence_score` 不得无条件搬入 `Provenance.confidence`；只有在其 `metric` 含义以及生成过程或推断过程都可以说明时才可保留。

### 17.6 Relation

`Relation` 的规范字段清单：

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| `source` | `CoreEntityRef` | 1 | 必需 |
| `target` | `CoreEntityRef` | 1 | 必需 |
| `type` | `Coding` | 1 | 必需 |
| `temporal` | `TemporalExtent` | 0..1 | 可选 |
| `provenance` | `Provenance` | 1..* | 必需 |
| `annotations` | `Annotation` | 0..* | 可选集合 |

`Relation` 继续不要求 `id` 字段。

`Relation` 不要求自身身份：Core `Relation` 表达语义断言，而不承诺跨文档版本的稳定生命周期句柄。

同一端点对上，`type`、时间适用范围或 `provenance` 语义不同的 `Relation` 断言，仍应依据其规范语义内容保持可区分。

只有 `Annotation` 发生变化，不得被解释为 `Relation` 因此获得新的 Core 身份；`temporal` / `type` / `provenance` 语义内容的变化则可以表示不同的 `Relation` 断言。

跨版本生命周期跟踪、审计句柄，以及 Core 外派生工件对特定 `Relation` 断言的稳定定位，属于应用或扩展层职责；不得用集合位置冒充 Core 身份。

符合规范的 `Relation` 不得具有 `weight` 字段、嵌套 `Relation` 端点或独立的推断方向字段。

`Relation` 的方向性继续由 `Relation.type` 的语义契约决定。

`Relation` 断言的内容相等与完整规范信息相等见 §22.9.3；该规则不得被解释为给 `Relation` 增加身份。

旧版 `Relation.weight` 继续属于派生/分析工件，不进入 Core `Relation` 的规范表示。

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

`SubjectRef.ref` 必须解析到当前 `PBDLDocument` 中恰好一个 `Subject`。

#### 17.7.2 CoreEntityRef

    CoreEntityRef {
        ref : EntityId
    }

`CoreEntityRef.ref` 必须解析到当前 `PBDLDocument` 中恰好一个 `Behavior` 或 `Preference`，并同时受全局 `Relation` 端点矩阵与具体 `Relation.type` 允许端点角色的约束。

裸 `EntityId` 字符串不得作为规范引用表示。

引用对象不得使用显示标签、数组索引、`Coding.code` 或类型标签代替 `ref`。

规范内部引用采用对象包装而不是裸字符串，以减少显示字符串歧义，并为未来版本化引用扩展保留明确结构边界；当前规范引用对象不增加 `display` 或 `type` 字段。

### 17.8 `Provenance`

`Provenance` 的最小规范字段清单：

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| `derivation` | `DerivationKind` | 1 | 必需 |
| `source` | `SourceDescriptor` | 0..1 | 可选；在特定 `derivation` 下为必需 |
| `generator` | `GeneratorDescriptor` | 0..1 | 可选；在特定 `derivation` 下为必需 |
| `evidence` | `Evidence` | 0..* | 可选集合 |
| `confidence` | `Confidence` | 0..1 | 可选 |

`Provenance` 不要求身份，也不进入文档级共享池。

`Provenance` 默认以嵌入方式附着在其所追踪的断言上：

- `Behavior.provenance : Provenance[1..*]`；
- `Preference.provenance : Provenance[1..*]`；
- `Relation.provenance : Provenance[1..*]`；
- `Annotation.provenance : Provenance[1..*]`。

#### 17.8.1 `Provenance.derivation`

`DerivationKind` 具有三种语义状态：

- DIRECT；
- INFERRED；
- UNDETERMINED。

§17 与 §13 已定义的 DIRECT / INFERRED 区分保持不变。

DIRECT 表示结构化语义内容忠实来自来源描述、记录或观测的信息。

INFERRED 表示语义内容超出来源直接表达，并由人工、模型、规则或分析过程推导产生。

UNDETERMINED 只表示：规范化器或迁移流程确实无法获得派生元数据，或无法可靠判断其类别。

UNDETERMINED 不得被解释为：

- 部分直接、部分推断；
- 使用方可以把它当作 DIRECT；
- 生成方在派生类别已知时可以跳过分类；
- 一种置信水平。

生成新的 PBDL 数据时，如果生成方拥有足够信息判定 DIRECT 或 INFERRED，就不得使用 UNDETERMINED 逃避分类。

旧版迁移在历史元数据不足、无法可靠重建派生类别时可以使用 UNDETERMINED，但不得猜测 DIRECT 或 INFERRED。

使用 UNDETERMINED 的 `Provenance` 必须保持至少一条可追踪的来源路径；通常 `source` 可以是被迁移的旧版记录或来源材料。已知的 `source`、`generator`、`Evidence` 信息必须保留，缺失元数据不得被发明。

如果连最小可追踪来源路径都不存在，规范化必须报告来源追踪要求无法满足，不得仅靠 UNDETERMINED token 伪造来源信息完整性。

UNDETERMINED 是规范有效的迁移语义，但符合规范的校验器应产生来源质量警告，以提示派生分类未能恢复。

工具或 `generator` 的存在本身不得决定 `derivation`。

`DerivationKind` 的规范词法 token 为且仅为：

-`"direct"`
-`"inferred"`
-`"undetermined"`

规范表示不得使用 `DIRECT`、`INFERRED`、`UNDETERMINED`、`unknown`、`unspecified`、`mixed` 或其他平行同义词作为序列化 token。

#### 17.8.2 `Provenance.source` 与 `generator`

`source` 表示原始信息来源及其描述。

`generator` 表示产生、抽取、转换或推导语义结果的人工、模型、规则、分析代理或过程。

条件不变量：

- 派生类别为 DIRECT 的 `Provenance` 必须具有 `source`；
- 派生类别为 INFERRED 的 `Provenance` 必须具有 `generator`；
- 派生类别为 UNDETERMINED 的 `Provenance` 必须具有 `source`；`generator` 可以存在，例如迁移或转换过程。

只有 `SourceDescriptor.kind` 不足以满足 UNDETERMINED 对可追踪来源路径的要求。

对于 `derivation = "undetermined"`，除 `source` 字段为必需字段外，还必须至少满足以下一项：

1. `source.locator` 存在；
2. `Provenance.evidence` 至少包含一个能够保留来源材料的 `Evidence` 项。

`Evidence` 项继续遵守 §17.8.5：`content` / `locator` 至少一个存在。

因此，以下结构不得视为已经满足可追踪来源路径的要求：

    {
        "derivation": "undetermined",
        "source": {
            "kind": "legacy_record"
        }
    }

该附加可追踪性要求**只适用于** `"undetermined"`；当前规范不得因此把所有派生类别为 DIRECT 的 `Provenance` 扩大为必须具有 `locator`。

一个 `Provenance` 可以同时具有 `source` 与 `generator`。

例如，LLM 从 EHR 文本忠实抽取 DIRECT 语义时，可以表示为：

- `source` = EHR 来源；
- `generator` = 抽取系统；
- `derivation` = `"direct"`。

因此，`generator` 的存在不得自动意味着派生类别为 INFERRED。

`Provenance` 不得在顶层重新引入无角色的通用 `time : TemporalValue`。

#### 17.8.3 SourceDescriptor

`SourceDescriptor` 的规范结构如下：

    SourceDescriptor {
        kind         : SourceKind
        locator?     : string
        display?     : Text
        times?       : SourceTimeEvent[0..*]
    }

`SourceDescriptor.kind` 为必需字段，并使用以下规范小写 token：

-`"patient_self_report"`
-`"questionnaire"`
-`"clinician_documentation"`
-`"ehr_record"`
-`"device_observation"`
-`"legacy_record"`
-`"other"`

`locator` 为可选的非空字符串，用于保存来源系统中的外部标识符或定位信息。它不是 PBDL Core 引用，也不加入 `EntityId` 命名空间。

`display` 是可选的人类可读来源描述。

`SourceTimeEvent` 的结构如下：

    SourceTimeEvent {
        role : "reported" | "recorded" | "observed"
        at   : TemporalValue
    }

`role` 与 `at` 都是必需字段。

`SourceDescriptor.times` 的集合顺序不得具有语义含义。

来源、报告、记录或观测相关时间必须使用显式标明 `role` 的 `SourceTimeEvent` 表示；不得重新压成一个含义歧义的通用 `Provenance` 时间。

如果某个时间只属于具体 `Evidence` 材料，而不是整个 `SourceDescriptor`，应由该 `Evidence` 项的 `times` 承载。

#### 17.8.4 GeneratorDescriptor

`GeneratorDescriptor` 的规范结构如下：

    GeneratorDescriptor {
        kind        : GeneratorKind
        identifier? : string
        version?    : string
        display?    : Text
        times?      : GeneratorTimeEvent[0..*]
    }

`GeneratorDescriptor.kind` 为必需字段，并使用以下规范小写 token：

-`"human"`
-`"llm"`
-`"rule_engine"`
-`"analytic_model"`
-`"migration_process"`
-`"other"`

`identifier`、`version`、`display` 均可选；若 `identifier` / `version` 存在，其值必须是非空字符串。

`GeneratorDescriptor` 的 `identifier` 不是 PBDL Core `EntityId`，也不建立 Participant 身份。

`GeneratorTimeEvent` 的结构如下：

    GeneratorTimeEvent {
        role : "extracted" | "generated" | "transformed" | "migrated"
        at   : TemporalValue
    }

`role` 与 `at` 都是必需字段。

`GeneratorDescriptor.times` 的集合顺序不得具有语义含义。

抽取、生成、转换或迁移相关时间必须使用显式标明 `role` 的 `GeneratorTimeEvent`。

`GeneratorDescriptor` 的存在不得自动把 `derivation` 判为 `"inferred"`。

#### 17.8.5 Evidence

`Evidence` 的规范结构如下：

    Evidence {
        kind      : EvidenceKind
        content?  : Text
        locator?  : string
        times?    : SourceTimeEvent[0..*]
    }

`Evidence.kind` 为必需字段，并使用以下规范小写 token：

-`"text_excerpt"`
-`"document_reference"`
-`"questionnaire_response"`
-`"device_observation"`
-`"legacy_material"`
-`"other"`

`content` 与 `locator` 均可选，但一个 `Evidence` 必须至少提供二者之一。

如果 `locator` 存在，其值必须是非空字符串。

`content` 用于内联人类可读的摘录或响应；`locator` 用于定位外部材料。二者可以同时存在。

`Evidence.content` 使用 §8.1 的 `Text` 契约，因此空内容或仅含空白字符的 `content` 无效。

`Evidence.times` 可以使用 `SourceTimeEvent` 保存只属于该 `Evidence` 项的报告、记录或观测时间。

如果同一个与来源相关的时间已经由更具体的 `Evidence` 项承载，规范表示不应为了方便而在没有语义区别的情况下同时复制到 `SourceDescriptor.times`。

`Evidence` 继续满足以下边界：

- 不要求身份；
- 嵌入在 `Provenance` 中；
- 不得与 `Annotation` 合并；
- 不得要求把完整 EHR 或来源文档复制进 PBDL Core。

#### 17.8.6 `Provenance.confidence`

如果 Core 的规范表示需要保留置信信息，其字段位置为可选的 `Provenance.confidence`。

`Confidence` 不得成为 `Behavior` / `Preference` / `Relation` 的内在真值字段。

`DIRECT` 的自述信息不得被迫填写 `Confidence`。

最小规范表示如下：

    Confidence {
        value  : number
        metric : string
        scale? : {
            min : number
            max : number
        }
    }

`value` 与 `metric` 都是必需字段。

`scale` 可选。

`value`、`scale.min`、`scale.max` 若存在都必须是有限数值；NaN、正无穷大和负无穷大不属于符合规范的 `Confidence`。

`metric` 必须是非空字符串，并承担“该数字衡量什么”的语义标识责任。

Core 不定义 `Confidence.metric` 的词汇；生成方不得仅因为 `value` 恰好落在 0..1 就自动解释为概率。

如果 `scale` 存在：

- `min` 与 `max` 必需；
- `min` 必须严格小于 `max`；
- `value` 必须位于闭区间 `[min,max]` 内。

`scale` 可以省略；这允许表达取值范围尚未定义，或本来就没有有界范围的模型评分或人工确定性度量。

### 17.8.6.1 `Confidence` 典型边界情况

- 校准后的概率：可以使用明确的 `metric`，例如由生成方定义的 `"probability"`，并可以声明 `scale {min:0,max:1}`；
- 未校准的模型评分：`metric` 必须说明具体评分含义；不得因为取值范围是 0..1 就自动称为概率；
- 人工标注确定性：可以使用与模型评分不同的 `metric`；
- 旧版 `confidence_score`：只有在其 `metric` 含义可以恢复或得到支持时，才可规范化为 `Confidence`；
- 评分范围未知：允许省略 `scale`，但 `metric` 仍是必需字段。

旧版 `confidence_score` 若没有可支持的 `metric` 含义，不得通过发明 `metric` 或 `scale` 被迁入规范 `Confidence`。原始旧版材料可以按实际来源通过 `Evidence` / `Annotation` 或 Core 外迁移报告保真保存。

当前规范不定义校准框架、阈值策略或统计解释。

### 17.8.6.2 `Confidence` 相等性

两个 `Confidence` 语义等价，当且仅当：

- `metric` 字符串精确相同；
- `value` 数值严格相等；
- `scale` 同时缺失，或双方 `scale.min` 与 `scale.max` 分别数值严格相等。

`Confidence` 相等性不得使用隐式浮点容差、舍入容差或统计等价。

JSON 数值的不同词法写法如果表示同一有限数学数值，可以在数值语义上相等；当前规范不要求保留 JSON 数值的词法写法作为置信信息。

### 17.9 Annotation

规范 `Annotation` 的最小字段如下：

| 字段 | 类型 | 基数 | 要求 |
|---|---|---:|---|
| `text` | `Text` | 1 | 必需 |
| `provenance` | `Provenance` | 1..* | 必需 |

`Annotation`：

- 不要求 `id`；
- 不是 `Relation` 端点；
- 不进入独立的文档级集合；
- 作为轻量嵌入结构附着于当前允许的规范断言或对象。

§17 允许：

- `Behavior.annotations`；
- `Preference.annotations`；
- `Relation.annotations`。

§17 不增加 `Subject.annotations`。

每个 `Annotation` 必须具有自己的 `provenance[1..*]`，从而区分来源承载、人工撰写与模型生成的 annotation。

当 `source` / `generator` / `derivation` 不同时，所属对象的 `provenance` 不得自动替代 `Annotation.provenance`。

`Annotation.text` 使用 §8.1 的 `Text` 约束。

`Annotation` 的内容相等与完整规范信息相等见 §22.9.2；`Annotation` 文本或 `provenance` 的差异不得改变所属实体身份。

### 17.10 嵌套限定信息的 `provenance` 继承与相等性

所属对象层级的 `provenance` 描述所属对象断言。

`BehaviorFrequency` / `BehaviorFactor` / `Context` 共用以下局部 `provenance` 字段契约；§8.3 的 `BehaviorFrequency` 与 §8.5–§8.6 的 `Context` / `BehaviorFactor` 均复用该契约：

    provenance? : Provenance[1..*]

该字段整体可选；一旦存在，集合必须至少包含一个 `Provenance`。显式空集合 `provenance: []` 不得用来表示继承。

#### 17.10.1 省略局部 `provenance`

嵌套语义限定信息可以省略局部 `provenance`，**仅当**该限定信息的来源语义与直接所属对象对它适用的完整来源集合一致。

省略局部 `provenance` 表示动态继承直接所属对象当前适用的完整来源集合。

采用规范表示的文档不得依赖不可见的历史快照来解释省略的局部 `provenance`。

因此，如果所属对象的 `provenance` 从 {P1,P2} 修改为 {P1,P2,P3}，而限定信息继续省略局部 `provenance`，则新文档中该限定信息继承的来源语义也变为 {P1,P2,P3}。

如果转换要求限定信息继续只由旧集合 {P1,P2} 支持，则所属对象增加 P3 时，该限定信息必须显式写出局部 `provenance`。

#### 17.10.2 显式局部 `provenance`

如果限定信息：

- `source` 不同；
- `generator` 不同；
- `derivation` 不同；
- 或仅由所属对象 `provenance` 的真子集支持；

则该限定信息必须携带显式局部 `provenance`。

当局部 `provenance` 存在时，它表示该限定信息的完整来源集合，并完全覆盖继承。

规范模型不得支持“继承所属对象 `provenance` + 添加局部 `provenance`”的叠加式混合合并语义。

#### 17.10.3 `Provenance` 语义相等

两个 `Provenance` 只有在以下具体维度均语义等价时，才允许视为语义等价：

1. `derivation` token 相同；
2. `source` 都缺失，或 `SourceDescriptor` 语义等价；
3. `generator` 都缺失，或 `GeneratorDescriptor` 语义等价；
4. `evidence` 集合按顺序无关比较判定为语义等价；
5. `confidence` 同时缺失，或按 §17.8.6.2 的 `Confidence` 相等性判定为语义等价。

`SourceDescriptor` / `GeneratorDescriptor` / `Evidence` 的语义相等基于其具体字段：

- 标量字段与 token 字段的值相同；
- `Text` 字段按 §8.1 的精确 Unicode 标量值序列相等；
- `TemporalValue` 字段按 §8.2.5 的规范信息相等；
- 可选字段同时缺失，或值语义等价；
- `times` 集合采用顺序无关比较，其中时间事件的 `role` 必须相同，`at` 必须按 `TemporalValue` 相等；
- `Evidence` 集合采用顺序无关比较；
- `Confidence` 按 §17.8.6.2 比较。

集合比较采用一一语义匹配；集合顺序不得产生语义差异。完整信息相等的 `Provenance`、`Evidence` 与时间事件重复项按 §22.8 进行规范化。

#### 17.10.4 规范化

限定信息省略局部 `provenance` 并继承所属对象集合 {P1...Pn}，与显式局部 `provenance` 恰为同一完整语义集合 {P1...Pn} 时，两种表示必须视为语义等价。

规范化必须省略与从直接所属对象继承得到的完整来源集合语义等价的冗余显式局部 `provenance`。

因此：

- 所属对象 {P1}，子项省略；
- 所属对象 {P1}，子项显式 {P1}；

二者语义等价，且规范形为子项省略 `provenance`。

同理，所属对象 {P1,P2}、子项显式 {P1,P2} 时，必须规范化为省略局部 `provenance`。

`Provenance` 集合顺序不得产生语义差异。

`TemporalValue`、`Text` 与 `Confidence` 的相等性已经定义，因此 `Provenance` 语义相等不再因这些叶类型未定义而受阻。

`Provenance` 的语义相等与规范化均为顺序无关；字节级确定性顺序不属于语义含义，明确留给未来的确定性序列化规范，见 §22.11。

#### 17.10.5 范围

上述继承、覆盖、相等性与规范化语义统一适用于：

- `BehaviorFrequency`；
- `BehaviorFactor`；
- `Context`；
- `TemporalExtent`。

`TemporalExtent` 的局部 `provenance` **采用同一机制**，不另建时间专用的来源信息系统。

规范模型不得用单一所属对象层级的 DIRECT / INFERRED / UNDETERMINED 标签粗暴覆盖内部 `derivation` 实际不同的嵌套限定信息，也不得把所属对象中不支持该限定信息的 `provenance` 错误继承给它。

### 17.11 具有实体身份的对象与嵌入结构

§17 保持身份边界：

- `Subject`：必需身份；
- `Behavior`：必需身份；
- `Preference`：必需身份；
- `Relation`：不要求必需身份。

以下 §17 命名结构不要求身份，不加入 `Subject` / `Behavior` / `Preference` 的文档内身份命名空间，也不是 `Relation` 端点：

- `TemporalExtent`；
- `BehaviorFrequency`；
- `Context`；
- `BehaviorFactor`；
- `Annotation`；
- `Provenance`；
- `Evidence`。

`PBDLDocument` 是规范根容器，不因本节获得实体身份语义。

### 17.12 规范字段归属取代旧版平行字段

规范模型不得同时保留以下平行机制：

| 规范字段归属 | 不得与规范字段并存的旧版平行字段 |
|---|---|
| `Behavior.type` | `Behavior.behavior_type` |
| `Preference.category` | `Preference.preference_category` |
| `Preference.value` | `Preference.preference_value` |
| `Behavior.annotations` | `Behavior.reasoning_note` |
| `Preference.annotations` | `Preference.note` |
| `Relation` | `Preference.associated_behavior` |
| `Provenance` | `Behavior.evidence_source` |
| `Provenance` | `Preference.source_type` |
| `Context` / `Behavior` / `Provenance` / 应用层，依据实际语义选择 | `Behavior.communication_status` |

旧版输入可以被迁移，但规范输出必须只使用 §17 规定的字段归属。

### 17.13 明确不属于 Core 规范表示的字段

以下旧版字段不得进入 PBDL-Core 规范对象模型：

- `Behavior.risk_tag` → 派生/应用结果；
- `Behavior.validity_flag` → 校验器/报告输出；
- `Preference.preference_conflict_flag` → 派生 `ConflictAnalysis` / 应用结果；
- `Relation.weight` → 派生/分析工件；
- 所有 Treatment Path / Pathway 字段 → 扩展/应用层。

这些字段不得为了历史兼容被重新塞回 Core 的规范表示。

### 17.14 仍待定义的能力

身份、引用、参与者、来源、生成方与证据的基础类型已经定义。

`Text`、`TemporalValue`、`TemporalExtent` 局部 `provenance`、`Coding`、`Confidence` 与相关相等性基础已经定义。

§8.3–§8.4 已定义 `BehaviorFrequency` 与 `PreferenceValue`。

§8.5–§8.6 已定义：

- `Context`；
- `ContextValue` 的 `coded` / `text` 联合类型；
- `Context` 内容相等与完整限定信息相等；
- `FactorRole`；
- `FactorDirection`；
- `FactorValue` 的 `coded` / `text` 联合类型；
- `BehaviorFactor`；
- `BehaviorFactor` 内容相等与完整限定信息相等；
- `Context`、`BehaviorFactor` 与 `Relation` 的判定边界。

主要业务复合语义类型已经定义。

以下能力仍留待后续规范定义：

- 类型兼容与转换细节；
- 规范级全局序列化顺序；
- 规范性 `Relation` 词汇与逆关系约定；
- JSON Schema 集成；
- DSL / EBNF 语法；
- 实现。

当前章节不定义这些后续能力。

## 18. 校验模型

完整校验架构尚未定义。

未来的校验模型预计至少需要区分结构合法性与语义合法性，但具体分层、严重级别模型、错误码与实现仍为 **TODO**。

已定义的最小校验后果包括：

- 旧版迁移因历史元数据确实不足而使用 `"undetermined"` 时，可以形成规范有效的 `Provenance`；
- 符合规范的校验器应对 `"undetermined"` 产生来源质量警告；
- 生成方已经掌握足够的 `derivation` 信息却仍使用 `"undetermined"`，属于语义不符合；
- 缺少 §17.8 所要求的可追踪来源路径时，`"undetermined"` 不得使来源追踪要求自动变为已满足；
- `Text` 必须满足 §8.1 的非空白内容规则；
- `TemporalValue` 必须满足 §8.2 的词法、格里高利日期与偏移量有效性；
- 当 §8.2.6 能判定 `Interval.start` 明确晚于 `Interval.end` 时，该 `Interval` 必须无效；
- `TemporalExtent` 的显式局部 `provenance` 必须满足 §17.10 的完全覆盖与禁止叠加合并规则；
- `Coding` 的必需与非空约束必须满足 §15；
- `Confidence` 必须满足有限数值、`metric` 与可选 `scale` 范围规则；
- `BehaviorFrequency` 必须满足 §8.3 的变体判别、`count` / `rate` / `period` 与重复模式集合规则；
- `BehaviorFrequency` 的定量 `precision` 必须显式为 `"exact"` 或 `"approximate"`；
- `RateFrequency` 缺少 `period` 必须无效；
- `RecurrenceFrequency` 的 `Weekday` 重复项，以及非法的 `period` / 日期计划组合都必须无效；
- `PreferenceValue` 必须满足 §8.4 的带标签联合类型判别；
- `NumericPreferenceValue.value` 必须有限，`operator` 必须为允许的 token，`unit` 若存在必须为有效 `Coding`；
- `Context` 必须满足 §8.5 的 `coded` / `text` 带标签联合类型判别；
- 完整信息相等的 `Context` 重复项不得在规范的 `context` 集合中重复保留；
- `BehaviorFactor` 的 `role` / `direction` / `factor` 变体必须满足 §8.6；
- `antecedent` 与 `reported_reason` 的 `direction` 必须为 `factor_to_behavior`；
- 由推断得到的解释性因素，如果不能与所属对象的 `provenance` 保持相同的 `derivation` / 适用来源集合，就必须显式写出局部 `provenance`；
- `BehaviorFactor` 指向已有 Core 实体的显式类型化关系必须使用 `Relation`，不得通过因素的文本或代码表示规避。

当前规范不定义校验器实现。

§22.13 将当前条件不变量分为 STRUCTURAL / REFERENCE / SEMANTIC / NORMALIZATION / VOCABULARY，以明确 JSON Schema、引用解析器、语义校验器与规范化器之间的职责边界；本节不定义校验器实现。

## 19. 扩展机制

扩展机制尚未设计。

Treatment Pathway 可以在未来作为扩展或上层应用进行设计，但当前不属于 PBDL-Core。

Core 的规范对象使用封闭字段集合。未定义或未知字段不得被静默接受为 Core 字段，也不得仅因为名称看似扩展字段就获得扩展语义。

未来扩展必须使用未来显式定义的扩展机制；任意未知 JSON property 都不是扩展机制。

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

当前具体规范类型至少包括以下命名类型与 token 族：

**根对象 / Core 对象**

- `PBDLDocument`；
- `Subject`；
- `Behavior`；
- `Preference`；
- `Relation`；
- `Annotation`。

**基础类型、词法类型与术语类型**

- `VersionToken`；
- `EntityId`；
- `Text`；
- `TemporalValue`；
- `Coding`；
- `Confidence`。

**引用与参与者**

- `SubjectRef`；
- `CoreEntityRef`；
- `ExternalActorRef`；
- `ActorRef`。

**`Provenance` 相关类型**

- `DerivationKind`；
- `SourceKind`；
- `SourceDescriptor`；
- `SourceTimeEvent`；
- `GeneratorKind`；
- `GeneratorDescriptor`；
- `GeneratorTimeEvent`；
- `EvidenceKind`；
- `Evidence`；
- `Provenance`。

**时间类型**

- `Instant`；
- `Interval`；
- `TemporalExtent`。

**频率类型**

- `QuantitativeFrequencyPrecision`；
- `FrequencyPeriod`；
- `Weekday`；
- `DayPart`；
- `QualitativeFrequencyToken`；
- `ObservedCountFrequency`；
- `RateFrequency`；
- `RecurrenceFrequency`；
- `QualitativeFrequency`；
- `BehaviorFrequency`。

**`Preference` 值类型**

- `CodedPreferenceValue`；
- `TextPreferenceValue`；
- `BooleanPreferenceValue`；
- `NumericPreferenceValue`；
- `PreferenceValue`。

**`Context` 类型**

- `CodedContextValue`；
- `TextContextValue`；
- `ContextValue`；
- `Context`。

**`BehaviorFactor` 相关类型**

- `FactorRole`；
- `FactorDirection`；
- `CodedFactorValue`；
- `TextFactorValue`；
- `FactorValue`；
- `BehaviorFactor`。

这些类型的业务字段与 token 集合继续由 §§8、15、17 规定。§22 不得通过表示规则增加新的业务字段或变体。

### 22.2 Core 规范对象闭包与未知字段

每个具体的 Core 规范对象或嵌入式结构化对象，其字段集合都是**封闭的**。

对象只允许出现该具体类型定义的字段。

未知字段、拼写错误字段、历史旧版别名或尚未定义的扩展属性不得出现在 Core 规范表示中。

例如，以下旧版字段不得与规范字段平行存在：

- `behavior_type`；
- `temporal_scope`；
- `evidence_source`；
- `communication_status`；
- `reasoning_note`；
- `risk_tag`；
- `validity_flag`；
- `preference_category`；
- `preference_value`；
- `source_type`；
- `confidence_score`；
- `associated_behavior`；
- `note`；
- `preference_conflict_flag`；
- `Relation.weight`。

未知属性不得被当作扩展。未来扩展必须使用 §19 所述的显式扩展机制。

### 22.3 缺失、`null` 与空集合

#### 22.3.1 可选标量与对象字段

Core 的规范表示使用**字段省略**表示可选字段缺失。

当前没有任何已定义的 Core 类型把 JSON `null` 作为语义值。

因此，在 Core 的规范表示中：

- 可选字段缺失 → 表示未提供该可选语义值；
- `field: null` → **无效的 Core 规范表示**。

该规则适用于 `executor`、`temporal`、`source`、`generator`、`confidence`、`locator`、`display`、`identifier`、`version`、`role`、`unit`、`window`、`day_part`、`times_per_period`、`start` / `end` 等所有可选字段。

#### 22.3.2 必需根集合

`PBDLDocument` 根集合保持 §17 的规则：

- `subjects` 必需，至少 1 项；
- `behaviors` 必需，可为空；
- `preferences` 必需，可为空；
- `relations` 必需，可为空。

必需根集合不得通过省略表示为空。

#### 22.3.3 可选集合

除必需根集合与必需 `provenance` 集合外，可选集合没有元素时，规范形必须省略该字段。

可选集合的空集合规则由该字段自身声明的基数控制：

- 基数 = `0..*` 且字段存在但为 `[]` → 可以是语义有效但需要规范化的表示；规范形必须省略该字段；
- 基数 = `1..*` 且字段存在但为 `[]` → **无效**，不得通过省略来修复基数违例。

因此，以下普通 `0..*` 可选集合显式为空时不属于规范形，但可以规范化为省略：

    annotations: []
    contexts: []
    factors: []
    frequencies: []
    evidence: []
    times: []

`days_of_week` 已由 §8.3.5 定义为存在时至少 1 项，因此：

    days_of_week: []

这是**无效**表示，不是需要规范化的表示。

局部限定信息的 `provenance` 同样是存在时 `1..*`；此外，省略还具有来源继承语义。因此，显式局部 `provenance: []` 必须视为语义无效，不得规范化为省略。

任何必需的 `provenance : Provenance[1..*]` 集合为空也同样无效。

### 22.4 带标签联合类型的机械判别

规范联合类型必须能够机械且唯一地判定变体；实现不得“猜哪个更像”。

| 联合类型 | 变体 | 必需判别字段 | 允许的变体字段 |
|---|---|---|---|
| `ActorRef` | `SubjectRef` | `ref` | 仅允许 `ref` |
| `ActorRef` | `ExternalActorRef` | `kind` = person/device/software/other | `kind, external_id?, display?, role?` |
| `TemporalExtent` | `Instant` | `kind="instant"` | `kind, at, provenance?` |
| `TemporalExtent` | `Interval` | `kind="interval"` | `kind, start?, end?, provenance?` |
| `BehaviorFrequency` | `ObservedCountFrequency` | `kind="observed_count"` | `kind,count,precision,window?,provenance?` |
| `BehaviorFrequency` | `RateFrequency` | `kind="rate"` | `kind,value,period,precision,provenance?` |
| `BehaviorFrequency` | `RecurrenceFrequency` | `kind="recurrence"` | `kind,period,precision,times_per_period?,days_of_week?,day_part?,provenance?` |
| `BehaviorFrequency` | `QualitativeFrequency` | `kind="qualitative"` | `kind,value,provenance?` |
| `PreferenceValue` | `CodedPreferenceValue` | `kind="coded"` | `kind,value` |
| `PreferenceValue` | `TextPreferenceValue` | `kind="text"` | `kind,value` |
| `PreferenceValue` | `BooleanPreferenceValue` | `kind="boolean"` | `kind,value` |
| `PreferenceValue` | `NumericPreferenceValue` | `kind="number"` | `kind,operator,value,unit?` |
| `ContextValue` | `CodedContextValue` | `kind="coded"` | `kind,value` |
| `ContextValue` | `TextContextValue` | `kind="text"` | `kind,value` |
| `FactorValue` | `CodedFactorValue` | `kind="coded"` | `kind,value` |
| `FactorValue` | `TextFactorValue` | `kind="text"` | `kind,value` |

由于 §22.2 的封闭字段规则，变体之外的冲突字段无效。

`ActorRef` 通过对象结构判别：`ref` 与 `kind` 不得共存。

其他联合类型使用必需的 `kind` token；缺失或未知的判别字段无效。

### 22.5 规范字段名规则

规范字段名只使用当前具体对象定义中规定的名称。

同一语义不得同时存在规范字段名与旧版别名。

规范化器可以在 Core 外的旧版输入层识别历史字段，但形成 Core 规范对象后必须只保留规范字段归属。

§22 不定义旧版解析器。

### 22.6 通用语义字符串一致性

`Text`、`EntityId`、`VersionToken`、`TemporalValue` 与枚举/token 字段继续使用各自的专门词法约束。

对于其他定义为非空 `string`，且承担标识符、定位信息、代码、度量名称或版本语义的字段，采用统一的**语义字符串**规则：

> `value` 必须包含至少一个不属于 Unicode `White_Space` 属性的码点。

该规则至少适用于：

- `Coding.system`；
- `Coding.code`；
- `Coding.version`（存在时）；
- `ExternalActorRef.external_id.system`；
- `ExternalActorRef.external_id.value`；
- `SourceDescriptor.locator`；
- `GeneratorDescriptor.identifier`；
- `GeneratorDescriptor.version`；
- `Evidence.locator`；
- `Confidence.metric`。

因此，只含空白字符的字符串（例如 `"   "`）不得满足这些字段的非空要求。

规范化不得自动对这些字符串执行去除首尾空白（trim）、大小写折叠（case-fold）或 Unicode 规范化。

这些语义字符串的相等性使用精确的 Unicode 标量值序列相等；如果某个专门类型已经定义更严格的词法或相等性规则，则以该专门规则为准。

### 22.7 数值一致性

规范数值语义使用数学数值，不保存 JSON 数值的词法写法。

因此，在允许 JSON 数值的字段中：

    1
    1.0
    1e0

表示相同的数学数值。

`-0` 与 `0` 在数值语义相等中相等。

§22 不得使用模糊容差、隐式舍入容差或统计等价。

各字段的具体约束保持不变：

- `FrequencyPeriod.value`：数学整数，>= 1；
- `ObservedCountFrequency.count`：数学整数，>= 0；
- `RecurrenceFrequency.times_per_period`：存在时为数学整数，>= 1；
- `RateFrequency.value`：有限数值，>= 0；
- `NumericPreferenceValue.value`：有限数值；
- `Confidence.value` / `scale.min` / `scale.max`：有限数值；
- `Confidence.scale` 存在时 `min < max` 且 `value ∈ [min,max]`。

JSON 数值的词法规范化与确定性写法属于未来的确定性序列化规范，不属于语义相等。

### 22.8 集合语义与重复项规则

当前 Core 数组或集合的顺序不得隐式表达优先级、身份、因果关系、时间顺序、排序级别或生命周期。

规范集合分为以下类别：

| 集合类别 | 示例 | 语义顺序 | 重复项规则 |
|---|---|---|---|
| 具有身份的实体集合 | `subjects` / `behaviors` / `preferences` | 无 | 重复 `EntityId` 无效；共享命名空间必须唯一 |
| `Relation` 集合 | `relations` | 无 | 完整信息相等的重复项需要规范化；`Relation` 相等性受类型方向性契约控制；仅端点相同绝不自动去重 |
| 断言来源集合 | `Behavior.provenance` / `Preference.provenance` / `Relation.provenance` / `Annotation.provenance` | 无 | 完整信息相等的重复项需要规范化 |
| `Evidence` 集合 | `Provenance.evidence` | 无 | 完整信息相等的重复项需要规范化 |
| `Annotation` 集合 | `Behavior.annotations` / `Preference.annotations` / `Relation.annotations` | 无 | 完整信息相等的重复项需要规范化 |
| 嵌套限定信息集合 | `frequencies` / `contexts` / `factors` | 无 | 完整限定信息相等的重复项需要规范化 |
| token 集合 | `RecurrenceFrequency.days_of_week` | 无 | token 重复无效 |
| 时间事件集合 | `SourceDescriptor.times` / `GeneratorDescriptor.times` / `Evidence.times` | 无 | 完整信息相等的事件重复项需要规范化 |

“需要规范化”表示语义内容可以理解，但规范形必须移除冗余的完整信息相等重复项。

如果 `provenance`、`Annotation.provenance`、`BehaviorFactor` 的 `role` / `direction`、`temporal.provenance`、`Relation.type` / `Relation.temporal` / `Relation.provenance` 等信息不同，从而导致完整规范信息不同，就不得机械去重。

`Relation` 重复项检测必须使用 §22.9.3 中感知类型契约的相等规则。对于对称或非定向关系类型，交换端点后若其余断言内容与完整信息相等，可以构成重复项；对于有向类型，端点顺序具有语义。若适用的 `Relation.type` 方向性契约不可用，规范化器不得自行猜测、交换、规范化或据此去重端点。

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
- `Interval.start` / `end` 必须分别同时缺失，或分别按 `TemporalValue` 相等规则比较；
- `provenance` 不参与内容相等。

`TemporalExtent` **完整规范信息相等**：

1. 内容相等；
2. 有效来源集合语义等价。

有效来源信息按 §17.10 在直接所属对象的语义环境中计算。

#### 22.9.2 `Annotation` 相等性

`Annotation` **内容相等**只比较 `text`，使用 §8.1 的 `Text` 相等性。

`Annotation` **完整规范信息相等**要求：

1. `text` 内容相等；
2. `Annotation.provenance` 集合语义等价。

完整信息相等的 `Annotation` 重复项需要规范化。

`Annotation` 相等性不得改变其所属实体身份。

#### 22.9.3 `Relation` 相等性

`Relation` **断言内容相等**受适用的 `Relation.type` 语义契约控制。

共同要求：

- `type` 使用 `Coding` 规范信息相等；
- `temporal` 同时缺失，或 `TemporalExtent` 内容相等。

端点相等要求：

A. 对**有向关系类型**：

- `source` 的 `CoreEntityRef` 必须与另一方的 `source` 相等；
- `target` 的 `CoreEntityRef` 必须与另一方的 `target` 相等；
- 端点顺序具有语义。

B. 对**对称/非定向关系类型**：

- `source` / `target` 端点对按无序对比较；
- 在同一对称或非定向关系类型下，A-B 与 B-A 不得仅因端点顺序不同而被判为不同的关系语义。

C. 若适用的 `Relation.type` 方向性契约不可用：

- 相等性引擎或规范化器不得自行猜测关系方向性；
- 不得自行交换或规范化端点；
- 交换端点后的相等性或去重必须等待适用的 `Relation` 词汇契约。

`Relation` **完整规范信息相等**要求：

1. `Relation` 断言内容相等；
2. `temporal` 同时缺失，或 `TemporalExtent` 完整信息相等；
3. `Relation.provenance` 集合语义等价；
4. `annotations` 集合按 `Annotation` 完整信息相等进行语义等价比较。

因此：

- 仅端点相同不得自动意味着同一个 `Relation`；
- 仅 `Annotation` 不同可以造成完整规范信息不同，但不得创建 Core 身份；
- 集合位置不得作为 `Relation` 身份；
- 完整信息相等的 `Relation` 重复项属于需要规范化的表示冗余；
- 对称关系交换端点后的相等或去重同时依赖 **VOCABULARY + SEMANTIC + NORMALIZATION**；通用结构 Schema 不得自行决定。

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

相同 `id` 不得自动表示完整规范信息相同。

`Subject` 当前只有 `id`，因此同一 `id` 的规范信息状态在当前模型中相同。

`Behavior` 规范信息相等要求 `id`、`subject`、`type`、`executor`、`temporal`、`frequencies`、`contexts`、`factors`、`provenance`、`annotations` 全部按对应的完整相等/集合相等规则判定为语义等价。

`Preference` 规范信息相等要求 `id`、`subject`、`category`、`value`、`temporal`、`contexts`、`provenance`、`annotations` 全部语义等价。

因此，当 `Behavior id=b1` 的 `temporal` / `provenance` / `annotations` 等信息发生变化时：

- 实体身份相同；
- 规范信息状态不同。

#### 22.9.7 `PBDLDocument` 相等性

`PBDLDocument` 规范信息相等要求：

1. `pbdl_version` 相等；
2. `subjects` 集合顺序无关，并可一一匹配规范信息相等的 `Subject`；
3. `behaviors` 集合按 `EntityId` 一一匹配且规范信息相等；
4. `preferences` 集合按 `EntityId` 一一匹配且规范信息相等；
5. `relations` 集合顺序无关，并可一一匹配按 §22.9.3 中适用的 `Relation.type` 语义契约判定为完整信息相等的 `Relation`；对于对称或非定向类型，交换端点不得仅因顺序不同而导致文档不相等。

根数组位置不得影响文档的语义相等。

### 22.10 规范有效、需要规范化与规范形

规范表示分为三个层次：

**语义有效表示**

满足业务、引用、来源与词法语义，但可能包含纯表示冗余。

**需要规范化的表示**

语义有效，但尚未达到规范形。例如：

- 基数 = `0..*` 的可选集合显式为 `[]`；
- 完整信息相等且无 `id` 的重复项；
- 显式局部 `provenance` 与继承得到的完整集合完全等价；
- 未来序列化器尚未统一 JSON 数值写法或数组顺序。

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
- 声明基数要求至少 1 项的集合为空（例如 `subjects: []`、`days_of_week: []`、必需/局部 `provenance: []`）；必需根集合 `behaviors` / `preferences` / `relations` 可以合法为 `[]`，但不得省略；
- 无效的联合类型判别字段；
- 重复 `EntityId`；
- 违反条件不变量。

采用规范表示的 PBDL 文档必须达到规范形。

§22 的规范形是**语义规范形**；它不承诺字节级一致的 JSON。

### 22.11 顺序与确定性序列化边界

§22 规定：

> **语义模型中的集合顺序无关；字节级确定性 JSON 序列化延后定义。**

JSON 对象成员顺序不得具有语义含义。

当前 Core 中声明为顺序无关的数组，无论输入或序列化器如何排列，只要元素集合按本节相等性规则相同，就具有相同的语义规范信息。

当前规范**不规定**：

- JSON 对象键顺序；
- 实体数组排序；
- 无 `id` 复杂对象的结构排序键；
- JSON 数值的词法写法；
- 空白与 pretty-print 规则。

未来的确定性序列化规范必须基于当前相等性与规范形规则定义字节级顺序，不得反过来改变 PBDL 语义。

因此，JSON Schema 可以在尚未定义字节级确定性 JSON 序列化规则的情况下定义。

### 22.12 跨类型 `Text` 保真回退边界

`TextPreferenceValue`、`TextContextValue`、`TextFactorValue` 都是保真回退，但每种 `Text` 回退只能承载其所属带标签类型自己的语义维度。

#### `Preference` 文本

`TextPreferenceValue` 不得暗中承载：

- 关联的 `Behavior` / `CoreEntityRef` 链接；
- `Relation` 语义；
- 当前不支持的 preference-strength 数值语义；
- 其他已经有独立规范归属的机器语义。

#### `Context` 文本

`TextContextValue` 不得暗中承载：

- `BehaviorFrequency`；
- `TemporalExtent`；
- `BehaviorFactor` 的 `reported_reason` / `antecedent` / `explanatory` 语义；
- 工作流状态；
- `Relation` 语义。

例如来源措辞：

> “在家里比较规律”

如果来源语义可以可靠分解：

- “在家里” → `Context`；
- “比较规律” → `BehaviorFrequency`；

规范化器应分别结构化。

如果某一部分无法可靠结构化，可以用 `Evidence` / `Annotation` 保留原始完整措辞；不得把跨维度的整句作为单一 `Context` 机器值。

#### `Factor` 文本

`TextFactorValue` 不得暗中承载已有 Core `Behavior` / `Preference` 身份；这类关系应使用 `Relation`。

`BehaviorFactor` 的 `role` 与 `direction` 也不得隐藏在 `factor` 文本中，从而省略必需的结构化字段。

### 22.13 规范条件不变量表

| 不变量 | 类别 |
|---|---|
| `PBDLDocument.subjects >= 1` | STRUCTURAL |
| `behaviors` / `preferences` / `relations` 根数组必需，可为空 | STRUCTURAL |
| `Subject` / `Behavior` / `Preference` 的 `EntityId` 在共享命名空间中唯一 | REFERENCE / SEMANTIC |
| `EntityId` 词法形式 | STRUCTURAL |
| `SubjectRef` 恰好解析到一个 `Subject` | REFERENCE |
| `CoreEntityRef` 恰好解析到一个 `Behavior` / `Preference` | REFERENCE |
| `ActorRef` = `ref` XOR `kind` 变体 | STRUCTURAL |
| 可选 Core 字段用省略表示缺失；禁止 `null` | STRUCTURAL |
| 可选集合基数 0..* 且存在但为空 => 规范形中省略 | NORMALIZATION |
| 可选集合基数 1..* 且存在但为空 => 无效 | STRUCTURAL / SEMANTIC |
| 局部 `provenance` 存在 => 非空 | STRUCTURAL / SEMANTIC |
| DIRECT => `source` 必需 | STRUCTURAL（条件） |
| INFERRED => `generator` 必需 | STRUCTURAL（条件） |
| UNDETERMINED => `source` 必需 | STRUCTURAL（条件） |
| UNDETERMINED => `source.locator` 或包含来源材料的 `Evidence` | STRUCTURAL + SEMANTIC |
| `Evidence` => `content` 或 `locator` | STRUCTURAL（条件） |
| `Interval` => `start` 或 `end` | STRUCTURAL（条件） |
| 可比较的 `Interval` 中 `start` 明确晚于 `end` => 无效 | SEMANTIC |
| `Confidence.scale` 存在 => `min < max` 且 `value` 位于范围内 | SEMANTIC / 数值型 |
| `FrequencyPeriod.value` 为整数且 >= 1 | STRUCTURAL |
| `ObservedCount.count` 为整数且 >= 0 | STRUCTURAL |
| `Rate.value` 有限且 >= 0，并且 `period` 必需 | STRUCTURAL |
| `Recurrence.times_per_period` 存在 => 整数且 >= 1 | STRUCTURAL |
| `days_of_week` 存在 => 非空、无重复，`period=1 week`，`times_per_period` 缺失 | STRUCTURAL + SEMANTIC |
| `NumericPreference.value` 有限且 `operator` 为允许 token | STRUCTURAL |
| 有量纲 `NumericPreference` 的来源提供 `unit` => 保留 `unit` | SEMANTIC（规范化） |
| `Context` / `Factor` / `Frequency` / `Temporal` 的局部 `provenance` 不同或仅为子集 => 显式局部 `provenance` | SEMANTIC |
| 冗余局部 `provenance` == 继承的完整集合 => 省略 | NORMALIZATION |
| `reported_reason` => `direction=factor_to_behavior` | STRUCTURAL（条件） |
| `antecedent` => `direction=factor_to_behavior` | STRUCTURAL（条件） |
| 解释性 `factor` 由模型推断且超出来源 => 有效 `derivation=inferred` | SEMANTIC |
| `BehaviorFactor` 表达已有 Core 实体关系 => `Relation` | SEMANTIC |
| `Context` 与 `Factor` 的分类遵循来源语义 | SEMANTIC |
| `Relation.type` 的 `Coding` 结构 | STRUCTURAL |
| `Relation.type` 的端点角色/方向性/因果契约 | VOCABULARY + SEMANTIC |
| `Relation` 对有向与对称端点顺序的相等规则 | VOCABULARY + SEMANTIC |
| 对称关系交换端点后的重复项移除 | VOCABULARY + SEMANTIC + NORMALIZATION |
| 完整信息相等的嵌入式/无 id 重复项 => 规范形中去重 | NORMALIZATION |
| 未知 Core 属性 | STRUCTURAL：无效 |
| `Text` 回退跨语义维度泄漏 | SEMANTIC（规范化） |

类别含义：

- **STRUCTURAL**：JSON Schema 可以直接表达全部或主要结构；
- **REFERENCE**：需要文档范围的引用解析器；
- **SEMANTIC**：需要语义校验器或规范化器读取跨字段信息或来源支持的语义；
- **NORMALIZATION**：属于规范化器职责，不应假装由 Schema 解决语义等价；
- **VOCABULARY**：依赖术语或 `Relation` 词汇契约。

### 22.14 `Relation` 词汇职责边界

`Relation.type` 已是 `Coding`，因此 JSON Schema 可以验证其 `Coding` 结构。

通用 JSON Schema 不得被要求独立决定某个关系代码的以下语义：

- 允许哪些端点角色或类型；
- 是否有向或对称；
- 逆关系约定；
- 因果语义状态；
- 交换端点后是否断言内容相等或可去重。

对称或非定向关系中的 `Relation` 相等与交换端点去重属于 **VOCABULARY + SEMANTIC + NORMALIZATION**。通用 JSON Schema 不得自行判断关系是否对称，也不得自行交换或规范化端点。

这些能力属于专门的 `Relation` 词汇、语义校验与规范化职责。

当前规范不定义具体的关系代码。

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

JSON Schema 不得尝试替代以下职责：

- 引用解析；
- 来源支持的语义判断；
- `Context` 与 `Factor` 的规范化；
- `provenance` 语义相等；
- 冗余 `provenance` / 重复项的语义规范化；
- `Relation` 词汇的端点、方向与因果校验。

### 22.16 仍待定义的表示能力

以下表示层能力仍待定义，但不阻塞结构 Schema：

- 未来的确定性字节级 JSON 序列化规范；
- 规范数组排序/对象键顺序规则；
- 通用类型转换或强制转换规则；
- 共享 `Provenance` 身份或池（若未来出现真实需要）；
- 来源链式追踪；
- 专门的 `Relation` 词汇、逆关系约定与因果状态定义；
- 扩展机制；
- DSL / EBNF 语法；
- 解析器、校验器与运行时实现；
- 规范性示例。

这些项目都有明确的职责边界；它们不得被解释为当前 Core 对象结构仍未确定。

## 附录 A：语法

当前语法占位文件位于 [`grammar/pbdl.ebnf`](grammar/pbdl.ebnf)。

当前语法有意保持不完整。

## 附录 B：校验错误码

**TODO：** 在校验语义确定后定义错误码体系。

当前不存在规范性错误码。

## 附录 C：保留关键字

**TODO：** 在词法结构与具体语法确定后定义保留关键字。

当前不存在规范性的 DSL 关键字。

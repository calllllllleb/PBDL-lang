# PBDL 设计理由

本文档用于记录 2026 年 PBDL 重新设计过程中的设计理由，属于**非规范性文档**。唯一规范性来源为 [`../spec/PBDL-v1.0-SPEC.md`](../spec/PBDL-v1.0-SPEC.md)。

2024 年原始项目形成的历史研究报告可以为设计讨论提供背景与概念来源，但它们不直接决定 PBDL v1 的语言语义。

## DR-001 — PBDL 不是 LLM 的替代品

### 决策

现代大语言模型可以负责理解非结构化文本，并从中抽取患者行为与偏好。NLP 系统、人工录入、问卷、设备数据和规则系统也可以提供候选信息。

PBDL 的职责是在这些抽取过程之后或旁路位置提供稳定的结构化语义契约。

预期架构如下：

```text
自然语言 / EHR / 问卷
        ↓
LLM / NLP / 人工录入
        ↓
候选 PBDL
        ↓
Parser / Validator
        ↓
规范化 PBDL
        ↓
应用
```

上图中的 Parser 与 Validator 只是未来架构组件，并不是 R0 阶段的实现内容。

### 理由

信息抽取技术可以独立演进，而表示层契约应保持稳定。把两者分离，可以避免 PBDL 语言本身绑定到某一种推理或抽取技术。

## DR-002 — PBDL-Core 负责描述，应用负责推理

### 决策

PBDL-Core 负责表示患者行为、偏好，以及解释这些信息所需的上下文、证据和关系信息。

以下推理与执行能力均位于 Core 之外：

- 诊断
- 推荐
- 风险预测
- 因果推断
- 知识库推理
- 治疗路径推荐
- 工作流执行

### 理由

如果把描述性陈述与推断结论混合在一起，下游消费者将无法区分哪些信息直接来自来源，哪些信息由另一个系统计算得出。

未来可以在明确标记其派生来源的前提下表示派生工件，但派生结果不得静默地变成来源直接描述的信息。

## DR-003 — 初始重新设计中 Pathway 不属于 Core

### 决策

Treatment Pathway 不属于初始重新设计中的 PBDL-Core。

它暂时保留为：

- 未来 PBDL 扩展候选，或
- 构建于 PBDL 之上的上层应用概念。

### 理由

项目的原始研究重点是患者行为与偏好的描述。在 Behavior / Preference 语言尚未稳定之前就把 Pathway 语义冻结进 Core，会过早扩张语言本体，同时模糊“描述”和“推荐 / 工作流”之间的边界。

## DR-004 — 历史研究报告不具有规范性

### 决策

历史研究报告用于保存项目历史，也可能包含值得重新讨论的概念，但它们不是开发规范。

如果历史报告与规范文件发生冲突，以规范文件为准。

### 理由

早期材料中存在定义漂移、字段冲突，以及语言本体与推理能力边界混淆的问题。如果直接将历史报告视为权威来源，这些不一致将被带入重新设计后的语言。

## DR-005 — 避免缺乏证据支持的临床语义

### 决策

PBDL 不得通过字段名称或默认语言构造暗示未经验证的因果关系、治疗效果或临床结论。

后续设计讨论中的候选关系包括：

- `related_to`
- `associated_with`
- `reported_reason_for`
- `precedes`
- `follows`
- `derived_from`

这些只是**设计候选**，并不是已经冻结的 Core 关系词表。

`causal_effect` 不被预设为 Core 的默认关系。

### 理由

描述上的接近、时间先后、关联或患者报告的原因，本身都不能证明因果关系。因果推断与因果权重需要额外证据和方法，因此不应成为默认描述语言核心的一部分。

## DR-006 — 依赖引用的 Core 实体需要显式 identity

### 决策

在 v1 Core 最小模型中：

- Subject **MUST** 具有 identity；
- Behavior **MUST** 具有 identity；
- Preference **MUST** 具有 identity；
- Relation 本身不要求 identity。

Subject 需要 identity，是因为 Behavior 与 Preference 必须稳定绑定到明确主体。

Behavior 与 Preference 需要 identity，是因为 Relation 以及历史 `associated_behavior` 兼容方向需要稳定引用具体实例。

Relation 当前不允许作为 Relation endpoint，也没有已经冻结的 Core 构造必须引用 Relation 本身，因此 R1B 不为了未来可能性提前强制 relation identity。

### 理由

只有在真实引用需求已经存在时才引入强制 identity，可以保持 Core 模型简单，同时避免使用对象位置、显示名称或类型标签充当不稳定引用。

如果未来 Provenance、扩展或其他明确用例需要引用 Relation，可以在后续设计轮次重新审议 relation identity。

## DR-007 — 类型与类别标签不是实体 identity

### 决策

Behavior type、Preference category、Relation type、显示标签和其他分类值不能自动充当 entity instance identity。

例如：

`medication_nonadherence`

如果它是一个 Behavior type，则只能回答“这是哪一类行为”，不能回答“这是哪个具体 Behavior instance”。

规范性引用必须解析到稳定 entity identity，而不能仅依赖类型名称或人类可读 label。

### 理由

同一个文档中可能存在多个同类型 Behavior 或同类别 Preference。

如果把 type/category 当作 identity，会导致引用歧义，并使对象重用、重复事件和多条同类陈述无法稳定表达。

## DR-008 — v1 默认采用 document-local identity scope

### 决策

v1 Core 最小 identity scope 为 PBDL document。

Subject、Behavior 与 Preference 共享同一个 document-local identity namespace；identifier 在所属文档内必须唯一，并在该文档生命周期中保持足够稳定以支持内部引用。

v1 Core 不强制 UUID、URI 或其他全球唯一标识符。

数组位置或列表序号不能作为规范性 identity。

跨文档 identity 与 reference protocol 保留为未来工作。

### 理由

当前真实需求是保证一个 PBDL document 内的 Subject 归属与 Behavior / Preference / Relation 引用可以确定解析。

直接要求全球 UUID、URI 或跨文档解析协议会提前引入尚无必要的命名、持久化和互操作复杂度。

document-local scope 已足以满足当前 Core 引用需求，同时不妨碍未来增加 external/global identifier binding。

## DR-009 — PBDL 记录有来源的信息，而不是认证真相

### 决策

PBDL 表示 Behavior / Preference 的结构化语义以及这些语义从哪里产生。

PBDL-Core **MUST NOT** 因某条信息进入 PBDL 就将其视为已经得到现实世界真值认证。

患者自述、临床记录、设备观测和外部推断可以表达不同甚至互相冲突的信息；PBDL 的职责是保留这些来源与语义差异，而不是自动决定哪个来源“正确”。

### 理由

将“来源直接描述的信息”误称为“事实”会让表示层承担并不存在的真实性担保。

来源追踪使下游能够判断信息由谁报告、记录、观测或推断，但真实性评估、证据权重与冲突裁决需要额外的方法和应用上下文，不属于 PBDL-Core。

## DR-010 — Direct 与 inferred information 必须保持可区分

### 决策

PBDL canonical semantics 必须至少能够区分两类来源语义：

- DIRECT：直接来自报告、记录或观测；
- INFERRED：由 LLM、ML model、rule engine、analytic process 或其他 inference process 根据输入推断产生。

DIRECT 不代表“绝对真实”。

INFERRED **MUST NOT** 静默伪装成 DIRECT information。

该区分必须由结构化 provenance semantics 表达，不能只靠自由文本 note 推测。

DIRECT / INFERRED 判断依据的是结构化 semantic content 相对于来源内容是否经过推导，而不是处理链路中是否出现 LLM、NLP 或其他工具。使用这些工具做 extraction、parsing、normalization、terminology mapping 或 serialization transformation，本身不能自动把信息归为 INFERRED；如果结构化语义忠实表达来源已经明确报告、记录或观测到的内容，即使由 LLM / NLP 抽取，也仍可属于 DIRECT。只有当 semantic content 超出来源直接表达、记录或观测的内容并经推导产生时，才属于 INFERRED。

### 理由

同一个 Preference category / value 或 Behavior semantic content 可能既来自患者直接表达，也可能来自模型推断。

如果丢失产生方式，下游无法判断信息的语义来源，也容易把模型输出误认为患者陈述。

## DR-011 — Behavior 与 Preference 必须具有实际来源追踪

### 决策

每个 canonical Behavior 和 Preference 都必须实际至少关联一条 provenance linkage。

“语言具有表达 provenance 的能力，但某个实例可以完全没有来源”不满足 v1 Core 的最小来源追踪要求。

同一个语义实例可以有多个 provenance records，但来源数量本身不构成真值权重。

如果来源表达的 semantic content 实质不同或冲突，规范化表示不得通过 provenance 合并、对象折叠或其他方式丢失、掩盖或使冲突语义不可区分。默认应优先保持为不同 Behavior / Preference instances；未来若采用其他表示方式，也必须保留冲突语义之间的可区分性。

Provenance 与 Evidence 是相关但不同的概念：

- Provenance 回答信息如何产生、从哪里来；
- Evidence 回答哪些材料支持或承载该信息。

R1C 暂不强制 Provenance 自身具有独立 identity。

### 理由

强制实例级来源追踪关闭了 R0 中“可追踪”究竟是语言能力还是实例要求的歧义，并使 DIRECT / INFERRED 区分具有可实现基础。

同时，不提前强制 Provenance identity 可以避免在没有共享 provenance、provenance chaining 或稳定反向引用需求时过度设计对象模型。

## DR-012 — Semantic time 与 Provenance time 必须分离

### 决策

PBDL-Core 将对象本身的时间语义与来源过程的时间语义明确区分：

- Semantic time：Behavior 发生、持续或适用的时间；Preference 适用的时间；Relation 成立或适用的时间。
- Provenance time：信息被报告、记录、观测、抽取或生成的时间。

两者不能互相自动替代。

例如，患者在 9 月 20 日说“上周漏服了三次药”时，“上周”是 Behavior semantic time，而“9 月 20 日”是 reporting / provenance time。

### 理由

记录时间经常晚于、早于或仅部分覆盖被描述事件的真实时间范围。若把记录时间直接当作 semantic time，会改变来源原本表达的时间含义，并制造错误的临床或行为时间线。

## DR-013 — 缺少时间信息不意味着永久成立

### 决策

Behavior、Preference 与 Relation 可以没有 semantic temporal information。

缺少时间只表示 PBDL 当前没有提供该项 semantic time，不自动表示：

- 永久成立；
- 当前仍成立；
- 从出生至今；
- 始终如此；
- 反复发生；
- 时间无关。

Preference 尤其不能因为没有时间信息就被解释为永久偏好。

同样，Interval 只有一个已知边界时，另一个 boundary 的缺失只表示 unspecified / not provided，不自动表示 ongoing、永久延续、从无限过去开始或数学意义上的 unbounded interval。显式 ongoing / unbounded semantics 留待后续 temporal design。

### 理由

“未记录时间”与“永久有效”是完全不同的语义。把二者混为一谈会给下游系统制造不存在的持续性信息，也会妨碍多个时期的不同 Preference 或 Behavior 陈述并存。

## DR-014 — Canonicalization 不得发明时间精度

### 决策

规范化转换必须保留来源实际支持的 temporal precision，不得仅为了满足某个固定格式而补造更高精度。

例如：

- “2026-09”不能自动变成“2026-09-01T00:00:00”；
- “2026 年”不能自动变成某个具体日期；
- 来源未提供 timezone / offset 时，不能凭空补充；
- relative time 若保留在 canonical semantics 中，必须具有明确 anchor。

R2B2 已冻结 TemporalValue partial-date / date-time lexical profiles；relative-time syntax 继续留待上游解析 / future DSL work。

### 理由

伪造精度会把格式便利误当成来源知识，并可能让下游误以为一个人为补全的日期、时刻或时区是真实观测值。R1D 因此只冻结信息保真原则，不提前冻结具体序列化。

## DR-015 — Trigger terminology 不建立因果关系

### 决策

历史 `behavior_trigger` 与 `symptom_triggered` 的表达能力继续保留，但 `trigger` / `triggered` 这些名称本身不构成因果证据，也不自动表示 verified causal relation。

PBDL 需要区分至少四件不同的事情：

1. 来源明确说“因为 X，所以 Y”；
2. 记录只显示 X 与 Y 共现或 X 先于 Y；
3. 模型 / 规则 / 分析过程推断“可能因为 X，所以 Y”；
4. 独立方法已经建立 X 对 Y 的真实因果效应。

R1E 只冻结前 3 类信息在 PBDL 中不得被压缩成第 4 类因果真值。

同样，`symptom_triggered` 不能依靠字段名自行决定 symptom → behavior 或 behavior → symptom 的方向。

### 理由

旧字段承载的业务能力仍然有价值，但“trigger”在自然语言中常同时混合 reason、association、antecedence 与 causality。

如果把 legacy 字段名直接冻结成因果语义，会使患者陈述、记录时序、模型推断和真实因果证据失去可区分性，并违反 PBDL-Core“描述而非因果推断”的既有边界。

## DR-016 — Source-attributed reason 与 inferred explanation 必须可区分

### 决策

当患者、临床记录、问卷或访谈等来源明确表达“因为 X，所以 Y”时，PBDL 可以保留“该来源把 X 归因为 / 描述为 Y 的原因”这一 source attribution。

这并不表示 PBDL 独立认证 X caused Y。

当来源未表达原因，而模型、规则或分析过程根据其他信息生成解释时，该解释属于 INFERRED semantics，并不得伪装为 DIRECT reported / source-attributed reason。

如果 LLM / NLP 只忠实抽取来源已经明确表达的原因，而没有新增解释语义，该结果仍可以是 DIRECT；这延续 R1C 中“工具参与 extraction 不等于 automatic inference”的规则。

Temporal precedence 与 co-occurrence 同样不能自动升级成 reported reason 或 causality。

### 理由

“患者说因为 X”、“记录显示 X 先出现”、“模型猜测因为 X”以及“方法学上证明 X 导致 Y”具有不同证据层级和 provenance。

将它们统一压成一个 `trigger` 会破坏来源语义、推断边界与因果边界，因此 R1E 保留 legacy 能力，但要求 canonical semantics 保持这些情况可区分。

## DR-017 — Context 限定语义，而不是 catch-all container

### 决策

Context 的最小职责是对 Behavior / Preference 的语义解释提供情境性限定。

Context 不承担已经由其他层明确负责的职责：

- Provenance 负责信息从哪里来、如何产生；
- temporal semantics 负责信息描述对象何时发生或适用；
- trigger / reason semantics 负责 source-attributed reason、association 与 inferred explanation 的边界；
- derived / application layer 负责 risk、recommendation、conflict、score 与 causal inference；
- workflow / application layer 负责 review、assignment、escalation、notification、closure 等流程状态。

Context 本身不建立 causality，也不因某因素影响行为就自动把该因素定义成 objective Constraint / Barrier。

Behavior / Preference 可以没有显式 Context；缺少 Context 不表示 unconditional 或 universally applicable。

R1F 暂不要求 Context 具有独立 identity，也不把 Context 加入 Relation endpoint matrix。

### 理由

如果 Context 被设计成“所有暂时不知道放哪里的信息”的容器，Provenance、时间、原因、分析结果和软件工作流状态就会再次混回同一对象，破坏 R1B–R1E 已经建立的语义边界。

最小而排他的 Context 职责可以保留真实情境信息，同时避免 Context 演化成无法验证、无法解释的万能属性袋。

## DR-018 — Communication behavior、communication context、Provenance 与 workflow state 必须分离

### 决策

历史 `Behavior.communication_status` 的业务能力继续保留，但该单一字段可能混合至少四类不同语义：

1. Subject / actor 实际实施或没有实施的 communication Behavior；
2. 对另一个 Behavior / Preference 的 contextual communication qualification；
3. 谁报告、记录、抽取或生成信息的 Provenance；
4. review、acknowledgment、assignment、escalation、notification 等 workflow / application state。

Canonical semantics 必须保持这些类别可区分，不能仅因为历史上共用一个 `communication_status` 字段就继续压成一个通用状态。

“患者告诉医生 X”与“医生把 X 记录进 EHR”不是同一语义；“communicated / acknowledged”也不表示内容已经 verified、agreed 或 true。

### 理由

如果不拆分这四类语义，未来 Schema 会重新把患者行为、语义上下文、来源追踪和软件工作流混在一起。

这不仅会削弱 PBDL-Core 的描述边界，也会让下游系统无法判断一个状态究竟描述患者做了什么、信息怎么进入系统、某项语义如何被沟通，还是后台流程已经走到哪一步。

## DR-019 — Frequency / recurrence 与 temporal extent 是不同维度

### 决策

R1D semantic temporal extent 与 R1G Behavior frequency / recurrence 必须保持独立。

Temporal extent 回答“Behavior 在什么时候发生、持续或适用”；frequency / recurrence 回答“某类 Behavior occurrence 以什么重复模式或频度发生”。

因此：

- “持续三个月”描述 temporal duration / extent；
- “每三个月一次”描述 recurrence pattern；
- “2026 年 1 月至 3 月，每天晨起测血压”可以同时具有 temporal extent 与 recurring pattern。

两者不能共享一个模糊 temporal 字段，也不能互相替代。

### 理由

Duration、applicability window 与 repetition pattern 对下游系统具有完全不同的解释。

如果把“持续三个月”与“每三个月一次”压成同一类值，规范化过程会失去来源真正表达的是持续性还是重复性，并容易制造并不存在的 occurrence 或 schedule。

## DR-020 — Observed counts、recurring patterns、qualitative frequency 与 expected schedules 必须可区分

### 决策

以下四类语义必须保持可区分：

1. “过去一周发生 3 次”——observed / reported count within a reference window；
2. “通常每周发生 3 次”——recurring / summarized pattern；
3. “经常发生”——qualitative frequency；
4. “计划 / 处方要求每周发生 3 次”——expected / prescribed schedule。

它们不能为了统一表示而全部归一化成 `frequency = 3/week`。

同样，多个具体 occurrence 不能自动证明 pattern；pattern 也不能自动生成 concrete observed events。

如果 pattern 是模型或分析过程从 occurrence records 推断出来的，它必须保留 INFERRED provenance semantics。来源明确表达 frequency，而 LLM / NLP 只忠实抽取时，则仍可以是 DIRECT。

### 理由

这四类信息的证据基础、时间含义和行为学解释不同。

把 observed count 当成 recurrence 会把历史窗口错误外推到未来；把 qualitative frequency 强制数值化会伪造精度；把 expected schedule 当成 actual Behavior 会把治疗计划误写成患者实际行为；而把多个 observed events 自动总结成 pattern 会把 derived inference 伪装成 source-described information。

R1G 因此冻结语义区分，而不设计 RRULE、cron、regimen、adherence scoring 或完整 scheduling language。

## DR-021 — Canonical Preference–Behavior association 使用单一 Relation mechanism

### 决策

历史 `Preference.associated_behavior` 的表达能力继续作为 legacy compatibility input 保留，但 canonical PBDL semantics 不再维护 dedicated `associated_behavior` link 与 generic Relation 两套平行机制。

Legacy `associated_behavior` 必须解析到唯一 Behavior identity，并 canonicalize 为 explicit Preference–Behavior Relation。

Legacy field 本身不自动决定 causal、directional、conflict 或 explanatory semantics；canonicalization 只能保留来源实际支持的 relation meaning。

### 理由

如果 canonical Preference 同时保留 dedicated `associated_behavior` reference 和 `Relation(Preference, Behavior, type)`，同一语义会有两个互相竞争的表达入口，造成校验、去重、provenance 与后续 vocabulary 绑定的不一致。

统一到 Relation 后，Preference–Behavior association 使用与其他合法 Core entity link 相同的语义合同，同时仍保留 legacy input 的迁移能力。

## DR-022 — Relation type 定义语义与方向；endpoint order 本身不建立因果

### 决策

Relation type 是 Relation 的机器语义核心。

每个 type 必须具有稳定定义，并说明 endpoint semantic roles、allowed endpoint kinds、directionality semantics 与 causal semantic status。

Specific relation type 可以把 R1B global endpoint matrix 进一步缩小到更严格的 endpoint combinations，但不能扩大 R1B 已允许的 endpoint matrix。

Directional type 中 endpoint 交换会改变或破坏语义；symmetric / non-directional type 中 endpoint 交换不能被解释为另一种 semantic relation meaning。

Source → target 的箭头本身不表示 cause、precedes、influence、priority 或 importance。

Directional 也不等于 causal；如果 type definition 没有明确赋予 causal semantics，consumer 不能根据名称、方向性或 endpoint order 猜测 causality。

### 理由

如果 endpoint order 自带隐式语义，下游系统会在没有 relation type 定义的情况下自行猜测“箭头是什么意思”，从而把 directionality、causality、temporal ordering 与 importance 混为一谈。

把语义放在 relation type contract 中，才能使 Relation 机器可解释且可验证，同时避免把 Preference → Behavior 误读成 Preference caused Behavior。

## DR-023 — Relation assertion 需要自己的 Provenance；derived weight 不属于 Core relation truth

### 决策

每个 canonical Relation assertion 必须具有可追踪 Provenance。

Endpoint provenance 不能自动充当 Relation provenance，因为“两个 endpoint 分别存在”与“两个 endpoint 之间存在某种关系”是不同 assertion。

因此，即使 Behavior 与 Preference endpoints 都是 DIRECT，模型根据它们推断出的 Relation 仍然是 INFERRED。

同时，历史 `Relation.weight` 继续保持 MOVE_DERIVED，不作为 Core Relation intrinsic truth / strength。外部分析产生的 score、statistic、correlation、association strength 或 effect estimate 属于 derived / analytic artifact。

### 理由

Relation assertion 可以来自不同于 endpoint 的信息来源或推理过程。如果直接继承 endpoint provenance，会把模型推断的关系伪装成来源明确陈述的关系。

同理，一个无语义约束的 numeric `weight` 无法同时代表 correlation、confidence、ranking score、association strength 与 causal effect。把它重新放入 Core 会再次混淆 source-described semantics 与 derived analysis。

## DR-024 — Annotation 是 human-readable adjunct，不是 machine-semantics backdoor

### 决策

Annotation 的最小职责是为已有 canonical semantic object / assertion 提供人类可读的补充说明、澄清或解释性文本。

如果信息已经具有结构化 canonical semantic mechanism，Annotation 可以补充解释，但不能取代该机制。下游实现不应必须“读懂 note”才能恢复 identity、reference、type、time、frequency、Context、Relation、Provenance、DIRECT / INFERRED 或 causal-status 等机器语义。

Annotation 也不是第二个 Context 式 catch-all container：不能把尚未设计字段的所有语义永久塞进自由文本，并依赖下游 NLP 恢复规范性含义。

Annotation 不获得 required identity，也不成为 Relation endpoint。

### 理由

自由文本是重要的信息保真工具，但如果允许 note 成为唯一机器语义载体，R1B–R1H 已冻结的结构化边界都会被绕过。

这会让实现重新依赖自然语言推断来决定本应结构化的语义，同时造成 schema validation、reference resolution、provenance tracking 和 interoperability 无法可靠执行。

## DR-025 — `reasoning_note` 与 `note` 统一语义所有权，但 derivation 必须可区分

### 决策

历史 `Behavior.reasoning_note` 与 `Preference.note` 的人类可读说明能力统一收敛到 Annotation semantics。

但以下三类内容必须保持 provenance / derivation 可区分：

1. 来源自己已经写出的说明；
2. 人工标注者或审阅者新增的解释；
3. model / analytic process 新增的解释。

是否使用 LLM 本身不决定 DIRECT / INFERRED；真正标准仍然是 semantic content 相对于 source 是否新增了推导。

因此，LLM 对来源已有说明进行忠实抽取、改写或规范化时仍可以是 DIRECT / source-faithful；模型新增来源未表达的解释时，该新增内容属于 INFERRED。

PBDL-Core 不要求保存 hidden chain-of-thought、private reasoning trace 或 token-level internal deliberation。需要解释时，可以保存 concise explanation、rationale summary 或 result-oriented annotation，并保留其 source / generator / derivation distinction。

### 理由

`reasoning_note` 这个历史名称容易让实现误以为 PBDL-Core 自己承担推理、或者需要保存模型内部推理过程；`note` 又容易成为没有边界的自由文本容器。

统一为 Annotation semantics 可以保留两者的历史价值，同时通过 provenance / derivation 与 structured-semantics boundary 防止其成为事实、推理或机器语义的后门。

## R1 Closure Note — non-normative

R1A–R1I 已完成 PBDL-Core semantic foundation 的主要边界冻结。

R1 semantic foundation is closed; concrete representation remains future work.

下一阶段 R2 — Canonical Model & Schema 将在后续独立设计轮次中，把已经冻结的语义映射到 concrete canonical object structure、fields、cardinalities、JSON Schema 与 validation invariants。

本轮不设计或启动 R2，也不表示 PBDL 1.0 已完成。

## DR-026 — Canonical model separates identity-bearing entities from embedded semantic qualifiers

### 决策

R2A 保持 Subject、Behavior、Preference 为 document-local identity-bearing entities。

Relation 继续不要求 identity，因为当前没有 Core reference 需要稳定指向 Relation，Relation 也不是 Relation endpoint。

TemporalExtent、BehaviorFrequency、Context、BehaviorFactor、Annotation、Provenance 与 Evidence 均作为 embedded / attached semantic structures，不加入 entity identity namespace，也不成为 Relation endpoint。

### 理由

Identity 应由真实稳定引用需求驱动，而不是由“对象有结构”驱动。

将所有 nested qualifier 都升级为 graph entity 会增加引用、生命周期、去重与 identity 管理复杂度，却没有 R1 已冻结的使用场景支持。

R2A 因此把 identity-bearing graph entities 与 embedded semantic qualifiers 明确分层。

## DR-027 — Provenance attaches to assertions, with local provenance for independently derived qualifiers

### 决策

Behavior、Preference、Relation 与 Annotation 都具有明确 provenance attachment。

Owner assertion 的 Provenance 不能粗暴覆盖 independently derived nested qualifier，也不能在 owner 具有多条 provenance 时，把与 qualifier 无关的 provenance 一并继承给 qualifier。

例如：

- Behavior：patient missed medication → DIRECT；
- BehaviorFrequency：usually daily → model inferred → INFERRED。

Canonical model 必须允许 frequency qualifier 保留 local INFERRED provenance，而不是因为 owner Behavior 为 DIRECT 就把 frequency 也错误标成 DIRECT。

同样，如果 Behavior provenance 包含 P1 patient report 与 P2 device record，而 frequency 只有 P1 支持，则 frequency 必须具有 local provenance；省略 local provenance 不能被解释为 P1 与 P2 都支持该 frequency。

因此，nested qualifier 只有在其 provenance semantics 与 owner 对该 qualifier 的完整 applicable provenance set 一致时，才可以省略 local provenance并继承 owner provenance。

同样原则适用于 BehaviorFactor、Context 与 TemporalExtent；R2B2 已确认 TemporalExtent 必须具有同样的 optional local provenance capacity。

### 理由

R1C 已冻结 semantic derivation relative to source 才决定 DIRECT / INFERRED。

如果 canonical model 只允许整个 Behavior 一个 provenance，就会在 qualifier 由不同 source / generator 推导时丢失这一边界。

局部 provenance capacity 因此是 semantic fidelity requirement，而不是实现便利。

## DR-028 — Canonical field ownership replaces legacy parallel fields

### 决策

Legacy fields 可以继续作为 migration input，但 canonical model 只保留一套权威 ownership。

例如：

- behavior_type → Behavior.type；
- reasoning_note / note → annotations；
- associated_behavior → Relation；
- evidence_source / source_type → Provenance；
- communication_status → 根据实际语义分流到 Behavior / Context / Provenance / workflow layer。

Canonical output 不得同时保留 legacy field 与新 canonical mechanism。

### 理由

平行 canonical fields 会制造两个 source of truth，使 validator、round-trip、provenance、reference 与 downstream interoperability 无法判断哪一个字段具有权威语义。

R2A 因而在 representation 层正式结束 legacy duplication；兼容性通过 migration mapping 保留，而不是通过 canonical duplication 保留。

## DR-029 — Relation remains non-identity-bearing after lifecycle stress test

### 决策

R2B0 对同 endpoint 多 type、多 temporal、多 provenance、跨版本 annotation / temporal 修改、derived artifact targeting、audit log 与 diff matching 进行了 stress test。

结论：**KEEP — Relation 继续不要求 document-local identity。**

Core Relation 表达当前文档中的 semantic assertion，不承诺跨文档版本的 stable lifecycle handle。

Type、temporal applicability 或 provenance semantics 不同的 Relation 可以依 canonical semantic content 保持区分。仅 annotation 改变不产生新的 Core identity；temporal / type / provenance semantic content 改变可以表示不同 assertion。

需要跨版本稳定 handle、audit lifecycle 或 Core 外 derived artifact 稳定定位的场景属于 application / extension responsibility，不足以证明 Core 必须增加 Relation.id。

### 理由

给 Relation 增加 id 会扩张 R1B identity model、reference namespace 与 JSON Schema，但当前 Core 没有实体需要通过 Core reference 指向 Relation。

A6/A7 所需要的是 application lifecycle / artifact targeting，而不是 Core graph endpoint identity。

因此保持 no-id model 更简单，也符合“identity 由真实 Core reference need 驱动”的原则。

## DR-030 — Nested provenance inheritance uses complete override and canonical omission

### 决策

Nested qualifier provenance 采用：

- local provenance absent → inherit complete current applicable owner provenance set；
- local provenance present → complete override；
- no additive merge。

Inheritance 是当前 canonical document 的 structural dynamic semantics，不是隐藏的 snapshot history。

显式 local set 与 inherited complete set semantic-equivalent 时，canonical form 必须省略 redundant local provenance。

Provenance collection ordering 不改变 semantic equality。

### 理由

如果 omitted provenance 采用不可见 snapshot semantics，serialized document 将无法自解释。

如果允许 additive inheritance，consumer 无法仅从 local field 判断 complete provenance set，也会让 hashing、dedup、diff 与 round-trip 产生多种等价表示。

Complete override + redundant omission 提供单一、可自解释的 canonical direction。

## DR-031 — UNDETERMINED derivation preserves legacy uncertainty without weakening DIRECT / INFERRED

### 决策

DerivationKind 增加受限语义状态 UNDETERMINED。

它只用于 derivation metadata 真实不可用或无法可靠重建的 migration / canonicalization 情况，不表示 mixed derivation，也不是 producer 的通用逃生口。

如果 producer 已能判断 DIRECT / INFERRED，则不得使用 UNDETERMINED。

UNDETERMINED 必须保留至少一条 traceable source path；仅有 SourceDescriptor.kind 不足以满足该要求。R2B1 将其操作化为：source.locator 存在，或 Provenance.evidence 至少包含一个保留 source material 的 Evidence item。validator 应产生 provenance-quality warning。

### 理由

强迫历史记录在证据不足时二选一 DIRECT / INFERRED 会制造虚假的确定性。

反过来，让所有 producer 任意选择 unknown 又会削弱 R1C boundary。

受限的 UNDETERMINED 允许诚实迁移 legacy uncertainty，同时保持 native documents 的分类责任。

R2B1 将其唯一 canonical lexical token 冻结为 `"undetermined"`，与 `"direct"`、`"inferred"` 共同构成唯一 DerivationKind token set。

## DR-032 — ActorRef is SubjectRef or embedded ExternalActorRef

### 决策

ActorRef architecture 冻结为：

    SubjectRef | ExternalActorRef

当前 Subject 本人作为 executor 时使用 SubjectRef。

Caregiver、clinician、device、external software / system 等非 Core Subject actor 使用 non-identity-bearing embedded ExternalActorRef。

R2B1 concrete representation 使用 REQUIRED kind，并允许 optional external_id / display / role。

external_id 使用 system + value 明确区分外部稳定 identity 与 human-readable display / role；SubjectRef 与 ExternalActorRef 通过 `ref` vs `kind` structural discrimination 保持 JSON shape 无歧义。

不新增 Actor / Participant Core entity。

### 理由

Stress cases 显示 executor 需要覆盖人、设备与软件系统，但没有 Core requirement 需要其他对象通过 PBDL Core reference 指向这些 actor。

Embedded external descriptor 足以表达当前语义需求。

当稳定 external id 存在时，可以重复表达同一 external actor；只有 role / display 时则不能假装具有稳定 instance identity。

## DR-033 — References use explicit ref objects and constrained document-local EntityId

### 决策

VersionToken 使用 constrained string；当前 PBDL 1.0 canonical token 精确为 `"1.0"`。

EntityId 使用简单、case-sensitive ASCII lexical profile：

    [A-Za-z_][A-Za-z0-9._-]*

SubjectRef 与 CoreEntityRef 统一使用：

    { "ref": EntityId }

而不是 bare string。

### 理由

Bare string reference 容易与 display text、code 或普通 string value 混淆。

显式 `ref` object 保持 parser / validator 简单，同时为 future versioned reference extension 提供结构边界，而不会引入 URI / global identity 负担。

EntityId 继续只承担 document-local instance identity，不需要 UUID。

## DR-034 — Source, generator, and evidence use minimal role-explicit concrete descriptors

### 决策

SourceDescriptor、GeneratorDescriptor 与 Evidence 在 R2B1 获得最小 concrete structure。

Source-related time 使用 `SourceTimeEvent(role, at)`，其中 role 明确为 reported / recorded / observed。

Generator-related time 使用 `GeneratorTimeEvent(role, at)`，其中 role 明确为 extracted / generated / transformed / migrated。

Evidence 同时允许 inline content 与 external locator，至少存在其中之一；Evidence 可以承载只属于该 evidence item 的 SourceTimeEvent。

### 理由

这些结构足以覆盖 patient self-report、questionnaire、clinician documentation、EHR record、device observation、legacy migration、human annotator、LLM extractor、rule engine 与 analytic model，而不需要完整 FHIR resource、ML registry 或 provenance event ontology。

Role-explicit time 保持 R2A final repair：不得重新引入 ambiguous top-level `Provenance.time`。

## DR-035 — Provenance equality is semantic and order-insensitive; sorting remains serialization work

### 决策

Provenance equality 基于已经 concretize 的 fields，而不是 collection position 或 serialization order。

Provenance collections、Evidence collections 与 role-explicit time-event collections 的 ordering 不产生 semantic meaning。

Nested local provenance 与 inherited owner set semantic-equivalent 时，canonical form 必须省略 redundant local provenance。

R2B2 已冻结 TemporalValue、Text 与 Confidence equality，因此 provenance semantic equality 已具备完整 leaf comparison foundation；deterministic global sorting key 仍留 final serialization round。

### 理由

Equality 必须先于 Schema / serialization freeze 明确，否则 provenance inheritance 无法判断 redundant local set。

但在 leaf lexical representation 尚不完整时强行冻结 sort key，会把后续 TemporalValue / Text / Confidence 设计反向绑死。

因此本轮冻结 order-insensitive semantic equality，sorting 延后到 final serialization round。

## DR-036 — Text preserves Unicode content without normalization side effects

### 决策

Canonical Text 是 JSON-compatible Unicode string，并且至少包含一个 Unicode White_Space 之外的 code point。

Text equality 使用 exact Unicode scalar-value sequence equality。

Core 不自动 trim、case-fold 或 Unicode-normalize。

### 理由

Evidence.content 与 Annotation.text 需要阻止 empty / whitespace-only value 伪造“存在内容”，同时又必须保留原始人类文本。

自动 normalization 会修改来源文本并让 canonical equality 隐含 producer-dependent behavior，因此不在 Core 中执行。

## DR-037 — TemporalValue encodes source precision and timezone information lexically

### 决策

TemporalValue 使用 constrained canonical string，分别支持 year、month、date、minute、second 与 fractional-second precision。

Date-time 可以无 timezone、带 numeric offset、带 bracketed source zone token，或同时保留 offset + zone token。

Canonical temporal equality 是 canonical information equality：要求完整 lexical form 相同，而不是只比较 physical instant。

### 理由

把所有值强制提升为 full timestamp 或 UTC instant 会发明缺失日期精度 / timezone，或丢失 source offset / zone information。

例如 `10:00Z` 与 `18:00+08:00` 可能是同一 physical instant，但它们保存的 source-local representation 不同。

需要 physical-instant comparison 的实现可以提供单独 operation，但不能替代 canonical equality。

## DR-038 — TemporalExtent receives local provenance

### 决策

TemporalExtent 增加 optional：

    provenance? : Provenance[1..*]

并完全复用 nested qualifier 的 complete-current-set inheritance、complete override、no additive merge 与 redundant omission rules。

### 理由

Owner assertion 与 temporal qualifier 可以来自不同 source 或 derivation。

Behavior 本身 DIRECT 但 temporal 是模型推断、Preference 的 temporal 只由 owner provenance 子集支持、Relation temporal applicability 为 INFERRED 等场景，仅靠 owner provenance 无法无损表达。

因此 TemporalExtent local provenance 是 semantic fidelity requirement，不是第二套 temporal provenance system。

## DR-039 — Coding separates basic machine identity from canonical information equality

### 决策

Coding concrete shape 使用 required system + code，optional display + version。

Basic machine semantic identity 继续由 system + code 决定。

Canonical information equality 还要求 version presence/value 与 display presence/value 相同。

### 理由

display 只是人类可读文本，不应改变 terminology code identity。

version 虽不推翻 R0 的 code + system basic identity，但属于被保留的 canonical information；不同版本不能在 normalization / dedup 时静默视为完全相同 representation。

## DR-040 — Confidence is metric-aware finite numeric metadata, not implicit probability

### 决策

Confidence 使用：

    value + metric + optional scale(min,max)

metric REQUIRED。

value / scale boundaries 必须 finite；scale 存在时 min < max 且 value 位于 inclusive range。

scale 可以省略。

Confidence equality 要求 metric、value、scale 精确语义相等，不使用 float tolerance。

### 理由

Calibrated probability、uncalibrated model score、human certainty 与 legacy confidence_score 不是同一 metric。

仅根据数字落在 0..1 就把任意 score 解释为 probability 会制造不存在的语义。

要求 metric 而允许 scale 省略，可以同时覆盖已知 bounded scale 与 range 未知的 score，而不引入完整 calibration framework。

## DR-041 — BehaviorFrequency uses four discriminated semantic variants

### 决策

BehaviorFrequency 冻结为：

    ObservedCountFrequency
    | RateFrequency
    | RecurrenceFrequency
    | QualitativeFrequency

不采用 arbitrary frequency string，也不引入 RRULE / cron。

Quantitative variants 使用 required `exact | approximate` precision。

FrequencyPeriod 只支持 positive integer + day/week/month/year；本轮不加入 hour 或 non-integer period。

### Stress-test 结果

| Case | Canonical decision |
|---|---|
| F1 过去一周漏服 3 次 | observed_count, count=3, window=Interval |
| F2 平均每周 2 次 | rate, value=2, period=1 week |
| F3 每天一次 | recurrence, period=1 day, times_per_period=1 |
| F4 每两周一次 | recurrence, period=2 weeks, times_per_period=1 |
| F5 每周一、三、五 | recurrence, period=1 week, days_of_week={mon,wed,fri} |
| F6 每天早晨 | recurrence, period=1 day, day_part=morning |
| F7 经常 | qualitative, value=often |
| F8 大约每周两次 | rate, value=2, period=1 week, precision=approximate |
| F9 通常每天一次，但上周只发生 3 次 | two BehaviorFrequency items: recurrence + observed_count |
| F10 医嘱每天两次，实际平均每天一次 | prescribed schedule 不进入 actual BehaviorFrequency；actual statement → rate 1/day |

### 理由

Observed count、rate、recurrence 与 qualitative frequency 的 denominator / schedule / evidence meaning 不同。

把它们压成同一个 string 或 numeric value 会重新制造 R1G 已经禁止的语义混淆。

Hour-level recurrence、non-integer period 与完整 scheduler engine 当前没有 stress-case necessity，因此延后而不是提前扩张。

## DR-042 — Observed count, rate, and recurrence remain non-interchangeable

### 决策

ObservedCountFrequency 的 count 可以为 0，window optional。

Count-only source information可以保留，而不发明 window。

RateFrequency 必须显式带 FrequencyPeriod。

RecurrenceFrequency 描述 pattern，不代表 concrete observed occurrences，也不由多条 observation 自动生成。

### 理由

“漏服 3 次”是 count information；“平均每周 3 次”有 denominator semantics；“每周三次”作为 recurrence 则表达 repeated pattern。

三者数值可能相同，但 semantic claim 不同。

强迫 count 必须有 window 会导致 source-only count 无处可放；反过来允许 count 自动变 rate 又会发明 denominator。

## DR-043 — Approximation is explicit semantic precision, not Confidence

### 决策

ObservedCountFrequency、RateFrequency、RecurrenceFrequency 都使用 required：

    precision = "exact" | "approximate"

不通过 numeric rounding、Confidence 或 fuzzy comparison 表达 approximation。

### 理由

“大约每周两次”与“每周两次”语义不同，即使 numeric value 都是 2。

Confidence 回答 producer 对 assertion 的 confidence；approximation 回答 source assertion 本身是否近似。二者不能混为一谈。

## DR-044 — Qualitative frequency uses finite tokens without hidden numeric thresholds

### 决策

R2B3A 使用有限 QualitativeFrequencyToken，而不是 Coding 或 arbitrary text：

    never / rarely / occasionally / sometimes /
    often / frequently / usually / intermittently / always

这些 token 不绑定 numeric threshold、probability、rate 或规范性 severity order。

### 理由

当前 Core 需要稳定 machine discrimination，但没有可信依据把 “often” 定义为某个百分比。

使用有限 token 可以覆盖 R1G 已出现的 qualitative expressions，同时避免引入外部 vocabulary dependency。

Exact-token equality 也不会假装 “often” 与 “frequently” 是自动同义词。

## DR-045 — PreferenceValue uses a minimal four-way tagged union

### 决策

PreferenceValue 冻结为：

    coded | text | boolean | number

Numeric variant 增加 required comparator：

    eq | lt | lte | gt | gte

unit 使用 optional Coding。

不新增 ordinal/strength、reference-valued 或 list/multi-select variant。

### Stress-test 结果

| Case | Canonical decision |
|---|---|
| P1 偏好口服给药 | coded when reliable terminology mapping exists |
| P2 不接受电话联系 | boolean only when category semantics is genuinely binary; otherwise coded/text |
| P3 偏好上午联系 | coded if reliable concept exists; otherwise text |
| P4 希望医生先和女儿沟通 | text fallback when no reliable structured value binding exists |
| P5 等待时间不超过 30 分钟 | number, operator=lte, value=30, unit=Coding(minutes) |
| P6 强烈偏好居家管理 | coded/text value for home management; “强烈” not converted into strength score |
| P7 legacy raw string, no reliable type mapping | text |

### 理由

四个 variant 足以覆盖当前真实 stress cases，同时避免把完整 FHIR datatype system搬入 Core。

P5 证明 bare numeric value 不足以保存比较语义，因此 comparator 是必要的最小字段。

P6 不足以证明需要 ordinal preference-strength type；本轮明确禁止 preference-strength analytics，因此保留 source wording而不发明强度值。

## DR-046 — Free text is a fidelity fallback, not a typed-value escape hatch

### 决策

PreferenceValue text variant 在 reliable typing / terminology mapping 不可得时允许保真迁移。

当 applicable normative binding 明确支持可靠 Coding 时，不应为了实现方便把 typed semantics降级为 Text。

Legacy raw string 如果无法可靠类型化，必须保留为 Text，而不是猜 code、boolean、number、operator 或 unit。

### 理由

完全禁止 Text 会迫使 legacy migration 发明不存在的类型信息；完全放任 Text 又会让 consumer 必须重新 NLP 所有 preference values。

因此 R2B3A 采用“可靠结构化优先、无法可靠类型化则 Text 保真”的单向边界。

## DR-047 — Context uses a dedicated coded/text value union

### 决策

Context concrete shape：

    Context {
        value       : ContextValue
        provenance? : Provenance[1..*]
    }

ContextValue 只包含：

    coded | text

不采用 generic metadata object，也不复用 PreferenceValue。

### Stress-test 结果

| Case | Canonical decision |
|---|---|
| C1 traveling + frequent misses | traveling → Context；frequency → BehaviorFrequency |
| C2 work setting + phone preference | work setting → Context；value → PreferenceValue |
| C3 family support present | Context；不自动表示 family support caused preference |
| C4 communication via WeChat | contextual communication concept → Context；不是 workflow status |
| C5 because nausea stopped medication | BehaviorFactor reported_reason，不是 merely Context |
| C6 stopped medication while traveling | Context when only co-occurrence is supported |
| C7 owner {P1,P2}, Context only P1 | local provenance required |
| C8 complete applicable provenance same as owner | local provenance omitted canonical form |
| C9 mixed free-text “在家里比较规律” | 若 source semantics 可可靠分解：“在家里” → Context；“比较规律” → BehaviorFrequency；不能结构化的剩余 wording → Evidence / Annotation；整句不得作为单一 Context machine value |
| C10 traveling + workday + family support | multiple Context items coexist；collection order no priority |

### 理由

当前 stress cases 需要的是 contextual concept，而不是一个跨领域 predicate engine。

单个 coded concept 可以表达 machine-interpretable context；text fallback 保留暂时无法 terminology-map 的来源信息。

额外 boolean / number variants 当前没有必要，type+value schema 也会提前要求一个尚未存在的 context-dimension ontology。

## DR-048 — Context text is a fidelity fallback, not a catch-all

### 决策

可靠 Context Coding 存在时 SHOULD 使用 coded variant。

无法可靠 terminology-map 时允许 TextContextValue。

不得发明 code，也不得把所有 Context 退化成 text。

### 理由

完全强迫 Coding 会让 legacy / narrative context 被迫发明 terminology；完全放任 text 会让 downstream 必须重新 NLP 本可可靠结构化的语义。

该边界沿用 PreferenceValue 的“可靠结构化优先、否则保真”，但不引入 preference comparator / choice semantics。

## DR-049 — BehaviorFactor separates role, factor value, direction, and derivation

### 决策

BehaviorFactor 使用四个独立 semantic dimensions：

    role
    factor
    direction
    provenance.derivation

FactorRole：

    reported_reason
    observed_association
    antecedent
    explanatory

FactorDirection：

    factor_to_behavior
    behavior_to_factor
    unspecified

FactorValue：

    coded | text

`inferred` 不作为 FactorRole；它继续属于 Provenance.derivation。

### Stress-test 结果

| Case | Canonical decision |
|---|---|
| B1 “因为头晕，我停药了” | reported_reason + factor_to_behavior；source attribution ≠ verified cause |
| B2 nausea then medication stopped | antecedent + factor_to_behavior；not reason |
| B3 model says work stress may explain misses | explanatory + factor_to_behavior + local inferred provenance |
| B4 nausea co-occurs with stopping | observed_association；direction per source or unspecified |
| B5 symptom → behavior explicit | preserve factor_to_behavior |
| B6 behavior → symptom explicit | preserve behavior_to_factor |
| B7 direction unclear | direction=unspecified |
| B8 dizziness/nausea reliably mapped | coded FactorValue |
| B9 only source wording | text FactorValue |
| B10 factor is existing Behavior/Preference | use Relation |

### 理由

把 role、direction 与 derivation 压成一个 `type` string 会再次混淆 source attribution、temporal orientation 与 inference status。

独立 axes 可以保留 R1E 边界，同时避免新增 `factor.inferred=true` 之类重复字段。

## DR-050 — Factor direction is orientation, not causality

### 决策

FactorDirection REQUIRED，并显式提供 `unspecified`。

`factor_to_behavior` / `behavior_to_factor` 只记录 source-supported semantic orientation。

reported_reason / antecedent 要求 factor_to_behavior，但这仍不等于 verified causal direction。

### 理由

Legacy `symptom_triggered` 本身有方向歧义。

如果 direction optional，省略可能被误解为 default direction；required + unspecified 可以明确表示“来源没有方向”。

同时，不把 direction 当 causality 能保留 R1E 已冻结的 non-causal boundary。

## DR-051 — Factor value stays non-Core; Core entity relationships remain Relation

### 决策

FactorValue 仅为 coded / text non-Core semantic factor。

如果 factor 实际是当前 document 中已有 Behavior / Preference entity，则必须使用 Relation。

不新增 Symptom entity，也不允许 factor text/code 冒充 CoreEntityRef。

### 理由

BehaviorFactor 的职责是 Behavior-local non-Core factor。

若允许它同时指向 Core entity，就会形成与 Relation 平行的第二套 entity-link system，破坏 R1B/R1H endpoint / provenance / relation-type contract。

## DR-052 — Context vs BehaviorFactor is decided by source semantics, not keywords

### 决策

同一个 lexical concept 可以根据 source semantics进入不同 structure：

- “旅行期间漏服” → Context；
- “因为旅行漏服” → reported_reason BehaviorFactor；
- “恶心时停药”若只是 contextual coincidence → Context；
- “因为恶心停药” → reported_reason BehaviorFactor。

不得根据 traveling / nausea / because-like keyword list 自动分类。

### 理由

Context 表达 situation qualification；BehaviorFactor 表达 factor-role semantics。

Lexical concept 本身不能证明 reason / causality。分类必须依据 source assertion 的 semantic relation，而不是单词。

## DR-053 — Canonical absence uses omission; Core has no semantic null

### 决策

Optional field absence 用 field omission 表示。

当前 Core 没有任何 type 定义 JSON null 为 semantic value，因此 canonical `field:null` invalid。

Required root arrays 保持显式；普通 optional collection empty 是 normalization-required，normal form省略；local `provenance:[]` 因 omission具有 inheritance语义而直接 invalid。

### 理由

如果 omission、null、empty collection并存，会产生多种等价或含糊 representation。

单一 omission rule让 R2C Schema 与 canonicalizer边界清楚，同时保留 root required-array decision。

## DR-054 — Canonical Core objects use closed field sets

### 决策

所有 concrete Core objects / embedded structured objects使用 closed field set。

Unknown property、legacy alias、typo field均不是 canonical Core。

Future extension必须有显式机制；arbitrary unknown property不是 extension。

### 理由

JSON Schema前如果不冻结 closed/open policy，legacy fields如 `weight`、`confidence_score`、`behavior_type` 可以静默与 canonical ownership并存，从而重新制造 dual semantics。

## DR-055 — Semantic strings and numbers use cross-type consistency rules

### 决策

Generic non-empty identifier/code/locator/metric/version strings必须包含至少一个 non-Unicode-White_Space code point；不自动 trim / case-fold / Unicode-normalize。

Numeric equality使用 exact mathematical value，不依赖 JSON lexical spelling；`1`、`1.0`、`1e0` numeric-semantic equal，`-0` 与 `0` equal。

不使用 fuzzy tolerance。

### 理由

“non-empty”如果允许 whitespace-only，会让 locator / metric / code等字段形式存在而实质为空。

数值 lexical spelling属于 serializer层；混入 semantic equality会造成 Confidence / Rate / PreferenceValue之间不一致。

## DR-056 — Identity, content equality, and full canonical-information equality are distinct

### 决策

R2B4统一区分：

- identity equality；
- semantic content equality；
- full canonical-information equality。

Entity id相同不代表 state相同。

Relation无 id，因此使用 assertion content equality + full canonical-information equality。

TemporalExtent、Annotation、Context、BehaviorFactor、BehaviorFrequency等 embedded structures按需要区分 content与full equality。

### 理由

Diff、dedup、normalization与reference identity是不同问题。

把它们压成一个“equals”会导致 annotation/provenance变化错误地创建 identity，或反过来丢失 canonical information。

## DR-057 — Duplicate handling follows identity and full canonical information

### 决策

Identity-bearing root entities通过 EntityId uniqueness禁止 duplicate identity。

No-id / embedded collections只有在 item **full canonical-information equal** 时才视为 representation redundancy并 canonical-dedup。

Relation same endpoints绝不足以 dedup。

days_of_week duplicate token继续 invalid，而不是 normalization-only。

### 理由

机械“所有数组去重”会错误合并不同 provenance / temporal / role assertions。

完全不去重又会允许同一无身份 assertion无限重复形成多种 canonical forms。

Full equality提供安全边界。

## DR-058 — Semantic ordering is frozen; byte-level deterministic JSON is separate

### 决策

当前 Core collection order与 JSON object member order不具有 semantic meaning。

R2B4不冻结 byte-identical JSON排序 / number spelling / pretty-print profile。

Future deterministic serialization profile必须建立在R2B4 equality与normal form上，不能反向改变 semantics。

### 理由

现在可以明确比较 semantic canonical documents，而无需先设计一个可能循环依赖“canonical JSON bytes”的 structural sort key。

这也允许 R2C JSON Schema立即施工。

## DR-059 — Text fidelity fallback cannot cross semantic dimensions

### 决策

TextPreferenceValue、TextContextValue、TextFactorValue只能承载各自 tagged type的 semantic dimension。

Mixed wording如果能够可靠分解，应分别进入对应 canonical fields；无法结构化部分可由 Evidence / Annotation保真。

Text fallback不能藏 Relation link、frequency、temporal extent、workflow status、reason role或CoreEntityRef。

### 理由

Text fallback的目的是真实信息保真，不是让已冻结 structured semantics重新变成 NLP-only blob。

这修正 DR-047 C9 对“在家里比较规律”的潜在误读。

## DR-060 — Semantic validity and canonical normal form are different states

### 决策

R2B4区分：

- semantic-valid；
- normalization-required；
- canonical normal form。

Redundant full-equal duplicate、普通 optional empty array、redundant explicit inherited provenance属于 normalization-required。

null、unknown field、empty local provenance、invalid union、duplicate EntityId等属于 invalid。

### 理由

后续 Schema不应被迫承担 semantic equivalence / dedup；canonicalizer也不应把真正 invalid structure当作“随便修一下”。

## DR-061 — R2C Schema owns structure, not references, normalization, or vocabulary semantics

### 决策

R2B4建立 STRUCTURAL / REFERENCE / SEMANTIC / NORMALIZATION / VOCABULARY 五类 invariant。

R2C JSON Schema只承担 structural层及可直接表达的 conditional structure。

Reference resolution、semantic source meaning、normalization equality与 Relation vocabulary contract由各自层负责。

### 理由

如果 generic JSON Schema试图承担 document-wide reference、source semantic interpretation或 relation vocabulary directionality，它会变成不可维护的伪语义执行器。

明确分层使 R2C可以施工而不重新猜 Core shape。

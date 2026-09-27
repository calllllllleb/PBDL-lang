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

具体 ISO 8601 serialization、partial-date 表示与 relative-time syntax 留待后续。

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

每个 type 必须具有稳定定义，并说明 endpoint semantic roles 与 directionality semantics。Directional type 中 endpoint 交换会改变或破坏语义；symmetric / non-directional type 中 endpoint 交换不能被解释为另一种 semantic relation meaning。

Source → target 的箭头本身不表示 cause、precedes、influence、priority 或 importance。

Directional 也不等于 causal。

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

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

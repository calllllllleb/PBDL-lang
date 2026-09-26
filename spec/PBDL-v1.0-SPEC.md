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
- Evidence / Provenance（证据 / 来源追踪）
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

### 4.2 事实与派生结果分离

PBDL-Core **MUST** 区分来源直接描述的事实与外部系统派生出的分析结果。

除非被明确表示为外部派生工件，否则 PBDL-Core **MUST NOT** 将以下内容视为来源事实：

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

当前候选 PBDL-Core 实体包括：

- Patient / Subject
- Behavior
- Preference
- Context
- Evidence / Provenance
- Relation

精确的抽象数据模型、基数约束、包含关系、标识符作用域和序列化字段仍为 **TODO**。

Behavior **MUST** 在有效引用所需的作用域内能够被唯一标识。具体标识字段名称及其精确作用域仍为 **TODO**。

Behavior 与 Preference **MUST** 能够追踪至其来源证据或来源信息。具体表示方法及基数关系仍为 **TODO**。

Relation **MUST** 引用明确存在的实体，并且 **MUST NOT** 引用未定义实体。允许作为关系端点的实体类型与引用语法仍为 **TODO**。

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

Patient / Subject 是 PBDL-Core 的候选核心概念，用于表示行为与偏好所归属的主体。

其最终命名、声明语法、身份模型、隐私敏感表示方式和必填字段仍为 **TODO**。

## 10. Behavior

Behavior 是 PBDL 重新设计中的核心研究对象。

Behavior **MUST** 能够被唯一标识，以支持合法引用。

Behavior **MUST** 支持通过 Evidence / Provenance 追踪其来源。

具体字段、行为类型词表、时间模型、定量表示方式和语法仍为 **TODO**。

## 11. Preference

Preference 是 PBDL 重新设计中的核心研究对象。

Preference **MUST** 支持通过 Evidence / Provenance 追踪其来源。

具体字段、偏好类型词表、取值模型、强度模型、时间模型和语法仍为 **TODO**。

## 12. Context

Context 是 PBDL-Core 的候选核心概念，用于承载解释 Behavior 或 Preference 所需的上下文信息。

上下文模型、作用域规则、允许的维度、继承规则和语法仍为 **TODO**。

## 13. Evidence 与 Provenance

Behavior 与 Preference **MUST** 能够追踪至其来源。

Evidence / Provenance 的精确结构尚未冻结。

### 13.1 非规范性候选来源类型

下列值仅作为设计候选记录，**不构成已经冻结的枚举**：

- `self_report`
- `ehr`
- `survey`
- `interview`
- `device`
- `manual_annotation`
- `model_inference`

**TODO：** 定义来源身份、来源类型绑定、时间戳、原始片段或外部引用、作者或代理信息、是否需要置信度表示，以及来源链追踪方式。

## 14. Relations

Relation 用于连接明确存在的实体。

Relation **MUST** 引用已经定义的实体，并且 **MUST NOT** 引用未定义实体。

PBDL-Core 当前不将 `causal_effect` 定义为默认关系，也不把未经证据支持的因果权重作为 Core 的默认能力。

规范性关系词表、关系端点约束、方向性、多重性和语法仍为 **TODO**。

候选关系术语在正式冻结之前只能记录于非规范性设计文档中。

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

1. PBDL-Core **MUST** 区分来源直接描述的事实与派生分析结果。
2. Behavior 与 Preference **MUST** 支持来源 / Provenance 追踪。
3. Relation **MUST NOT** 引用未定义实体。
4. PBDL-Core **MUST NOT** 将未经证据支持的因果权重作为来源事实或默认 Core 语义。
5. Treatment Pathway 不属于初始重新设计中的 PBDL-Core。

其他跨实体约束、基数规则、身份规则与校验语义仍为 **TODO**。

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

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

R1B 冻结以下四类核心语义对象的最小边界：

- Subject：Behavior 与 Preference 所描述的主体，以及文档内主体引用的稳定锚点。
- Behavior：对某个 Subject 已描述或已断言的行为、未发生行为或行为状态的表示。
- Preference：对某个 Subject 已表达或已推断的倾向、选择、优先级、厌恶或偏好的表示。
- Relation：在允许的端点类型之间显式表达语义联系的 Core 构造。

Context 与 Evidence / Provenance 仍属于 PBDL-Core 的候选概念，但其详细结构与 identity 要求不在 R1B 冻结。

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

Behavior 的具体字段、行为类型词表、时间模型、trigger / symptom 模型、Evidence / Provenance 结构和语法仍为 **TODO**。

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

Preference 的具体字段、偏好类型词表、取值模型、confidence、Evidence / Provenance 结构、时间模型和语法仍为 **TODO**。

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

### 14.2 Relation identity

Relation 在 v1 Core 最小模型中**不要求自身具有 identity**。

这是因为当前没有已冻结的 Core reference 需要指向 Relation 本身，且 Relation 也不是允许的 Relation endpoint。

未来若 Evidence / Provenance、extension 或其他明确使用场景需要稳定引用 Relation，可在后续设计轮次增加 relation identity requirement；R1B 不提前冻结。

### 14.3 Relation type is not causality by default

Relation type concept 用于说明 source 与 target 之间“是什么关系”，但 Relation type **MUST NOT** 因其名称或存在本身就被解释为因果关系。

PBDL-Core 当前不将 `causal_effect` 定义为默认关系，也不把未经证据支持的因果权重作为 Core 的默认能力。

规范性 relation vocabulary、temporal semantics、derived relation strength、方向性细则与语法仍为 **TODO**。

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

1. PBDL-Core **MUST** 区分来源直接描述的信息与派生分析结果。
2. 一个 PBDL document **MUST** 至少包含一个 Subject，并 **MAY** 包含多个 Subject。
3. Subject、Behavior 与 Preference **MUST** 具有 document-local identity。
4. Subject、Behavior 与 Preference 共享同一个 document-local identity namespace，其 identifier **MUST** 在所属 PBDL document 内唯一。
5. identifier **MUST NOT** 由数组位置或列表顺序充当规范性 identity。
6. Behavior 与 Preference **MUST** 各自绑定到恰好一个 Subject。
7. Behavior type、Preference category、显示标签与 Relation type **MUST NOT** 自动充当 entity instance identity。
8. Core reference **MUST** 在当前文档 reference scope 内解析到恰好一个实体。
9. undefined reference 与 ambiguous reference 均无效。
10. Relation source / target **MUST** 使用明确 entity reference，不能使用未解析的自由文本标签。
11. Core Relation endpoint 仅允许 Behavior 与 Preference；Subject 与 Relation 均不是 R1B 中的 Relation endpoint。
12. Relation 在 v1 Core 最小模型中不要求 identity，且 Relation **MUST NOT** 作为 Relation endpoint。
13. Behavior 与 Preference **MUST** 支持来源 / Provenance 追踪，但其详细结构不在 R1B 冻结。
14. PBDL-Core **MUST NOT** 将未经证据支持的因果权重作为来源事实或默认 Core 语义。
15. Treatment Pathway 不属于初始重新设计中的 PBDL-Core。

跨文档 identity / reference protocol、temporal model、Evidence / Provenance 详细结构、confidence、trigger / symptom、术语词表和 Constraint 模型仍为 **TODO**。

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

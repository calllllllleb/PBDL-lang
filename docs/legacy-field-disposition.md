# R1A — 旧字段去向兼容性审计

> 文档性质：非规范性设计审计
> 审计对象：历史 PBDL 字段体系
> 审计目标：在保留历史兼容性的前提下，明确字段在新版架构中的职责归属
> 规范性来源：`spec/PBDL-v1.0-SPEC.md`

本文件只记录兼容性审计结论，不直接修改 PBDL 的规范性语义。

- Historical PBDL fields are preserved as design history.
- This document does not itself redefine normative PBDL semantics.
- Final normative decisions must later be reflected in `spec/PBDL-v1.0-SPEC.md`.
- The goal is compatibility-preserving refinement, not historical field deletion.

换言之，本轮不是推翻旧 PBDL，也不是直接删除旧字段，而是把历史字段逐项放回更清晰的架构层级：PBDL-Core、扩展、外部派生结果，或待重新设计的语义位置。

---

## 1. 审计范围

旧研究报告中正式出现并定义过的字段共 32 个：

- Behavior：10 个
- Preference：7 个
- Treatment Path：7 个
- StepObject：3 个
- Relation：5 个

本轮对全部 32 个字段进行逐项审计。

本文件：

- 不修改 `spec/PBDL-v1.0-SPEC.md`
- 不修改 grammar
- 不修改 JSON Schema
- 不修改 vocabulary
- 不冻结新的字段结构
- 不实现 Parser / Validator
- 不创建 `src/`
- 不修改 CHANGELOG

---

## 2. Disposition 分类

### KEEP_CORE

字段继续属于 PBDL-Core。

适用于仍然直接描述患者行为、偏好或其基础关系语义的概念。

### KEEP_EXTENSION

字段继续保留，但属于扩展，不属于最小 PBDL-Core。

本轮最主要的候选扩展是：

`PBDL-Pathway`

### MOVE_DERIVED

字段继续存在于 PBDL 生态中，但其语义属于外部分析、验证、推理或评分结果。

这类字段不得继续伪装成 source-described fact。

### REFINE

历史概念仍然有价值，但旧字段的名称、类型、作用域或语义边界需要重新设计。

`REFINE` 不代表删除，而代表“保留概念、重新定义表达方式”。

### DEPRECATE

字段保留历史兼容价值，但新版文档 **SHOULD NOT** 再新增使用。

废弃不等于物理删除；必须记录替代方案。

---

## 3. Primary disposition 规则

为了保证统计可验证，每个 legacy field 恰好只有一个 **primary disposition**。

对于同时满足“仍属于 Core/Extension”且“表达方式需要重做”的字段，本轮优先使用 `REFINE` 作为 primary disposition，并在 “New semantic role” 与兼容性说明中记录其预计归属。

因此：

- `temporal_scope` 不是同时计入 KEEP_CORE 与 REFINE，而只计入 REFINE。
- `path_condition` 不是同时计入 KEEP_EXTENSION 与 REFINE，而只计入 REFINE，并明确其未来语义仍位于 Pathway extension。
- `weight` 只计入 MOVE_DERIVED；未来若存在来源直接声明的 relation strength，应另行设计，不复用当前默认含义。

---

## 4. 完整字段审计矩阵

| # | Legacy field | Legacy owner | Legacy meaning | Primary disposition | New semantic role | Reason | Compatibility note | Future normative action | Open question |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | `behavior_type` | Behavior | 行为类别 | KEEP_CORE | Behavior 基础分类语义 | 直接描述患者行为本身，是 Core 的基础语义之一 | 保留历史字段概念；具体 vocabulary 尚未冻结 | 后续在 SPEC / vocabulary 中正式定义分类绑定方式 | 类型词表采用封闭枚举、开放词表还是 terminology binding？ |
| 2 | `executor` | Behavior | 行为执行者 | KEEP_CORE | Behavior participant / executor | “谁执行该行为”属于行为描述本身，而不是外部推理结果 | 历史概念保留；不在本轮确定字段类型 | 后续明确主体引用、角色与身份模型 | executor 是否仅限患者本人，还是允许 caregiver / clinician / device？ |
| 3 | `temporal_scope` | Behavior | 行为发生或适用的时间范围 | REFINE | Core temporal semantics | 时间概念必须保留，但旧版时间表达方式不足以支撑统一语义 | 概念保留，不直接沿用旧字段类型 | 后续设计统一 temporal abstraction，并决定是否复用于 Relation / Context | 时间点、区间、频率、持续性、相对时间如何统一表达？ |
| 4 | `behavior_trigger` | Behavior | 行为触发因素或原因 | REFINE | Reported / observed trigger or reason | 旧命名容易把“相关、报告原因、观察到的触发因素”误解为已成立因果关系 | 历史信息应保留，但不得默认解释为 guaranteed cause | 后续明确 trigger/reason 的证据类型与关系语义 | 应作为 Behavior 属性、Context，还是 Relation（如 `reported_reason_for`）表达？ |
| 5 | `symptom_triggered` | Behavior | 与行为相关的症状触发信息 | REFINE | Associated symptom / symptom context | 历史名称存在方向和因果歧义；症状与行为的关系需要显式区分关联、先后与报告原因 | 不删除概念，但禁止默认解释为“行为导致症状”或“症状必然导致行为” | 后续重新命名或迁移到 Relation / Context 表达 | 真实历史定义的方向是否稳定？是否需要拆成 symptom association 与 trigger 两种语义？ |
| 6 | `communication_status` | Behavior | 行为或信息是否已沟通、沟通状态 | REFINE | Candidate contextual / communication metadata | 概念可能有价值，但明显绑定医疗沟通场景，是否属于最小 Core 尚不明确 | 历史字段保留；本轮不决定 Core 或专门 extension | 后续通过代表性使用场景审计决定最终归属 | 它是患者行为固有属性，还是临床工作流/沟通扩展中的状态？ |
| 7 | `risk_tag` | Behavior | low / medium / high 等风险标签 | MOVE_DERIVED | External RiskAssessment / AnalysisResult | 风险等级通常由规则、模型或临床分析计算，并非行为自身的来源事实 | 历史字段可读取，但新版不得把它当成 Behavior intrinsic fact | 后续若需要表示风险结果，应定义外部派生工件及 provenance | 是否需要通用 AnalysisResult 抽象，还是由应用自行定义？ |
| 8 | `validity_flag` | Behavior | 当前对象是否合法或是否通过校验 | DEPRECATE | Validator output | 文档内容不应保存“我自己是否合法”的自描述标志；合法性应由 Validator 对具体版本和规则计算 | 旧数据中的字段不得物理删除，但新版 SHOULD NOT 新增 | 后续定义 Validator 输出与错误码，不在 PBDL payload 中保留此标志 | 旧实例迁移时是忽略、保留为 legacy annotation，还是外移到 validation report？ |
| 9 | `evidence_source` | Behavior | 行为信息的证据或来源 | REFINE | Unified Evidence / Provenance | 来源追踪是 Core 必需能力，但单一字段不足以表达来源身份、时间、引用、代理等信息 | 强烈保留概念；不冻结现有字符串或枚举形式 | 后续与 Preference 的 `source_type` 一起审计统一 provenance/source abstraction | Evidence 与 Provenance 是一个对象还是两层模型？如何表示多来源？ |
| 10 | `reasoning_note` | Behavior | 对行为的解释或推理备注 | REFINE | Descriptive annotation / externally attributed reasoning note | 自由文本备注有兼容价值，但“reasoning”容易被误解为 PBDL-Core 自身推理结论 | 可保留历史文本，但必须区分来源备注、人工解释与模型推理 | 后续决定是否改名为通用 note/annotation，或显式标记 author / derivation | 是否需要与 Preference 的 `note` 收敛到统一 annotation 模型？ |
| 11 | `preference_category` | Preference | 偏好类别 | KEEP_CORE | Preference 基础分类语义 | 直接描述 Preference 的类别，是核心语义 | 保留历史概念；具体 vocabulary 尚未冻结 | 后续在 SPEC / vocabulary 中定义分类机制 | 是否使用开放词表、受控词表或 terminology binding？ |
| 12 | `preference_value` | Preference | 偏好具体内容或取值 | KEEP_CORE | Preference value | 这是偏好的核心陈述内容 | 保留概念，但不在本轮冻结数据类型 | 后续定义值模型与可能的类型系统绑定 | 单值、多值、排序、范围和否定偏好如何表达？ |
| 13 | `preference_conflict_flag` | Preference | 偏好是否与其他对象发生冲突 | MOVE_DERIVED | ConflictAnalysis result | “冲突”必须相对于另一个偏好、路径、计划或约束计算，不是 Preference 自身固有属性 | 历史字段可映射为外部分析结果 | 后续如有需要定义 ConflictAnalysis / AnalysisResult，不放回 Preference Core | 冲突分析的比较对象与算法如何记录 provenance？ |
| 14 | `source_type` | Preference | 偏好来源类型 | REFINE | Unified Evidence / Provenance source classification | 来源语义必须保留，但与 Behavior 的 `evidence_source` 存在重复和定义漂移 | 历史字段保留；不冻结旧 enum | 后续与 `evidence_source` 收敛为统一 provenance/source 模型 | source type 是 Evidence 属性、Provenance 属性还是独立 Coding？ |
| 15 | `confidence_score` | Preference | 偏好陈述的置信度 | REFINE | Assertion / inference confidence metadata | 对模型推断信息有价值，但 self-report 等直接来源不应被迫使用模型式置信度 | 保留概念，但不得作为所有 Preference 的强制属性 | 后续明确其适用对象、计算主体与 provenance；可能归属于 derived assertion metadata | 是 Core 可选 provenance metadata，还是仅属于模型推断扩展？ |
| 16 | `associated_behavior` | Preference | 与该偏好关联的行为 | REFINE | Explicit reference / Relation between Preference and Behavior | 关联概念有价值，但随意字符串标签无法保证引用完整性 | 历史关联应保留，未来应通过正式引用或 Relation 表达 | 后续决定是专门引用字段还是统一 Relation | 是否需要特定 relation type，还是 generic Relation 即可？ |
| 17 | `note` | Preference | 自由文本备注 | KEEP_CORE | Human-readable descriptive annotation | 通用备注可作为对来源描述的补充，不天然属于外部推理 | 保留；不得把 note 自动解释为事实或模型结论 | 后续仅需明确 note 的非结构化、非推理权威性质 | Behavior 与 Preference 是否共用统一 Annotation 类型？ |
| 18 | `path_id` | Treatment Path | 路径标识符 | KEEP_EXTENSION | PBDL-Pathway extension identity | Treatment Pathway 已在 R0 明确不属于 Core，但历史能力应保留 | 作为 candidate `PBDL-Pathway` extension 的历史字段继续保留 | 后续若批准 Pathway extension，再冻结其 identity model | extension 的标识符作用域如何定义？ |
| 19 | `path_node` | Treatment Path | 路径节点 | KEEP_EXTENSION | PBDL-Pathway node | 属于路径建模能力，而非患者行为/偏好最小 Core | 保留为历史 Pathway capability | 后续由 PBDL-Pathway 设计节点模型 | node 是引用、对象、图节点还是步骤容器？ |
| 20 | `path_condition` | Treatment Path | 路径分支或执行条件，历史上可为自由字符串 | REFINE | PBDL-Pathway condition expression | 概念属于 Pathway extension，但旧自由字符串不足以形成机器可验证条件语义 | 保留概念，不冻结旧表达方式 | 后续在 PBDL-Pathway 中单独设计条件表达；不得借本轮偷渡完整表达式语言 | 条件语言是受限表达式、结构化谓词还是外部规则引用？ |
| 21 | `path_dynamic_score` | Treatment Path | 路径动态评分 | MOVE_DERIVED | Pathway scoring / ranking result | 动态评分通常由模型、规则或算法计算，不是路径静态定义本身 | 历史结果保留为 derived artifact | 后续定义外部 scoring result 与 derivation/provenance | 是否需要通用 ScoreResult，而不是 Pathway 专用字段？ |
| 22 | `steps` | Treatment Path | 路径步骤集合 | KEEP_EXTENSION | PBDL-Pathway step collection | 路径步骤是历史 Pathway 能力的核心组成，不应删除，但不属于 PBDL-Core | 保留到 candidate PBDL-Pathway extension | 后续扩展设计时定义顺序、分支、引用与基数 | steps 是线性序列还是图结构？ |
| 23 | `_guideline` | Treatment Path | 路径关联的指南信息 | KEEP_EXTENSION | PBDL-Pathway guideline/reference metadata | 指南绑定属于 Pathway / knowledge integration 层，而非最小行为偏好 Core | 历史能力保留；下划线命名不代表未来规范名称 | 后续 extension 设计时明确 external reference / Coding / citation 方式 | 是引用指南实体、版本、章节还是规则来源？ |
| 24 | `_deviation_analysis` | Treatment Path | 对路径偏离的分析结果 | MOVE_DERIVED | PathwayDeviationAnalysis | “偏离分析”需要比较事实与路径/指南后计算，属于外部分析结果 | 历史字段可迁移为 derived artifact | 后续定义分析结果及其输入、算法和 provenance | 偏离是描述性差异、规则违规还是临床判断？必须避免混为一谈 |
| 25 | `action` | StepObject | 路径步骤中的动作 | KEEP_EXTENSION | PBDL-Pathway step action | StepObject 属于历史 Treatment Pathway 结构，因此整体位于 extension | 保留历史字段 | 后续由 PBDL-Pathway 决定 action 的表示方式 | action 是自由文本、编码概念还是外部任务引用？ |
| 26 | `status` | StepObject | 路径步骤状态 | KEEP_EXTENSION | PBDL-Pathway step state | 属于路径执行/状态描述，不属于最小 PBDL-Core | 保留历史字段，不在本轮冻结状态枚举 | 后续 extension 明确静态定义与运行时状态边界 | status 属于路径定义还是 workflow runtime？ |
| 27 | `outcome` | StepObject | 路径步骤结果 | KEEP_EXTENSION | PBDL-Pathway step outcome | 作为 Pathway 历史结构应保留，但需要避免把推断结果与实际观察混为一谈 | 保留字段概念；具体语义未来明确 | 后续 extension 区分 observed outcome、expected outcome 与 inferred outcome | outcome 是否需要 Evidence / Provenance？ |
| 28 | `source` | Relation | 关系起点实体 | KEEP_CORE | Relation source reference | 明确关系端点是 Core Relation 的基础能力 | 保留历史概念；具体引用语法未冻结 | 后续 SPEC 定义实体引用和作用域规则 | source 可以引用哪些 Core / extension 实体？ |
| 29 | `target` | Relation | 关系终点实体 | KEEP_CORE | Relation target reference | 明确关系端点是 Core Relation 的基础能力 | 保留历史概念；具体引用语法未冻结 | 后续 SPEC 定义实体引用和作用域规则 | target 可以引用哪些 Core / extension 实体？ |
| 30 | `type` | Relation | 关系类型 | KEEP_CORE | Relation semantic type | Relation 需要显式类型才能形成可解释语义 | 保留概念，但不得默认把任意 type 解释为因果关系 | 后续冻结 relation vocabulary / terminology binding；因果类型若存在必须单独论证 | relation vocabulary 是封闭枚举还是可扩展术语绑定？ |
| 31 | `weight` | Relation | 关系权重、统计强度或因果强度 | MOVE_DERIVED | Externally derived relation strength / statistic | 旧报告中的 weight 常来自统计或模型计算，不能作为默认 source-described relation 属性 | 历史值应保留其计算来源；新版默认 Relation 不假设 intrinsic weight | 后续若需要 relation strength，应显式记录 derivation、method 与 provenance | 是否存在来源直接声明的“强度”？若存在应否使用不同字段/对象以避免与模型 weight 混淆？ |
| 32 | `temporal` | Relation | 关系的时间或时间顺序信息 | REFINE | Relation temporal semantics | 时间关系属于重要基础语义，但旧字段粒度和方向性不明确 | 保留概念，不冻结旧格式 | 后续与 Behavior 的 temporal model 协同设计 | 表示关系发生时间、有效期、先后顺序还是时距？是否应拆分？ |

---

## 5. 关键语义审计

### 5.1 Fact 与 Derived Result

历史字段中存在两类性质不同的信息。

#### Source-described / descriptive information

这些字段直接描述患者、行为、偏好或基础关系语义，例如：

- `behavior_type`
- `executor`
- `preference_category`
- `preference_value`
- Relation 的 `source` / `target` / `type`

这些信息适合作为 PBDL-Core 的组成部分，或者在表达方式尚不成熟时以 `REFINE` 保留。

#### Derived information

以下字段的主要语义依赖外部计算、比较、推理或校验：

- `risk_tag`
- `preference_conflict_flag`
- `path_dynamic_score`
- `_deviation_analysis`
- Relation 的 `weight`

它们被归入 `MOVE_DERIVED`。

`validity_flag` 更进一步：它不是患者语义，而是校验过程的输出，因此归入 `DEPRECATE`，未来由 Validator output 替代。

核心原则是：

> PBDL 数据可以引用或承载外部派生工件，但派生结果不得被默认为 source-described fact。

---

## 6. Behavior、Preference 与 Analysis 的职责边界

旧字段体系中，一些字段放在对象内部并不代表它在语义上就是对象自身属性。

典型例子：

### `preference_conflict_flag`

冲突不是 Preference 的固有属性。

同一个 Preference：

- 可能与路径 A 冲突；
- 与路径 B 不冲突；
- 与另一个 Preference 在特定 Context 下才冲突。

因此，冲突必须相对于比较对象、上下文和分析方法计算。

它应属于派生分析结果，而不是 Preference Core。

### `risk_tag`

风险同样依赖风险模型、阈值、时间窗口和目标事件。

因此它不是 Behavior 的内在属性。

### `_deviation_analysis`

路径偏离只有在选定某个 Pathway、Guideline 或预期行为后才能成立，因此是比较/分析结果。

---

## 7. 因果语义兼容性问题

新版 PBDL 不直接继承旧设计中可能产生的因果暗示。

### 7.1 `behavior_trigger`

旧字段名中的 “trigger” 不能默认解释为：

`A caused B`

未来更安全的语义方向包括：

- reported trigger
- observed trigger
- reported reason
- associated context

具体方案本轮不冻结。

### 7.2 `symptom_triggered`

该字段的旧名称存在方向歧义。

不得默认推出：

- 行为导致症状；
- 症状必然导致行为。

未来必须明确其方向、证据来源与关系类型。

### 7.3 Relation `type`

保留 `type` 不等于默认支持 causal relationship。

任何未来因果关系类型都必须经过单独的规范设计与证据要求讨论。

### 7.4 Relation `weight`

旧 `weight` 可能表示：

- 统计相关强度
- 模型得分
- 排名权重
- 因果强度

这些概念不可混为一个默认 Core 字段。

因此当前 primary disposition 为 `MOVE_DERIVED`。

如果未来确实需要表示 externally derived relation strength，至少需要显式记录：

- derivation method
- provenance
- source data / model
- version
- metric semantics

本轮不冻结这些字段。

---

## 8. Provenance 收敛问题

历史设计中：

- Behavior 使用 `evidence_source`
- Preference 使用 `source_type`

两者实际上指向同一类架构需求：**信息来自哪里，以及如何追踪来源。**

因此二者均归入 `REFINE`。

未来可能收敛到统一的 Evidence / Provenance / Source abstraction，但本轮不决定：

- 是一个对象还是多个对象；
- source type 是否为枚举；
- 是否允许多来源；
- 如何记录 source identifier；
- 如何表示人工标注、设备、问卷、EHR、模型推断；
- confidence 是否属于 provenance；
- 如何表示 provenance chaining。

R1A 只确认一件事：

> 来源追踪能力必须保留，但旧字段名和旧字段结构不应被直接冻结为最终方案。

---

## 9. Pathway 兼容性

旧 Treatment Pathway **不删除**。

R0 已经决定 Treatment Pathway 不属于 PBDL-Core，但这并不意味着否定历史 PBDL 的 Pathway 能力。

本轮正式使用以下兼容性表述：

```text
historical PBDL capability
        ↓
retained as candidate PBDL-Pathway extension
```

因此：

- `path_id`
- `path_node`
- `steps`
- `_guideline`
- StepObject.`action`
- StepObject.`status`
- StepObject.`outcome`

继续保留在 candidate `PBDL-Pathway` extension 中。

`path_condition` 也保留在 Pathway 语义中，但因为旧自由字符串条件需要重新设计，所以 primary disposition 为 `REFINE`。

`path_dynamic_score` 与 `_deviation_analysis` 属于外部派生结果，不应作为路径静态定义的固有字段。

这实现了：

- 历史能力连续性；
- Core 边界收敛；
- 推理结果与描述模型分离。

---

## 10. Primary disposition 统计

总字段数：**32**

| Primary disposition | 数量 |
|---|---:|
| KEEP_CORE | 8 |
| KEEP_EXTENSION | 7 |
| MOVE_DERIVED | 5 |
| REFINE | 11 |
| DEPRECATE | 1 |
| **Total** | **32** |

校验：

```text
8 + 7 + 5 + 11 + 1 = 32
```

不存在双重计数。

### KEEP_CORE — 8

1. Behavior.`behavior_type`
2. Behavior.`executor`
3. Preference.`preference_category`
4. Preference.`preference_value`
5. Preference.`note`
6. Relation.`source`
7. Relation.`target`
8. Relation.`type`

### KEEP_EXTENSION — 7

1. Treatment Path.`path_id`
2. Treatment Path.`path_node`
3. Treatment Path.`steps`
4. Treatment Path.`_guideline`
5. StepObject.`action`
6. StepObject.`status`
7. StepObject.`outcome`

### MOVE_DERIVED — 5

1. Behavior.`risk_tag`
2. Preference.`preference_conflict_flag`
3. Treatment Path.`path_dynamic_score`
4. Treatment Path.`_deviation_analysis`
5. Relation.`weight`

### REFINE — 11

1. Behavior.`temporal_scope`
2. Behavior.`behavior_trigger`
3. Behavior.`symptom_triggered`
4. Behavior.`communication_status`
5. Behavior.`evidence_source`
6. Behavior.`reasoning_note`
7. Preference.`source_type`
8. Preference.`confidence_score`
9. Preference.`associated_behavior`
10. Treatment Path.`path_condition`
11. Relation.`temporal`

### DEPRECATE — 1

1. Behavior.`validity_flag`

---

## 11. 尚未解决的 Open Questions

R1A 不解决以下问题，只将其登记为后续规范设计输入。

### OQ-001 — 统一时间模型

`temporal_scope` 与 Relation.`temporal` 是否应共享统一 temporal abstraction？

需要覆盖：

- 时间点
- 时间区间
- 频率
- 持续时间
- 顺序
- 相对时间
- 有效期

### OQ-002 — `communication_status` 的最终归属

需要判断它是：

- 最小 PBDL-Core 中普遍适用的 Context；
- 临床沟通领域扩展；
- 工作流系统状态。

### OQ-003 — 统一 Evidence / Provenance

`evidence_source` 与 `source_type` 应如何收敛？

需要明确 Evidence、Source、Provenance 三者是否分层。

### OQ-004 — Confidence 的语义归属

`confidence_score` 是否：

- 只适用于 model inference；
- 也适用于人工标注一致性；
- 属于 provenance；
- 属于 derived assertion metadata。

self-report 不应被迫具有模型式 confidence。

### OQ-005 — Trigger / Symptom 的非因果表达

`behavior_trigger` 与 `symptom_triggered` 最终应：

- 继续作为字段；
- 转为 Relation；
- 转为 Context；
- 或拆分为多种明确语义。

### OQ-006 — Preference 到 Behavior 的关联方式

`associated_behavior` 应采用：

- 专门引用字段；
- generic Relation；
- 特定 Relation type。

### OQ-007 — Pathway condition 表达

`path_condition` 未来在 PBDL-Pathway 中使用：

- 结构化 predicate；
- 受限表达式语言；
- 外部规则引用；

仍未决定。

### OQ-008 — Relation type 与 relation strength

需要分别解决：

- Relation type vocabulary；
- causal semantics 是否允许；
- externally derived strength 的单独表达；
- metric / model / provenance 的绑定方式。

### OQ-009 — Note / Annotation 收敛

Behavior.`reasoning_note` 与 Preference.`note` 是否应统一为通用 Annotation 模型？

若保留模型推理文字，必须明确其 derivation，而不是把它当成来源事实。

### OQ-010 — Pathway runtime boundary

StepObject.`status` 与 `outcome` 到底是：

- Pathway 静态描述；
- 执行实例状态；
- 外部 workflow runtime 信息；

需要在 PBDL-Pathway 设计时进一步区分。

### OQ-011 — Core identity 与 reference boundary

该问题已进入 **R1B — Core Object Boundary & Identity** 处理。

R1B 负责冻结 Subject、Behavior、Preference 与 Relation 的最小 identity / reference 规则；R1A 的 32-field disposition matrix 保持不变。

规范性结论以 `spec/PBDL-v1.0-SPEC.md` 的 R1B 更新为准。

---

## 12. Compatibility Conclusion

### 12.1 原中期 PBDL 是否被整体推翻？

**没有。**

本轮审计明确保留历史字段作为 PBDL 设计历史，并逐项寻找兼容性去向。

新版不是通过删除旧字段来建立新语言，而是把旧体系中混合在一起的描述信息、扩展能力、分析结果和校验结果拆分到更合适的架构层。

### 12.2 有多少字段仍被保留？

32 个历史字段全部保留在兼容性审计记录中，没有任何字段被从历史中删除。

其中：

- 31 个字段继续作为 Core 概念、Extension 概念、Derived artifact 或待 Refine 的有效设计概念保留；
- 只有 `validity_flag` 被标记为 DEPRECATE，但仍保留历史兼容记录，不做物理删除。

### 12.3 有多少字段只是改变所属层级？

在 primary disposition 中，有 **12 个字段**被明确放到最小 Core 之外：

- 7 个 `KEEP_EXTENSION`
- 5 个 `MOVE_DERIVED`

其中 Treatment Pathway 相关能力被保留为 candidate `PBDL-Pathway` extension，而风险、冲突、动态评分、偏离分析和 relation weight 被重新识别为外部派生结果。

此外还有 11 个 `REFINE` 字段保留其历史概念，但具体字段结构或最终架构归属尚待规范设计。

### 12.4 是否存在真正需要废弃的字段？

只有一个 primary disposition 为 `DEPRECATE`：

`Behavior.validity_flag`

原因不是该历史信息毫无价值，而是“对象是否合法”应该由 Validator 在特定规范版本和校验规则下计算，而不是由对象自己保存一个自我声明的合法性布尔值。

其替代方向是 Validator output / validation report。

### 12.5 为什么新版属于 architecture refinement，而不是 redesign from scratch？

因为新版继续保留绝大多数历史字段词汇和概念，只重新澄清它们的职责归属：

- 患者行为与偏好的基础描述进入或继续留在 Core；
- Treatment Pathway 作为历史能力保留到 extension；
- 风险、冲突、评分等结果进入 derived application layer；
- 来源、时间、关联与 trigger 等有价值但定义不足的概念进入 REFINE；
- 只有校验自描述字段 `validity_flag` 被明确建议停止新增使用。

因此，本轮结论是：

> **PBDL v1 redesign preserves the majority of the historical field vocabulary while clarifying semantic ownership between Core, extensions, and derived application results.**

这是一种 compatibility-preserving architecture refinement，而不是从零开始重建一套与历史 PBDL 无关的新语言。

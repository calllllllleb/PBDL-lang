# 变更记录

## 未发布

RC1 之后的未发布变更记录在此。

## 1.0.0rc1 - 2026-09-29

PBDL 1.0 的第一个 release candidate。Core semantics 与 runtime 已通过 final repository consistency audit；该版本仍不是 final release。

### PBDL 1.0 Core

- 建立以 Subject、Behavior、Preference 与 Relation 为核心的 PBDL document representation。
- 支持 Context、Provenance、Evidence、Annotation 与 typed references 等跨实体表示能力。
- 完成 TemporalValue / TemporalExtent、BehaviorFrequency、PreferenceValue、BehaviorFactor 等结构化值类型。
- 明确 PBDL-Core 的责任是 description / representation，而不是诊断、临床推荐、风险预测、因果推断或工作流执行。

### JSON-first 表示面

- 冻结 PBDL 1.0 normative machine interchange 为 JSON data model。
- 提供 JSON Schema Draft 2020-12 的 STRUCTURAL projection。
- 文档版本精确使用 "pbdl_version": "1.0"。
- current-version processing boundary 对不支持的 document version fail closed。
- PBDL 1.0 不定义 normative textual DSL、parser 或 CLI；现有 grammar 文件仅为 non-normative placeholder。

### Runtime

- 提供 STRUCTURAL Schema validation。
- 提供 REFERENCE resolution 与引用有效性检查。
- 提供 document-intrinsic SEMANTIC validation。
- 提供 Relation Vocabulary validation。
- 提供 semantic canonicalization。
- 提供 PBDLDocument canonical-information equality。
- 按 responsibility 保持 STRUCTURAL、REFERENCE、SEMANTIC、VOCABULARY、SOURCE-FIDELITY 与 NORMALIZATION 边界分离。

### Relation Vocabulary

- 定义 Relation Vocabulary Contract，而不是内置具体医学关系 ontology。
- Relation type identity 使用 system + code。
- 定义 directionality、causal status 与 endpoint signatures。
- 定义 vocabulary version compatibility。
- 支持 optional inverse metadata。
- PBDL-Core 当前不提供 built-in concrete medical Relation ontology；reference corpus 中的 relation codes 仅用于示例与测试。

### Conformance、Canonicalization 与 Equality

- canonicalization 定义 semantic canonical form。
- 对规范上无序的 semantic collections 使用 order-insensitive 语义。
- 纳入 provenance inheritance 的规范信息语义。
- 在 Relation vocabulary 可用时，canonical-information equality 对 Relation 使用 directionality-aware 处理。
- 在 vocabulary 不可用时，对 Relation equality 保持 conservative behavior。
- PBDL 1.0 不定义 deterministic byte-level JSON serialization、统一 object-key ordering、canonical array byte ordering 或 whitespace format。

### Reference Corpus

- 提供 structural valid / invalid reference corpus，用于验证 Draft 2020-12 Schema projection。
- 提供 full-pipeline reference corpus，覆盖跨层的 REFERENCE、SEMANTIC、VOCABULARY、NORMALIZATION 与 canonical-information equality 行为。
- reference corpus 是可执行符合性材料，不是独立规范来源。
- SOURCE-FIDELITY 需要原始来源或 producer evidence，因此不由孤立 document corpus 自动判定。

### Packaging 与 CI

- 建立 PEP 517 / PEP 621 Python package，distribution name 为 pbdl-lang。
- 本 RC 的 Python distribution version 为 1.0.0rc1，最低 Python 版本为 3.11。
- 支持构建 wheel 与 sdist。
- 构建时将唯一 canonical Schema 从 spec/schema/pbdl-v1.schema.json 注入 wheel runtime resource；仓库不维护第二份 tracked canonical Schema。
- clean-wheel smoke 验证从 repository 外部 cwd 安装并运行 public runtime。
- GitHub Actions CI 验证 Python 3.11、3.12 与 3.13，并验证 distribution build、Schema resource 与 clean installed runtime。

### PBDL 1.0 未包含（Deferred scope）

以下能力明确延后，不代表当前实现缺陷：

- normative textual DSL / parser；
- deterministic byte-level JSON serialization；
- extension mechanism；
- future cross-version migration policy；
- built-in concrete Relation ontology；
- SOURCE-FIDELITY automated validator；
- complete warning / severity / error-code standard。

这些 deferred scope 不改变当前 PBDL 1.0 已冻结的 JSON-first Core 语义与 runtime responsibility boundaries。

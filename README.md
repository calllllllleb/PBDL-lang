# PBDL-lang

**PBDL — Patient Behavior Description Language（患者行为描述语言）**

PBDL 是一种用于结构化表示患者行为、偏好及其上下文、来源和关系信息的声明式领域专用描述语言 / 数据模型。

**PBDL 1.0 的规范机器交换面是 JSON data model；规范性 textual DSL 尚未定义。**

## 当前状态

当前仓库处于 **PBDL 1.0 Final** 阶段。

已经完成并收口：

- PBDL 1.0 Core runtime；
- JSON-first release surface；
- current-version processing boundary；
- structural 与 full-pipeline reference corpus；
- Python packaging 与 installed-runtime Schema resource；
- GitHub Actions CI。

当前规范状态为 Final，Python distribution 版本为 1.0.0。项目尚未发布到 PyPI。

版本号需要区分：

~~~text
PBDL document version:
"1.0"

Python distribution version:
1.0.0
~~~

二者不是同一个版本字段。PBDL 1.0 文档中的版本仍必须写为：

~~~json
"pbdl_version": "1.0"
~~~

## PBDL 是什么

PBDL-Core 提供患者行为与偏好信息的稳定表示层，重点描述：

- Subject；
- Behavior；
- Preference；
- Relation；
- Context；
- Provenance / Evidence；
- temporal、frequency、factor、annotation 等结构化信息；
- typed references 与关系语义。

上游信息可以来自人工录入、规则系统、NLP / LLM 或其他抽取流程；PBDL 负责表示与符合性边界，而不是替上游完成信息抽取，也不替下游应用做临床判断。

## PBDL 1.0 表示边界

PBDL 1.0 当前定义的是 **JSON-first** 的规范机器表示。

~~~text
normative machine interchange
→ JSON data model

normative textual DSL
→ NOT DEFINED in PBDL 1.0
~~~

仓库中的 spec/grammar/pbdl.ebnf 是 non-normative placeholder，不代表 PBDL 1.0 已存在可用的规范文本语法、parser 或 CLI。

PBDL canonicalization 面向**语义规范形（semantic canonical form）**。PBDL 1.0 不定义 canonical JSON bytes、固定 object-key 顺序、统一 whitespace 格式或完整的 byte-level deterministic serialization。

## 规范性来源

[spec/PBDL-v1.0-SPEC.md](spec/PBDL-v1.0-SPEC.md) 是 PBDL 1.0 的**唯一规范性来源**。

其他仓库制品承担不同职责，但不会成为独立规范权威：

- [spec/schema/pbdl-v1.schema.json](spec/schema/pbdl-v1.schema.json)：JSON Schema Draft 2020-12 的 **STRUCTURAL** projection；
- [src/pbdl/](src/pbdl/)：PBDL 1.0 conformance reference Python runtime；
- [spec/examples/](spec/examples/)：structural 与 full-pipeline reference corpus；
- tests：验证规范投影与 runtime 行为的一致性。

如果 README、Schema、示例、测试或 runtime 行为与规范文本发生冲突，以规范文本为准。

## 安装

当前项目尚未发布到 PyPI。请从 repository checkout 使用。

要求：

~~~text
Python >= 3.11
~~~

开发、测试与构建环境：

~~~bash
python -m pip install -e ".[test,build]"
python -m pytest -q
python -m build
~~~

CI 当前验证 Python 3.11、3.12 和 3.13。

## Quick Start

最小结构验证：

~~~python
from pbdl import validate_document

document = {
    "pbdl_version": "1.0",
    "subjects": [{"id": "subject_1"}],
    "behaviors": [],
    "preferences": [],
    "relations": [],
}

result = validate_document(document)
assert result.valid
~~~

validate_document() 执行 STRUCTURAL validation。引用、文档内语义、Relation vocabulary 与 canonicalization 分别由对应 runtime responsibility 处理。

## Python Runtime

当前正式 public runtime API 按 processing responsibility 划分：

| Responsibility | Public API |
| --- | --- |
| **STRUCTURAL** | validate_document, is_schema_valid |
| **REFERENCE** | resolve_references, are_references_valid |
| **SEMANTIC** | validate_semantics, are_semantics_valid |
| **VOCABULARY** | RelationVocabulary, validate_relation_vocabulary, is_relation_vocabulary_valid |
| **NORMALIZATION** | canonicalize_document, is_canonical_normal_form |
| **CANONICAL-INFORMATION EQUALITY** | documents_canonically_equal |

对应的 Result / Violation / InputError 类型也作为 public API 导出；具体契约以规范与 runtime public surface 为准。

## Conformance Model

核心处理职责不是一个把所有检查混在一起的单一 validator。

~~~text
STRUCTURAL
    ↓
REFERENCE
    ↓
SEMANTIC
~~~

此外：

- **VOCABULARY**：在适用时独立验证 Relation type contract；它不是 SEMANTIC 的隐式子步骤；
- **SOURCE-FIDELITY**：需要原始来源、producer 过程或等价外部证据，孤立 PBDL document runtime 无法自动推断；
- **NORMALIZATION**：负责 semantic canonical form；
- **canonical-information equality**：比较规范信息是否等价，并在提供 Relation vocabulary 时考虑关系方向性等语义。

复杂语义与层间责任边界请直接参阅 [spec/PBDL-v1.0-SPEC.md](spec/PBDL-v1.0-SPEC.md)。

## Relation Vocabulary

PBDL 1.0 定义 **Relation Vocabulary Contract**，使 Relation type 可以机器解释其：

- identity（system + code）；
- directionality；
- causal status；
- endpoint signatures；
- version compatibility；
- optional inverse metadata。

PBDL-Core **不内置具体医学 Relation ontology**。[spec/vocabulary/relation-types.yaml](spec/vocabulary/relation-types.yaml) 当前没有内置 relation entries。

full-pipeline reference corpus 中出现的示例 relation codes 仅用于测试与示例，不属于正式 PBDL 内置词表。

## Repository Layout

- [spec/PBDL-v1.0-SPEC.md](spec/PBDL-v1.0-SPEC.md) — normative specification；
- [spec/schema/](spec/schema/) — Draft 2020-12 structural Schema；
- [spec/examples/](spec/examples/) — structural + full-pipeline reference corpus；
- [spec/vocabulary/](spec/vocabulary/) — vocabulary / Relation Vocabulary contract carrier；
- [src/pbdl/](src/pbdl/) — Python runtime；
- [tests/](tests/) — conformance 与 runtime tests；
- [.github/workflows/ci.yml](.github/workflows/ci.yml) — CI。

## Scope / Non-goals

**PBDL-Core 负责描述 / representation；外部应用负责推理与执行。**

PBDL-Core 本身不承担：

- 临床诊断或治疗推荐；
- 临床决策支持；
- 风险预测；
- 因果推断；
- 工作流执行；
- LLM reasoning。

当前仓库不宣称 PBDL 已经过临床有效性验证，也不将其描述为医疗器械、FHIR replacement 或完整临床生产系统。

当前实现是 PBDL 1.0 规范的参考 Python runtime；是否适用于具体生产或临床环境，需要由使用方基于自身需求、风险和验证要求独立评估。

## License

PBDL-lang is licensed under the [Apache License, Version 2.0](LICENSE).

## Specification

规范入口：

[spec/PBDL-v1.0-SPEC.md](spec/PBDL-v1.0-SPEC.md)

README 只用于项目定位与使用导引，不重新定义 PBDL 1.0 规范语义。

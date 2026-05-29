# SkillCI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-48%20passed-brightgreen.svg)](#测试)
[![Ruff](https://img.shields.io/badge/Lint-Ruff-brightgreen.svg)](https://docs.astral.sh/ruff/)
[![Release](https://img.shields.io/badge/release-v0.1.0-orange.svg)](https://github.com/your-username/skillci/releases)

[English](README.md) | 中文

**在发布前测试和回归检查你的 Agent Skills。**

Agent Skills 正在成为可复用的软件资产，但大多数 Skill 在发布前没有任何测试。SkillCI 帮助你在发布前检查结构、资源引用、风险命令和触发行为。

---

## 为什么需要 SkillCI

随着 Claude Skills、OpenAI Codex Skills、GitHub `gh skill`、AGENTS.md 等 Agent 工作流资产逐渐普及，AI Agent 的能力复用方式正在从"写 Prompt"转向"维护可复用 Skill"。

但当前 Skill 生态仍处于早期阶段，开发者主要面临以下问题：

- **Skill 写完后无法判断是否真的有效** — 只能靠人工试几条 Prompt，缺少标准化测试方法
- **Skill 修改后容易产生行为回归** — 修改 `SKILL.md` 后，可能导致原本能触发的任务不再触发
- **Skill 质量缺少工程化门禁** — 没有 lint、测试、回归、报告和 CI 检查
- **Skill 逐渐成为团队资产，但缺少维护工具** — 会出现描述过宽、重复能力、资源引用失效等问题

SkillCI 的目标是：**让 Agent Skills 像代码一样可以被测试、回归检查和持续集成。**

---

## 检查能力

### 静态健康检查

| 检查项 | 严重级别 | 说明 |
|--------|---------|------|
| `SKILL.md` 不存在 | error | Skill 目录下缺少 SKILL.md |
| frontmatter 非法 | error | YAML frontmatter 解析失败 |
| 缺少 name | error | frontmatter 中无 name 字段 |
| 缺少 description | error | frontmatter 中无 description 字段 |
| description 过短 | warning | 单词数 < 8 |
| description 过长 | warning | 单词数 > 80 或字符数 > 500 |
| description 过宽 | warning | 包含泛化词，如"所有任务"、"通用" |
| 缺少触发边界 | warning | 没有说明何时应该使用该 Skill |
| 引用文件不存在 | error | SKILL.md 中引用的文件不存在 |
| 危险命令 | warning | 包含 `rm -rf`、`sudo` 等危险命令 |
| 敏感路径 | warning | 引用 `.ssh`、`.env` 等敏感路径 |

### 触发测试

- **本地模式**：基于规则的评分，使用 description 相似度、关键词覆盖率、领域词、标题、标签 5 个维度加权计算
- **LLM 模式**：调用 LLM 判断 Skill 是否应该在给定任务中触发
- **回归对比**：与保存的基线快照对比，检测行为变化

---

## 快速开始

```bash
# 安装
pip install -e .[dev]

# 静态检查
skillci lint examples/api-doc-writer

# 本地触发测试
skillci test examples/api-doc-writer --mode local

# LLM 触发测试（mock）
skillci test examples/api-doc-writer --mode llm --provider mock

# 保存基线快照
skillci snapshot examples/api-doc-writer

# 与基线对比
skillci test examples/api-doc-writer --mode local --compare latest

# 生成 Markdown 报告
skillci report examples/api-doc-writer --format markdown --output report.md
```

---

## 示例 SKILL.md

```markdown
---
name: api-doc-writer
description: Use this skill when the user asks to generate, refine, or validate
  API documentation from backend routes, controllers, request and response models,
  or OpenAPI specifications.
---

# API Doc Writer

This skill helps generate API documentation from backend source code,
including Spring Boot controllers, FastAPI routes, REST endpoints,
request DTOs, response schemas, and OpenAPI specifications.

## When to use

Use this skill for:
- Generating OpenAPI documentation
- Writing REST API docs
- Converting backend routes into API specs

## References

See `references/openapi-style-guide.md`.
```

---

## 示例 skillci.yaml

```yaml
skill: .
mode: local

judge:
  provider: openai
  base_url: https://your-api.com/v1
  model: gpt-4o-mini
  temperature: 0
  timeout: 30

thresholds:
  trigger_score: 0.45
  trigger_f1: 0.8
  llm_confidence: 0.7

cases:
  - name: should_trigger_for_spring_controller
    input: 根据这个 Spring Controller 生成 OpenAPI 文档
    expected_trigger: true
    tags: [api, spring, openapi]

  - name: should_trigger_for_fastapi_routes
    input: 把这些 FastAPI 路由整理成接口说明
    expected_trigger: true
    tags: [api, fastapi, documentation]

  - name: should_not_trigger_for_sql_optimization
    input: 帮我优化这个 SQL 查询
    expected_trigger: false
    tags: [sql, database]

  - name: should_not_trigger_for_css_explanation
    input: 解释一下这个 CSS 样式
    expected_trigger: false
    tags: [frontend, css]
```

---

## 示例输出

### 本地触发测试

```
$ skillci test examples/api-doc-writer --mode local

SkillCI Report: api-doc-writer
Static Health
  OK no issues found

Trigger Check
  PASS should_trigger_for_spring_controller: expected=True, actual=True, score=0.4786
    matched_terms: api, controller, openapi, spring, 文档
  PASS should_trigger_for_fastapi_routes: expected=True, actual=True, score=0.57
    matched_terms: api, documentation, fastapi
  PASS should_not_trigger_for_sql_optimization: expected=False, actual=False, score=0.0
    matched_terms: none
  PASS should_not_trigger_for_css_explanation: expected=False, actual=False, score=0.0
    matched_terms: none

Summary
  Local Precision: 1.0
  Local Recall: 1.0
  Local F1: 1.0
  Local Accuracy: 1.0

Result
  passed
```

### LLM 触发测试

```
$ skillci test examples/api-doc-writer --mode llm --provider mock

SkillCI Report: api-doc-writer
Static Health
  OK no issues found

LLM Trigger Check
  PASS should_trigger_for_spring_controller: expected=True, actual=True, confidence=0.92
    reason: mock judge returned expected result
  PASS should_trigger_for_fastapi_routes: expected=True, actual=True, confidence=0.92
    reason: mock judge returned expected result
  PASS should_not_trigger_for_sql_optimization: expected=False, actual=False, confidence=0.88
    reason: mock judge returned expected result
  PASS should_not_trigger_for_css_explanation: expected=False, actual=False, confidence=0.88
    reason: mock judge returned expected result

LLM Summary
  LLM Precision: 1.0
  LLM Recall: 1.0
  LLM F1: 1.0
  LLM Accuracy: 1.0
  Average Confidence: 0.9

Result
  passed
```

### 回归测试

```
$ skillci test examples/api-doc-writer --mode local --compare latest

Regression Report
  Baseline: .skillci/baselines/api-doc-writer/latest.json
  Total cases: 4
  Unchanged: 4
  Regressed: 0
  Improved: 0
  No behavior changes detected.
```

---

## CLI 命令

| 命令 | 说明 |
|------|------|
| `skillci init <path>` | 为 Skill 目录生成 `skillci.yaml` 配置 |
| `skillci lint <path>` | 执行静态健康检查 |
| `skillci test <path> --mode local` | 运行本地触发测试 |
| `skillci test <path> --mode llm --provider openai` | 运行 LLM 触发测试 |
| `skillci test <path> --mode llm --provider mock` | 运行 LLM 测试（mock） |
| `skillci test <path> --json` | 输出 JSON 报告 |
| `skillci test <path> --compare latest` | 与基线快照对比 |
| `skillci snapshot <path>` | 保存基线快照 |
| `skillci report <path> --format markdown` | 生成 Markdown 报告 |

---

## 配置

### skillci.yaml

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `skill` | string | `.` | Skill 目录路径 |
| `mode` | string | `local` | 测试模式：`local`、`llm`、`both` |
| `judge.provider` | string | `openai` | LLM 提供商 |
| `judge.base_url` | string | `null` | 自定义 API 地址 |
| `judge.model` | string | `gpt-4.1-mini` | 模型名称 |
| `judge.temperature` | float | `0` | 温度参数 |
| `judge.timeout` | int | `30` | 超时秒数 |
| `thresholds.trigger_score` | float | `0.6` | 本地触发阈值 |
| `thresholds.trigger_f1` | float | `0.8` | F1 通过阈值 |
| `thresholds.llm_confidence` | float | `0.7` | LLM 置信度阈值 |
| `cases[].name` | string | 必填 | 测试用例名称 |
| `cases[].input` | string | 必填 | 用户输入 |
| `cases[].expected_trigger` | bool | 必填 | 期望是否触发 |
| `cases[].tags` | list | `[]` | 标签 |

### 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI 兼容 API 的密钥 |
| `OPENAI_BASE_URL` | 默认 API 地址（被 `judge.base_url` 覆盖） |

### 本地配置覆盖

如果你不想把敏感配置（如 API 密钥）提交到版本控制，可以在 `skillci.yaml` 同目录下创建 `skillci.local.yaml` 文件。它会自动加载并覆盖对应字段，且默认被 gitignore。

```yaml
# skillci.local.yaml（不提交）
judge:
  provider: openai
  base_url: https://your-api.com/v1
  model: your-model-name
```

本地配置会覆盖 `skillci.yaml` 中的同名字段，不需要修改任何命令，自动生效。

### LLM 模式配置

安装可选依赖：

```bash
pip install -e .[llm]
```

在 `skillci.yaml` 中配置：

```yaml
judge:
  provider: openai
  base_url: https://your-api.com/v1
  model: your-model-name
```

或使用环境变量：

```bash
set OPENAI_API_KEY=your-key
set OPENAI_BASE_URL=https://your-api.com/v1
```

---

## 测试

```bash
pip install -e .[dev]
python -m pytest -v
ruff check .
```

当前状态：**48 个测试通过**，**ruff 检查通过**。

---

## 当前限制

- **`both` 模式尚未实现** — 目前只支持 `local` 和 `llm` 模式
- **Judge 缓存尚未实现** — LLM 结果不会缓存，每次运行都会调用 API
- **LLM 置信度是模型自报的** — 不是基于 logprobs 或多次运行的一致性
- **本地触发评分是启发式的** — 基于词覆盖率，不是语义理解
- **中文分词是字符级的** — 没有使用分词库
- **只支持 OpenAI 兼容 API** — Anthropic、Gemini、本地模型（Ollama）计划后续支持

---

## 后续计划

- Anthropic / Gemini / Ollama Provider 支持
- 基于 logprobs 的置信度
- 多次运行取一致（`--runs N`）
- Judge 缓存
- Both 模式（local + LLM 对比）
- HTML 报告
- GitHub Action
- Skill Health Score
- 批量测试（多个 Skill）

---

## 许可证

Apache-2.0

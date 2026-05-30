# SkillCI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-48%20passed-brightgreen.svg)](#testing)
[![Ruff](https://img.shields.io/badge/Lint-Ruff-brightgreen.svg)](https://docs.astral.sh/ruff/)
[![Release](https://img.shields.io/badge/release-v0.1.2-orange.svg)](https://github.com/your-username/skillci/releases)

English | [中文](README_zh.md)

**Test and regression-check your Agent Skills before shipping.**

Agent Skills are becoming reusable software assets, but most skills are shipped without tests. SkillCI helps you check structure, resource references, risky commands, and trigger behavior before publishing a Skill.

---

## Why SkillCI

随着 Claude Skills、OpenAI Codex Skills、GitHub `gh skill`、AGENTS.md 等 Agent 工作流资产逐渐普及，AI Agent 的能力复用方式正在从"写 Prompt"转向"维护可复用 Skill"。

但当前 Skill 生态仍处于早期阶段，开发者主要面临以下问题：

- **Skill 写完后无法判断是否真的有效** — 只能靠人工试几条 Prompt
- **Skill 修改后容易产生行为回归** — 原本能触发的任务不再触发
- **Skill 质量缺少工程化门禁** — 没有 lint、测试、回归、报告和 CI 检查
- **Skill 逐渐成为团队资产，但缺少维护工具**

SkillCI 的目标是：**让 Agent Skills 像代码一样可以被测试、回归检查和持续集成。**

---

## What It Checks

### Static Health Checks

| Check | Severity | Description |
|-------|----------|-------------|
| `SKILL.md` missing | error | No SKILL.md in skill directory |
| Invalid frontmatter | error | YAML frontmatter parse failure |
| Missing name | error | No `name` in frontmatter |
| Missing description | error | No `description` in frontmatter |
| Description too short | warning | Word count < 8 |
| Description too long | warning | Word count > 80 or chars > 500 |
| Description too broad | warning | Contains generic phrases like "all tasks" |
| Missing scope hints | warning | No "when to use" indicators |
| Broken reference | error | Referenced file does not exist |
| Dangerous command | warning | Contains risky commands like `rm -rf` |
| Sensitive path | warning | References sensitive paths like `.ssh` |

### Trigger Testing

- **Local mode**: Rule-based scoring using description similarity, keyword overlap, domain terms, headings, and tags
- **LLM mode**: Calls an LLM to judge whether the Skill should trigger for each test case
- **Regression**: Compares current results against a saved baseline to detect behavior changes

---

## Quick Start

```bash
# Install
pip install -e .[dev]

# Lint a skill
skillci lint examples/api-doc-writer

# Run local trigger test
skillci test examples/api-doc-writer --mode local

# Run LLM trigger test (mock)
skillci test examples/api-doc-writer --mode llm --provider mock

# Save baseline snapshot
skillci snapshot examples/api-doc-writer

# Compare with baseline
skillci test examples/api-doc-writer --mode local --compare latest

# Generate markdown report
skillci report examples/api-doc-writer --format markdown --output report.md
```

---

## Example SKILL.md

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

## Example skillci.yaml

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

## Example Output

### Local Trigger Test

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

### LLM Trigger Test

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

### Regression Test

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

## CLI Commands

| Command | Description |
|---------|-------------|
| `skillci init <path>` | Generate a starter `skillci.yaml` for a Skill directory |
| `skillci lint <path>` | Run static health checks |
| `skillci test <path> --mode local` | Run local trigger test |
| `skillci test <path> --mode llm --provider openai` | Run LLM trigger test |
| `skillci test <path> --mode llm --provider mock` | Run LLM test with mock provider |
| `skillci test <path> --json` | Output JSON report |
| `skillci test <path> --compare latest` | Compare with baseline snapshot |
| `skillci snapshot <path>` | Save baseline snapshot |
| `skillci report <path> --format markdown` | Generate markdown report |

---

## Configuration

### skillci.yaml

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `skill` | string | `.` | Skill directory path |
| `mode` | string | `local` | Test mode: `local`, `llm`, `both` |
| `judge.provider` | string | `openai` | LLM provider |
| `judge.base_url` | string | `null` | Custom API endpoint |
| `judge.api_key` | string | `null` | API key, overrides `OPENAI_API_KEY` when set |
| `judge.model` | string | `gpt-4.1-mini` | Model name |
| `judge.temperature` | float | `0` | Temperature |
| `judge.timeout` | int | `30` | Timeout in seconds |
| `thresholds.trigger_score` | float | `0.6` | Local trigger threshold |
| `thresholds.trigger_f1` | float | `0.8` | F1 pass threshold |
| `thresholds.llm_confidence` | float | `0.7` | LLM confidence threshold |
| `cases[].name` | string | required | Test case name |
| `cases[].input` | string | required | User input |
| `cases[].expected_trigger` | bool | required | Expected trigger result |
| `cases[].tags` | list | `[]` | Tags for the case |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | API key for OpenAI-compatible LLM providers |
| `OPENAI_BASE_URL` | Default API endpoint (overridden by `judge.base_url`) |

### Local Config Override

If you want to keep sensitive settings (like API keys) out of version control, create a `skillci.local.yaml` file in the same directory as `skillci.yaml`. It will be automatically loaded and merged, but is gitignored by default.

```yaml
# skillci.local.yaml (not committed)
judge:
  provider: openai
  api_key: sk-...
  base_url: https://your-api.com/v1
  model: your-model-name
```

The local config overrides any matching fields in `skillci.yaml`. You don't need to change any commands — it loads automatically.

**API key priority:** `judge.api_key` in `skillci.local.yaml` > `judge.api_key` in `skillci.yaml` > `OPENAI_API_KEY`

### LLM Mode

To use LLM mode, install the optional dependency:

```bash
pip install -e .[llm]
```

Then configure the judge section in `skillci.yaml`:

```yaml
judge:
  provider: openai
  base_url: https://your-api.com/v1
  model: your-model-name
```

Or use environment variables:

```bash
export OPENAI_API_KEY=your-key
export OPENAI_BASE_URL=https://your-api.com/v1
```

---

## Testing

```bash
pip install -e .[dev]
python -m pytest -v
ruff check .
```

Current status: **48 tests passing**, **ruff clean**.

---

## Current Limitations

- **`both` mode is planned** — currently only `local` and `llm` modes are supported
- **Judge cache is planned** — LLM results are not cached yet, each run calls the API
- **LLM confidence is self-reported** — the confidence score comes from the model, not from logprobs or multi-run consensus
- **Local trigger scoring is heuristic** — based on word coverage, not semantic understanding
- **Chinese tokenization is character-level** — no word segmentation library is used
- **Only OpenAI-compatible API is supported** — Anthropic, Gemini, and local models (Ollama) are planned

---

## Roadmap

- Anthropic / Gemini / Ollama provider support
- logprobs-based confidence
- Multi-run consistency check (`--runs N`)
- Judge cache
- Both mode (local + LLM comparison)
- HTML report
- GitHub Action
- Skill Health Score
- Batch testing (multiple skills)

---

## License

Apache-2.0

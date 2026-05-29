# SkillCI

Test and regression-check your Agent Skills before shipping.

SkillCI 是一个轻量 CLI，用于在 Agent Skill 发布前进行质量检查、触发测试、回归对比和报告输出。

## Why SkillCI

Agent Skills 正在成为可复用的软件资产，但大多数 Skill 在发布前没有测试。SkillCI 帮助你在合并或发布前检查结构、资源引用、风险命令、触发准确性和版本回归。

## Quick Start

```bash
pip install -e .[dev]

skillci init examples/api-doc-writer
skillci lint examples/api-doc-writer
skillci test examples/api-doc-writer --mode local
skillci test examples/api-doc-writer --mode llm --provider mock
skillci snapshot examples/api-doc-writer
skillci test examples/api-doc-writer --mode local --compare latest
skillci report examples/api-doc-writer --format markdown --output report.md
```

## v0.1 Release Scope

Implemented:

- `SKILL.md` parser
- `skillci.yaml` parser
- `skillci init`
- static health checks
- local trigger evaluator
- LLM trigger judge
- terminal report
- JSON report
- Markdown report
- snapshot baseline
- regression compare

Planned after v0.1:

- HTML report
- GitHub Action
- judge cache
- both mode comparison

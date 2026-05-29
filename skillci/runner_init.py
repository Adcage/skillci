from pathlib import Path

from skillci.parser.skill_parser import parse_skill

DEFAULT_CONFIG_TEMPLATE = """\
skill: .
mode: local
thresholds:
  trigger_score: 0.45
  trigger_f1: 0.8
  llm_confidence: 0.7
cases:
  - name: should_trigger_for_example
    input: {default_input}
    expected_trigger: true
    tags: [{default_tag}]
  - name: should_not_trigger_for_unrelated_task
    input: 帮我优化这个 SQL 查询
    expected_trigger: false
    tags: [sql, database]
"""


def run_init(skill_path: Path) -> Path:
    skill_path = skill_path.resolve()
    skill = parse_skill(skill_path)
    config_path = skill_path / "skillci.yaml"

    if config_path.exists():
        return config_path

    default_input = f"请基于 {skill.name} 生成相关文档"
    default_tag = skill.name.replace("-", " ").split()[0] if skill.name else "skill"

    content = DEFAULT_CONFIG_TEMPLATE.format(
        default_input=default_input,
        default_tag=default_tag,
    )
    config_path.write_text(content, encoding="utf-8")
    return config_path

from pathlib import Path

from skillci.lint.runner import run_static_health_checks
from skillci.parser.skill_parser import parse_skill
from skillci.schema.result import Severity


def test_example_skill_has_no_errors():
    skill = parse_skill(Path("examples/api-doc-writer"))
    result = run_static_health_checks(skill)

    assert result.passed is True
    assert not [issue for issue in result.issues if issue.severity == Severity.error]


def test_broken_reference_is_error(tmp_path):
    skill_dir = tmp_path / "broken-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: broken\n"
        "description: Generate API docs from backend controllers and OpenAPI specs.\n"
        "---\n"
        "# Broken\n"
        "See `references/missing.md`.\n",
        encoding="utf-8",
    )

    skill = parse_skill(skill_dir)
    result = run_static_health_checks(skill)

    assert result.passed is False
    assert any(issue.code == "broken_reference" for issue in result.issues)

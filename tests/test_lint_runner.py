from pathlib import Path

import pytest

from skillci.lint.runner import run_static_health_checks
from skillci.parser.skill_parser import SkillParseError, parse_skill
from skillci.schema.result import Severity


def _make_skill(tmp_path, content):
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return parse_skill(skill_dir)


def test_example_skill_has_no_errors():
    skill = parse_skill(Path("examples/api-doc-writer"))
    result = run_static_health_checks(skill)

    assert result.passed is True
    assert not [issue for issue in result.issues if issue.severity == Severity.error]


# --- SKILL.md 存在性检查 ---

def test_missing_skill_md_is_error(tmp_path):
    with pytest.raises(SkillParseError, match="SKILL.md not found"):
        parse_skill(tmp_path)


# --- frontmatter 检查 ---

def test_invalid_frontmatter_is_error(tmp_path):
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "no frontmatter here\n"
        "# Just body\n",
        encoding="utf-8",
    )

    with pytest.raises(SkillParseError, match="Invalid or missing frontmatter"):
        parse_skill(skill_dir)


def test_missing_name_is_error(tmp_path):
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "description: Generate API docs.\n"
        "---\n"
        "# Demo\n",
        encoding="utf-8",
    )

    with pytest.raises(SkillParseError, match="Missing required frontmatter field: name"):
        parse_skill(skill_dir)


def test_missing_description_is_error(tmp_path):
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: demo\n"
        "---\n"
        "# Demo\n",
        encoding="utf-8",
    )

    with pytest.raises(SkillParseError, match="Missing required frontmatter field: description"):
        parse_skill(skill_dir)


# --- description_too_short ---

def test_description_too_short(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: short-desc\n"
        "description: Too short.\n"
        "---\n"
        "# Short\n",
    )

    result = run_static_health_checks(skill)

    assert result.passed is True
    assert any(issue.code == "description_too_short" for issue in result.issues)


def test_description_long_enough(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: good-desc\n"
        "description: Generate OpenAPI documentation from backend Spring Boot controllers.\n"
        "---\n"
        "# Good\n",
    )

    result = run_static_health_checks(skill)

    assert not any(issue.code == "description_too_short" for issue in result.issues)


# --- description_too_long ---

def test_description_too_long(tmp_path):
    long_desc = "Generate API documentation from backend controllers. " * 20
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: long-desc\n"
        f"description: {long_desc}\n"
        "---\n"
        "# Long\n",
    )

    result = run_static_health_checks(skill)

    assert any(issue.code == "description_too_long" for issue in result.issues)


def test_description_not_too_long(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: normal-desc\n"
        "description: Generate OpenAPI documentation from backend Spring Boot controllers.\n"
        "---\n"
        "# Normal\n",
    )

    result = run_static_health_checks(skill)

    assert not any(issue.code == "description_too_long" for issue in result.issues)


# --- description_too_broad ---

def test_description_too_broad(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: broad-skill\n"
        "description: This skill helps with all tasks and general purpose work for anything.\n"
        "---\n"
        "# Broad\n",
    )

    result = run_static_health_checks(skill)

    broad_issues = [issue for issue in result.issues if issue.code == "description_too_broad"]
    assert len(broad_issues) == 1
    assert "all tasks" in broad_issues[0].message
    assert "general purpose" in broad_issues[0].message
    assert "anything" in broad_issues[0].message


def test_description_not_broad(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: narrow-skill\n"
        "description: Generate OpenAPI documentation from backend Spring Boot controllers.\n"
        "---\n"
        "# Narrow\n",
    )

    result = run_static_health_checks(skill)

    assert not any(issue.code == "description_too_broad" for issue in result.issues)


# --- description_missing_scope ---

def test_description_missing_scope(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: no-scope\n"
        "description: Generate OpenAPI documentation and REST API specs and endpoint schemas.\n"
        "---\n"
        "# No Scope\n",
    )

    result = run_static_health_checks(skill)

    assert any(issue.code == "description_missing_scope" for issue in result.issues)


def test_description_has_scope(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: has-scope\n"
        "description: Generate OpenAPI documentation from backend Spring Boot controllers.\n"
        "---\n"
        "# Has Scope\n",
    )

    result = run_static_health_checks(skill)

    assert not any(issue.code == "description_missing_scope" for issue in result.issues)


def test_description_has_scope_chinese(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: chinese-scope\n"
        "description: 根据用户输入的后端代码生成 OpenAPI 文档。\n"
        "---\n"
        "# Chinese Scope\n",
    )

    result = run_static_health_checks(skill)

    assert not any(issue.code == "description_missing_scope" for issue in result.issues)


# --- broken_reference ---

def test_broken_reference_is_error(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: broken\n"
        "description: Generate API docs from backend controllers and OpenAPI specs.\n"
        "---\n"
        "# Broken\n"
        "See `references/missing.md`.\n",
    )

    result = run_static_health_checks(skill)

    assert result.passed is False
    assert any(issue.code == "broken_reference" for issue in result.issues)


def test_valid_reference_no_error(tmp_path):
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: ok-skill\n"
        "description: Generate API docs from backend controllers and OpenAPI specs.\n"
        "---\n"
        "# OK\n"
        "See `references/guide.md`.\n",
        encoding="utf-8",
    )
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")

    skill = parse_skill(skill_dir)
    result = run_static_health_checks(skill)

    assert result.passed is True
    assert not any(issue.code == "broken_reference" for issue in result.issues)


# --- dangerous_command ---

def test_dangerous_command(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: risky\n"
        "description: Generate API docs from backend controllers and OpenAPI specs.\n"
        "---\n"
        "# Risky\n"
        "Run `sudo rm -rf /tmp/cache`.\n",
    )

    result = run_static_health_checks(skill)

    assert any(issue.code == "dangerous_command" for issue in result.issues)
    messages = [issue.message for issue in result.issues if issue.code == "dangerous_command"]
    assert any("rm -rf" in msg for msg in messages)
    assert any("sudo" in msg for msg in messages)


def test_no_dangerous_command(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: safe\n"
        "description: Generate API docs from backend controllers and OpenAPI specs.\n"
        "---\n"
        "# Safe\n"
        "Just read files and generate documentation.\n",
    )

    result = run_static_health_checks(skill)

    assert not any(issue.code == "dangerous_command" for issue in result.issues)


# --- sensitive_path ---

def test_sensitive_path(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: leaky\n"
        "description: Generate API docs from backend controllers and OpenAPI specs.\n"
        "---\n"
        "# Leaky\n"
        "Read `~/.ssh/id_rsa` and `.env` for config.\n",
    )

    result = run_static_health_checks(skill)

    assert any(issue.code == "sensitive_path" for issue in result.issues)
    messages = [issue.message for issue in result.issues if issue.code == "sensitive_path"]
    assert any("~/.ssh" in msg for msg in messages)
    assert any(".env" in msg for msg in messages)


def test_no_sensitive_path(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: clean\n"
        "description: Generate API docs from backend controllers and OpenAPI specs.\n"
        "---\n"
        "# Clean\n"
        "Read openapi.yaml and generate docs.\n",
    )

    result = run_static_health_checks(skill)

    assert not any(issue.code == "sensitive_path" for issue in result.issues)


# --- 多个问题同时存在 ---

def test_multiple_issues_combined(tmp_path):
    skill = _make_skill(
        tmp_path,
        "---\n"
        "name: bad\n"
        "description: general purpose\n"
        "---\n"
        "# Bad\n"
        "See `references/missing.md`.\n"
        "Run `chmod 777` and read `id_rsa`.\n",
    )

    result = run_static_health_checks(skill)

    codes = [issue.code for issue in result.issues]
    assert "description_too_broad" in codes
    assert "description_too_short" in codes
    assert "description_missing_scope" in codes
    assert "broken_reference" in codes
    assert "dangerous_command" in codes
    assert "sensitive_path" in codes
    assert result.passed is False

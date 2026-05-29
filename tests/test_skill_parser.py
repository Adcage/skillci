from pathlib import Path

import pytest

from skillci.parser.skill_parser import SkillParseError, parse_skill


def test_parse_example_skill():
    skill = parse_skill(Path("examples/api-doc-writer"))

    assert skill.name == "api-doc-writer"
    assert "API documentation" in skill.description
    assert "API Doc Writer" in skill.headings
    assert Path("references/openapi-style-guide.md") in skill.references


def test_parse_skill_missing_skill_md(tmp_path):
    with pytest.raises(SkillParseError, match="SKILL.md not found"):
        parse_skill(tmp_path)

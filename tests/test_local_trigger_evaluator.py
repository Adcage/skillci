from pathlib import Path

from skillci.evaluator.local_trigger_evaluator import evaluate_local_trigger
from skillci.parser.config_parser import parse_config
from skillci.parser.skill_parser import parse_skill
from skillci.schema.config import SkillTestCase, ThresholdConfig
from skillci.schema.skill import Skill


def test_api_doc_case_triggers_and_sql_case_does_not_trigger():
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))

    api_case = config.cases[0]
    sql_case = config.cases[2]

    api_result = evaluate_local_trigger(skill, api_case, config.thresholds)
    sql_result = evaluate_local_trigger(skill, sql_case, config.thresholds)

    assert api_result.actual_trigger is True
    assert api_result.passed is True
    assert "api" in api_result.matched_terms
    assert sql_result.actual_trigger is False
    assert sql_result.passed is True


def test_evaluate_local_trigger_result_fields():
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    result = evaluate_local_trigger(skill, case, config.thresholds)

    assert result.case_name == case.name
    assert isinstance(result.expected_trigger, bool)
    assert isinstance(result.actual_trigger, bool)
    assert 0 <= result.trigger_score <= 1
    assert isinstance(result.passed, bool)
    assert result.reason
    assert isinstance(result.matched_terms, list)
    assert isinstance(result.missing_terms, list)


def test_evaluate_local_trigger_high_score_triggers():
    skill = Skill(
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
        name="api-doc",
        description="Generate API documentation from routes and controllers",
        body="api openapi swagger rest controller route",
    )
    case = SkillTestCase(
        name="api-case",
        input="generate API documentation",
        expected_trigger=True,
    )
    thresholds = ThresholdConfig(trigger_score=0.3)

    result = evaluate_local_trigger(skill, case, thresholds)

    assert result.actual_trigger is True
    assert result.trigger_score >= 0.3


def test_evaluate_local_trigger_low_score_does_not_trigger():
    skill = Skill(
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
        name="css-helper",
        description="Help with CSS styling",
        body="css style layout",
    )
    case = SkillTestCase(
        name="sql-case",
        input="optimize SQL query",
        expected_trigger=False,
    )
    thresholds = ThresholdConfig(trigger_score=0.6)

    result = evaluate_local_trigger(skill, case, thresholds)

    assert result.actual_trigger is False
    assert result.trigger_score < 0.6


def test_evaluate_local_trigger_threshold_boundary():
    skill = Skill(
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
        name="test",
        description="test description",
        body="test body",
    )
    case = SkillTestCase(
        name="case",
        input="test input",
        expected_trigger=True,
    )

    thresholds_low = ThresholdConfig(trigger_score=0.0)
    result_low = evaluate_local_trigger(skill, case, thresholds_low)
    assert result_low.actual_trigger is True

    thresholds_high = ThresholdConfig(trigger_score=1.0)
    result_high = evaluate_local_trigger(skill, case, thresholds_high)
    assert result_high.actual_trigger is False


def test_evaluate_local_trigger_domain_terms():
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    result = evaluate_local_trigger(skill, case, config.thresholds)

    assert len(result.matched_terms) > 0


def test_evaluate_local_trigger_empty_skill():
    skill = Skill(
        path=Path("."),
        skill_md_path=Path("./SKILL.md"),
        name="empty",
        description="",
        body="",
    )
    case = SkillTestCase(
        name="case",
        input="test input",
        expected_trigger=False,
    )
    thresholds = ThresholdConfig(trigger_score=0.5)

    result = evaluate_local_trigger(skill, case, thresholds)

    assert result.actual_trigger is False
    assert result.trigger_score < 0.5

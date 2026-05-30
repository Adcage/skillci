from pathlib import Path

from skillci.schema.config import RunMode, SkillCIConfig, SkillTestCase
from skillci.schema.result import (
    JudgeDisagreement,
    LintIssue,
    LLMTriggerResult,
    LocalTriggerResult,
    Severity,
    StaticHealthResult,
    TriggerMetrics,
)
from skillci.schema.skill import Skill


def test_skill_model_defaults():
    skill = Skill(
        path=Path("examples/api-doc-writer"),
        skill_md_path=Path("examples/api-doc-writer/SKILL.md"),
        name="api-doc-writer",
        description="Generate API documentation from backend routes and controllers.",
    )

    assert skill.body == ""
    assert skill.headings == []
    assert skill.references == []


def test_config_model_defaults_to_local_mode():
    config = SkillCIConfig(
        skill=Path("examples/api-doc-writer"),
        cases=[SkillTestCase(name="case", input="generate OpenAPI docs", expected_trigger=True)],
    )

    assert config.mode == RunMode.local
    assert config.thresholds.trigger_score == 0.6


def test_result_model_values():
    result = LocalTriggerResult(
        case_name="case",
        expected_trigger=True,
        actual_trigger=True,
        trigger_score=0.82,
        passed=True,
        reason="matched API documentation terms",
        matched_terms=["api", "documentation"],
    )
    metrics = TriggerMetrics(true_positive=1, precision=1, recall=1, f1=1, accuracy=1)

    assert result.passed is True
    assert metrics.f1 == 1
    assert Severity.error == "error"


def test_llm_trigger_result_defaults():
    result = LLMTriggerResult(
        case_name="case",
        expected_trigger=True,
        actual_trigger=False,
        confidence=0.8,
        passed=False,
        reason="judge said no",
    )

    assert result.error is None
    assert result.raw_response is None


def test_judge_disagreement_model():
    disagreement = JudgeDisagreement(
        case_name="test-case",
        expected_trigger=True,
        local_actual=True,
        llm_actual=False,
        local_score=0.85,
        llm_confidence=0.72,
        reason="local matched but LLM disagreed",
    )

    assert disagreement.case_name == "test-case"
    assert disagreement.expected_trigger is True
    assert disagreement.local_actual is True
    assert disagreement.llm_actual is False
    assert disagreement.local_score == 0.85
    assert disagreement.llm_confidence == 0.72
    assert disagreement.reason == "local matched but LLM disagreed"


def test_judge_disagreement_with_llm_actual_none():
    disagreement = JudgeDisagreement(
        case_name="error-case",
        expected_trigger=True,
        local_actual=True,
        llm_actual=None,
    )

    assert disagreement.llm_actual is None
    assert disagreement.local_score is None
    assert disagreement.llm_confidence is None
    assert disagreement.reason is None


def test_judge_disagreement_minimal_fields():
    disagreement = JudgeDisagreement(
        case_name="minimal",
        expected_trigger=False,
        local_actual=False,
        llm_actual=True,
    )

    assert disagreement.case_name == "minimal"
    assert disagreement.expected_trigger is False
    assert disagreement.local_actual is False
    assert disagreement.llm_actual is True


def test_llm_trigger_result_with_all_fields():
    result = LLMTriggerResult(
        case_name="full",
        expected_trigger=True,
        actual_trigger=True,
        confidence=0.95,
        passed=True,
        reason="matched",
        raw_response='{"should_trigger": true}',
    )

    assert result.case_name == "full"
    assert result.expected_trigger is True
    assert result.actual_trigger is True
    assert result.confidence == 0.95
    assert result.passed is True
    assert result.reason == "matched"
    assert result.raw_response == '{"should_trigger": true}'
    assert result.error is None


def test_llm_trigger_result_with_error():
    result = LLMTriggerResult(
        case_name="error-case",
        expected_trigger=True,
        actual_trigger=None,
        confidence=None,
        passed=False,
        error="API timeout",
    )

    assert result.actual_trigger is None
    assert result.confidence is None
    assert result.passed is False
    assert result.error == "API timeout"


def test_trigger_metrics_defaults():
    metrics = TriggerMetrics()

    assert metrics.true_positive == 0
    assert metrics.false_positive == 0
    assert metrics.true_negative == 0
    assert metrics.false_negative == 0
    assert metrics.precision == 0
    assert metrics.recall == 0
    assert metrics.f1 == 0
    assert metrics.accuracy == 0


def test_trigger_metrics_custom_values():
    metrics = TriggerMetrics(
        true_positive=10,
        false_positive=2,
        true_negative=8,
        false_negative=1,
        precision=0.8333,
        recall=0.9091,
        f1=0.8696,
        accuracy=0.8571,
    )

    assert metrics.true_positive == 10
    assert metrics.false_positive == 2
    assert metrics.precision == 0.8333


def test_static_health_result_passed():
    result = StaticHealthResult(passed=True, issues=[])
    assert result.passed is True
    assert result.issues == []


def test_static_health_result_failed():
    from skillci.schema.result import Severity

    issue = LintIssue(
        code="MISSING_NAME",
        severity=Severity.error,
        message="name is required",
    )
    result = StaticHealthResult(passed=False, issues=[issue])
    assert result.passed is False
    assert len(result.issues) == 1
    assert result.issues[0].code == "MISSING_NAME"


def test_skill_model_with_all_fields():
    skill = Skill(
        path=Path("/test"),
        skill_md_path=Path("/test/SKILL.md"),
        name="test-skill",
        description="A test skill",
        body="skill body",
        headings=["## Section 1"],
        references=[Path("ref.md")],
        scripts=[Path("script.py")],
        assets=[Path("image.png")],
    )

    assert skill.name == "test-skill"
    assert skill.description == "A test skill"
    assert skill.body == "skill body"
    assert len(skill.headings) == 1
    assert len(skill.references) == 1
    assert len(skill.scripts) == 1
    assert len(skill.assets) == 1


def test_skill_test_case_model():
    case = SkillTestCase(
        name="test-case",
        input="generate API docs",
        expected_trigger=True,
        tags=["api", "documentation"],
    )

    assert case.name == "test-case"
    assert case.input == "generate API docs"
    assert case.expected_trigger is True
    assert "api" in case.tags
    assert "documentation" in case.tags


def test_skill_test_case_defaults():
    case = SkillTestCase(
        name="test-case",
        input="test input",
        expected_trigger=False,
    )

    assert case.tags == []


def test_run_mode_enum():
    assert RunMode.local == "local"
    assert RunMode.llm == "llm"
    assert RunMode.both == "both"

from pathlib import Path

from skillci.schema.config import RunMode, SkillCIConfig, SkillTestCase
from skillci.schema.result import (
    JudgeDisagreement,
    LLMTriggerResult,
    LocalTriggerResult,
    Severity,
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

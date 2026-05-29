from pathlib import Path

from skillci.schema.config import RunMode, SkillCIConfig, SkillTestCase
from skillci.schema.result import LLMTriggerResult, LocalTriggerResult, Severity, TriggerMetrics
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

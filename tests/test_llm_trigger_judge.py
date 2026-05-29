from pathlib import Path

import pytest

from skillci.evaluator.llm_trigger_judge import run_llm_judge
from skillci.parser.config_parser import parse_config
from skillci.parser.skill_parser import parse_skill
from skillci.providers.openai_provider import OpenAIJudgeProvider


def test_mock_provider_returns_deterministic_result():
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    result = run_llm_judge(skill, case, config.thresholds, provider_name="mock")

    assert result.error is None
    assert result.actual_trigger is case.expected_trigger
    assert result.passed is True
    assert 0.8 <= result.confidence <= 1.0


def test_openai_provider_requires_api_key(monkeypatch):
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIJudgeProvider()

    judge_config = config.judge.model_copy(update={"api_key": None})

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        provider.judge_trigger(skill, case, judge_config)

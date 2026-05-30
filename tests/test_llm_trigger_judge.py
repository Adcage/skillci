from pathlib import Path

import pytest

from skillci.cache.judge_cache import JudgeCache
from skillci.evaluator import llm_trigger_judge
from skillci.evaluator.llm_trigger_judge import run_llm_judge
from skillci.parser.config_parser import parse_config
from skillci.parser.skill_parser import parse_skill
from skillci.providers.openai_provider import OpenAIJudgeProvider
from skillci.schema.config import JudgeConfig


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


def test_cache_hit_returns_cached_result(monkeypatch, tmp_path):
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    call_count = 0
    original_judge = type(
        llm_trigger_judge._PROVIDERS["mock"]()
    ).judge_trigger

    def counting_judge(self, skill, case, config):
        nonlocal call_count
        call_count += 1
        return original_judge(self, skill, case, config)

    monkeypatch.setattr(
        type(llm_trigger_judge._PROVIDERS["mock"]()),
        "judge_trigger",
        counting_judge,
    )

    cache = JudgeCache(cache_dir=tmp_path)
    monkeypatch.setattr(llm_trigger_judge, "_cache", cache)

    judge_config = JudgeConfig(cache=True)

    result1 = run_llm_judge(
        skill, case, config.thresholds, provider_name="mock", judge_config=judge_config
    )
    assert call_count == 1

    result2 = run_llm_judge(
        skill, case, config.thresholds, provider_name="mock", judge_config=judge_config
    )
    assert call_count == 1

    assert result1.case_name == result2.case_name
    assert result1.actual_trigger == result2.actual_trigger
    assert result1.passed == result2.passed


def test_cache_disabled_always_calls_provider(monkeypatch, tmp_path):
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    call_count = 0
    original_judge = type(
        llm_trigger_judge._PROVIDERS["mock"]()
    ).judge_trigger

    def counting_judge(self, skill, case, config):
        nonlocal call_count
        call_count += 1
        return original_judge(self, skill, case, config)

    monkeypatch.setattr(
        type(llm_trigger_judge._PROVIDERS["mock"]()),
        "judge_trigger",
        counting_judge,
    )

    cache = JudgeCache(cache_dir=tmp_path)
    monkeypatch.setattr(llm_trigger_judge, "_cache", cache)

    judge_config = JudgeConfig(cache=False)

    run_llm_judge(
        skill, case, config.thresholds, provider_name="mock", judge_config=judge_config
    )
    assert call_count == 1

    run_llm_judge(
        skill, case, config.thresholds, provider_name="mock", judge_config=judge_config
    )
    assert call_count == 2


def test_error_result_not_cached(monkeypatch, tmp_path):
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    from skillci.schema.result import LLMTriggerResult

    def error_judge(self, skill, case, config):
        return LLMTriggerResult(
            case_name=case.name,
            expected_trigger=case.expected_trigger,
            actual_trigger=None,
            confidence=None,
            passed=False,
            error="simulated error",
        )

    monkeypatch.setattr(
        type(llm_trigger_judge._PROVIDERS["mock"]()),
        "judge_trigger",
        error_judge,
    )

    cache = JudgeCache(cache_dir=tmp_path)
    monkeypatch.setattr(llm_trigger_judge, "_cache", cache)

    judge_config = JudgeConfig(cache=True)

    result = run_llm_judge(
        skill, case, config.thresholds, provider_name="mock", judge_config=judge_config
    )
    assert result.error == "simulated error"

    from skillci.cache.cache_key import build_judge_cache_key
    cache_key = build_judge_cache_key(skill, case, judge_config)
    assert cache.get(cache_key) is None


def test_provider_not_found_raises(monkeypatch):
    import skillci.evaluator.llm_trigger_judge as judge_module

    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    original_providers = judge_module._PROVIDERS.copy()
    monkeypatch.setattr(judge_module, "_PROVIDERS", {"mock": original_providers["mock"]})
    monkeypatch.setattr(judge_module, "_cache", None)

    with pytest.raises(ValueError, match="Unsupported judge provider"):
        run_llm_judge(
            skill, case, config.thresholds,
            provider_name="nonexistent_xyz",
            judge_config=JudgeConfig(cache=False),
            use_cache=False,
        )


def test_actual_trigger_none_marks_failed(monkeypatch):
    from skillci.providers.base import JudgeProvider
    from skillci.schema.result import LLMTriggerResult

    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    class NoneProvider(JudgeProvider):
        def judge_trigger(self, skill, case, config):
            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                actual_trigger=None,
                confidence=0.5,
                passed=False,
                reason="could not determine",
            )

    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    new_providers = original_providers.copy()
    new_providers["none_test"] = NoneProvider
    monkeypatch.setattr(judge_module, "_PROVIDERS", new_providers)
    monkeypatch.setattr(judge_module, "_cache", None)

    result = run_llm_judge(
        skill, case, config.thresholds,
        provider_name="none_test",
        judge_config=JudgeConfig(cache=False),
        use_cache=False,
    )

    assert result.actual_trigger is None
    assert result.passed is False
    assert result.error == "LLM judge did not return should_trigger"


def test_use_cache_false_skips_cache(monkeypatch, tmp_path):
    from skillci.providers.mock_provider import MockJudgeProvider

    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    cache = JudgeCache(cache_dir=tmp_path)
    monkeypatch.setattr(llm_trigger_judge, "_cache", cache)

    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    call_count = 0
    original_judge = MockJudgeProvider.judge_trigger

    def counting_judge(self, skill, case, config):
        nonlocal call_count
        call_count += 1
        return original_judge(self, skill, case, config)

    monkeypatch.setattr(MockJudgeProvider, "judge_trigger", counting_judge)

    judge_config = JudgeConfig(cache=True)

    run_llm_judge(
        skill, case, config.thresholds,
        provider_name="mock", judge_config=judge_config, use_cache=False
    )
    assert call_count == 1

    run_llm_judge(
        skill, case, config.thresholds,
        provider_name="mock", judge_config=judge_config, use_cache=False
    )
    assert call_count == 2

    judge_module._PROVIDERS = original_providers


def test_use_cache_true_uses_cache(monkeypatch, tmp_path):
    from skillci.providers.mock_provider import MockJudgeProvider

    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    case = config.cases[0]

    cache = JudgeCache(cache_dir=tmp_path)
    monkeypatch.setattr(llm_trigger_judge, "_cache", cache)

    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    call_count = 0
    original_judge = MockJudgeProvider.judge_trigger

    def counting_judge(self, skill, case, config):
        nonlocal call_count
        call_count += 1
        return original_judge(self, skill, case, config)

    monkeypatch.setattr(MockJudgeProvider, "judge_trigger", counting_judge)

    judge_config = JudgeConfig(cache=True)

    run_llm_judge(
        skill, case, config.thresholds,
        provider_name="mock", judge_config=judge_config, use_cache=True
    )
    assert call_count == 1

    run_llm_judge(
        skill, case, config.thresholds,
        provider_name="mock", judge_config=judge_config, use_cache=True
    )
    assert call_count == 1

    judge_module._PROVIDERS = original_providers

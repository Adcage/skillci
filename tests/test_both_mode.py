from pathlib import Path

import pytest

from skillci.evaluator import llm_trigger_judge
from skillci.evaluator.llm_trigger_judge import JudgeCache
from skillci.providers.base import JudgeProvider
from skillci.runner import run_both_test
from skillci.schema.config import JudgeConfig, SkillTestCase
from skillci.schema.result import LLMTriggerResult
from skillci.schema.skill import Skill


@pytest.fixture(autouse=True)
def isolate_cache(monkeypatch, tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    monkeypatch.setattr(llm_trigger_judge, "_cache", cache)


def test_both_mode_returns_consistent_results_for_example_skill():
    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.skill_name == "api-doc-writer"
    assert report.passed is True
    assert len(report.local_results) == 4
    assert len(report.llm_results) == 4
    assert report.local_metrics is not None
    assert report.llm_metrics is not None
    assert report.llm_average_confidence is not None
    assert report.judge_disagreement_count == 0
    assert report.judge_disagreements == []


def test_both_mode_detects_disagreement():
    class DisagreeingProvider(JudgeProvider):
        def judge_trigger(
            self, skill: Skill, case: SkillTestCase, config: JudgeConfig
        ) -> LLMTriggerResult:
            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                actual_trigger=not case.expected_trigger,
                confidence=0.75,
                passed=False,
                reason="mock disagreement",
            )

    llm_trigger_judge._PROVIDERS["mock"] = DisagreeingProvider

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.judge_disagreement_count > 0
    assert len(report.judge_disagreements) > 0
    for d in report.judge_disagreements:
        assert d.local_actual != d.llm_actual
        assert d.case_name
        assert isinstance(d.expected_trigger, bool)


def test_both_mode_llm_error_not_counted_as_disagreement():
    class ErrorProvider(JudgeProvider):
        def judge_trigger(
            self, skill: Skill, case: SkillTestCase, config: JudgeConfig
        ) -> LLMTriggerResult:
            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                actual_trigger=None,
                confidence=None,
                passed=False,
                error="simulated API error",
            )

    llm_trigger_judge._PROVIDERS["mock"] = ErrorProvider

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.judge_disagreement_count == 0
    assert report.judge_disagreements == []
    for result in report.llm_results:
        assert result.error == "simulated API error"


def test_both_mode_partial_disagreement():
    call_count = 0

    class SelectiveProvider(JudgeProvider):
        def judge_trigger(
            self, skill: Skill, case: SkillTestCase, config: JudgeConfig
        ) -> LLMTriggerResult:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return LLMTriggerResult(
                    case_name=case.name,
                    expected_trigger=case.expected_trigger,
                    actual_trigger=not case.expected_trigger,
                    confidence=0.6,
                    passed=False,
                    reason="selective disagreement",
                )
            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                actual_trigger=case.expected_trigger,
                confidence=0.9,
                passed=True,
                reason="mock agree",
            )

    llm_trigger_judge._PROVIDERS["mock"] = SelectiveProvider

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.judge_disagreement_count == 1
    assert len(report.judge_disagreements) == 1
    disagreement = report.judge_disagreements[0]
    assert disagreement.local_actual != disagreement.llm_actual


def test_both_mode_includes_all_metrics():
    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.local_metrics is not None
    assert report.llm_metrics is not None
    assert report.local_metrics.precision >= 0
    assert report.local_metrics.recall >= 0
    assert report.local_metrics.f1 >= 0
    assert report.llm_metrics.precision >= 0
    assert report.llm_metrics.recall >= 0
    assert report.llm_metrics.f1 >= 0


def test_both_mode_disagreement_has_correct_fields():
    class DisagreeingProvider(JudgeProvider):
        def judge_trigger(
            self, skill: Skill, case: SkillTestCase, config: JudgeConfig
        ) -> LLMTriggerResult:
            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                actual_trigger=not case.expected_trigger,
                confidence=0.75,
                passed=False,
                reason="mock disagreement",
            )

    llm_trigger_judge._PROVIDERS["mock"] = DisagreeingProvider

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.judge_disagreement_count > 0
    for d in report.judge_disagreements:
        assert d.case_name
        assert isinstance(d.expected_trigger, bool)
        assert isinstance(d.local_actual, bool)
        assert d.llm_actual is not None
        assert d.local_score is not None
        assert d.llm_confidence is not None


def test_both_mode_passed_based_on_local_results():
    class DisagreeingProvider(JudgeProvider):
        def judge_trigger(
            self, skill: Skill, case: SkillTestCase, config: JudgeConfig
        ) -> LLMTriggerResult:
            return LLMTriggerResult(
                case_name=case.name,
                expected_trigger=case.expected_trigger,
                actual_trigger=not case.expected_trigger,
                confidence=0.75,
                passed=False,
                reason="mock disagreement",
            )

    llm_trigger_judge._PROVIDERS["mock"] = DisagreeingProvider

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.passed is True
    assert all(r.passed for r in report.local_results)


def test_both_mode_llm_average_confidence():
    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.llm_average_confidence is not None
    assert 0 <= report.llm_average_confidence <= 1


def test_both_mode_static_health_passed():
    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.static_health is not None
    assert report.static_health.passed is True

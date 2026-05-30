from pathlib import Path

from skillci.providers.mock_provider import MockJudgeProvider
from skillci.runner import run_both_test, run_lint, run_llm_test, run_local_test


def test_run_lint_for_example_skill():
    result = run_lint(Path("examples/api-doc-writer"))

    assert result.passed is True


def test_run_local_test_for_example_skill():
    report = run_local_test(Path("examples/api-doc-writer"))

    assert report.skill_name == "api-doc-writer"
    assert report.passed is True
    assert report.local_metrics is not None
    assert report.local_metrics.f1 >= 0.8
    assert len(report.local_results) == 4


def test_run_llm_test_for_example_skill_with_mock():
    report = run_llm_test(Path("examples/api-doc-writer"), provider_name="mock")

    assert report.skill_name == "api-doc-writer"
    assert len(report.llm_results) == 4
    assert report.llm_metrics is not None
    assert report.llm_metrics.f1 >= 0.8
    assert report.llm_average_confidence is not None
    assert report.passed is True


def test_run_both_test_for_example_skill_with_mock():
    report = run_both_test(Path("examples/api-doc-writer"), provider_name="mock")

    assert report.skill_name == "api-doc-writer"
    assert report.passed is True
    assert len(report.local_results) == 4
    assert len(report.llm_results) == 4
    assert report.local_metrics is not None
    assert report.llm_metrics is not None
    assert report.local_metrics.f1 >= 0.8
    assert report.llm_metrics.f1 >= 0.8
    assert report.llm_average_confidence is not None
    assert isinstance(report.judge_disagreement_count, int)
    assert isinstance(report.judge_disagreements, list)


def test_run_llm_test_with_use_cache_false():
    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    report = run_llm_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.skill_name == "api-doc-writer"
    assert report.passed is True
    assert len(report.llm_results) == 4
    assert report.llm_metrics is not None

    judge_module._PROVIDERS = original_providers


def test_run_llm_test_with_use_cache_true():
    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    report = run_llm_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=True
    )

    assert report.skill_name == "api-doc-writer"
    assert report.passed is True
    assert len(report.llm_results) == 4

    judge_module._PROVIDERS = original_providers


def test_run_both_test_with_use_cache_false():
    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )

    assert report.skill_name == "api-doc-writer"
    assert report.passed is True
    assert len(report.local_results) == 4
    assert len(report.llm_results) == 4

    judge_module._PROVIDERS = original_providers


def test_run_both_test_with_use_cache_true():
    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=True
    )

    assert report.skill_name == "api-doc-writer"
    assert report.passed is True

    judge_module._PROVIDERS = original_providers


def test_run_local_test_static_health_check():
    report = run_local_test(Path("examples/api-doc-writer"))

    assert report.static_health is not None
    assert report.static_health.passed is True
    assert len(report.static_health.issues) == 0


def test_run_local_test_all_cases_have_results():
    report = run_local_test(Path("examples/api-doc-writer"))

    assert len(report.local_results) == 4
    for result in report.local_results:
        assert result.case_name
        assert isinstance(result.expected_trigger, bool)
        assert isinstance(result.actual_trigger, bool)
        assert 0 <= result.trigger_score <= 1
        assert isinstance(result.passed, bool)


def test_run_llm_test_all_cases_have_results():
    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    report = run_llm_test(Path("examples/api-doc-writer"), provider_name="mock")

    assert len(report.llm_results) == 4
    for result in report.llm_results:
        assert result.case_name
        assert isinstance(result.expected_trigger, bool)
        assert result.actual_trigger is not None
        assert result.confidence is not None
        assert 0 <= result.confidence <= 1

    judge_module._PROVIDERS = original_providers


def test_run_both_test_results_count():
    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    report = run_both_test(Path("examples/api-doc-writer"), provider_name="mock", use_cache=False)

    assert len(report.local_results) == 4
    assert len(report.llm_results) == 4
    assert report.judge_disagreement_count == 0
    assert len(report.judge_disagreements) == 0

    judge_module._PROVIDERS = original_providers


def test_run_both_test_metrics_consistency():
    import skillci.evaluator.llm_trigger_judge as judge_module
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    report = run_both_test(Path("examples/api-doc-writer"), provider_name="mock", use_cache=False)

    assert report.local_metrics is not None
    assert report.llm_metrics is not None
    assert report.local_metrics.precision == report.llm_metrics.precision
    assert report.local_metrics.recall == report.llm_metrics.recall
    assert report.local_metrics.f1 == report.llm_metrics.f1

    judge_module._PROVIDERS = original_providers

from pathlib import Path

from skillci.runner import run_lint, run_llm_test, run_local_test


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

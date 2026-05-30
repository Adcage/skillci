from pathlib import Path

from typer.testing import CliRunner

from skillci.cli import app
from skillci.report.markdown_report import render_github_markdown, render_markdown
from skillci.report.terminal_report import render_report
from skillci.runner import run_local_test
from skillci.schema.report import SkillCIReport
from skillci.schema.result import (
    JudgeDisagreement,
    LLMTriggerResult,
    LocalTriggerResult,
    StaticHealthResult,
    TriggerMetrics,
)

runner = CliRunner()


def _make_report_with_disagreements() -> SkillCIReport:
    return SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=True, issues=[]),
        local_results=[
            LocalTriggerResult(
                case_name="case1",
                expected_trigger=True,
                actual_trigger=True,
                passed=True,
                trigger_score=0.9,
                reason="matched",
                matched_terms=["doc"],
            )
        ],
        judge_disagreement_count=3,
        judge_disagreements=[
            JudgeDisagreement(
                case_name="case-a",
                expected_trigger=True,
                local_actual=True,
                llm_actual=False,
            ),
            JudgeDisagreement(
                case_name="case-b",
                expected_trigger=False,
                local_actual=False,
                llm_actual=True,
                reason="LLM misclassified trigger intent",
            ),
            JudgeDisagreement(
                case_name="case-c",
                expected_trigger=True,
                local_actual=True,
                llm_actual=None,
                reason="LLM returned no verdict",
            ),
        ],
        passed=True,
    )


def test_render_markdown_contains_expected_sections():
    report = run_local_test(Path("examples/api-doc-writer"))

    content = render_markdown(report)

    assert "# SkillCI Report" in content
    assert "api-doc-writer" in content
    assert "## Static Health" in content
    assert "## Trigger Check" in content
    assert "## Local Metrics" in content


def test_report_markdown_writes_file(tmp_path):
    report_path = tmp_path / "report.md"

    result = runner.invoke(
        app,
        [
            "report",
            "examples/api-doc-writer",
            "--format",
            "markdown",
            "--output",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "# SkillCI Report" in content
    assert "api-doc-writer" in content


def test_markdown_report_shows_disagreements():
    report = _make_report_with_disagreements()
    content = render_markdown(report)

    assert "## Judge Disagreements" in content
    assert "Count: 3" in content
    assert "case-a" in content
    assert "case-b" in content
    assert "case-c" in content
    assert "LLM misclassified trigger intent" in content
    assert "LLM returned no verdict" in content
    assert "| Reason |" in content


def test_markdown_report_no_disagreements_section_when_empty():
    report = run_local_test(Path("examples/api-doc-writer"))
    content = render_markdown(report)

    assert "## Judge Disagreements" not in content


def test_terminal_report_shows_disagreements(capsys):
    report = _make_report_with_disagreements()
    render_report(report)

    captured = capsys.readouterr()
    assert "Judge Disagreements" in captured.out
    assert "Count: 3" in captured.out
    assert "DISAGREE case-a" in captured.out
    assert "DISAGREE case-b" in captured.out
    assert "DISAGREE case-c" in captured.out
    assert "reason: LLM misclassified trigger intent" in captured.out
    assert "reason: LLM returned no verdict" in captured.out


def test_render_github_markdown_contains_expected_sections():
    report = run_local_test(Path("examples/api-doc-writer"))
    content = render_github_markdown(report)

    assert "## SkillCI Check" in content
    assert "| Section | Result |" in content
    assert "| Static Health | passed |" in content
    assert "| Local F1 |" in content
    assert "| Judge Disagreements | 0 |" in content
    assert "| Regressions | 0 |" in content
    assert "| Final Result | **passed** |" in content


def test_render_github_markdown_shows_failed_status():
    report = SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=False, issues=[]),
        local_results=[],
        passed=False,
    )
    content = render_github_markdown(report)

    assert "| Static Health | failed |" in content
    assert "| Final Result | **failed**** |" not in content
    assert "| Final Result | **failed** |" in content


def test_render_github_markdown_with_disagreements():
    report = _make_report_with_disagreements()
    content = render_github_markdown(report)

    assert "| Judge Disagreements | 3 |" in content
    assert "| Final Result | **passed** |" in content


def test_report_github_format_writes_file(tmp_path):
    report_path = tmp_path / "report.md"

    result = runner.invoke(
        app,
        [
            "report",
            "examples/api-doc-writer",
            "--format",
            "github",
            "--output",
            str(report_path),
        ],
    )

    assert result.exit_code == 0
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "## SkillCI Check" in content
    assert "| Static Health |" in content


def test_report_unsupported_format():
    result = runner.invoke(
        app,
        [
            "report",
            "examples/api-doc-writer",
            "--format",
            "html",
        ],
    )

    assert result.exit_code == 2


def test_markdown_report_contains_llm_metrics():
    from skillci.runner import run_both_test

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )
    content = render_markdown(report)

    assert "## LLM Metrics" in content
    assert "## LLM Trigger Check" in content


def test_github_markdown_with_llm_metrics():
    from skillci.runner import run_both_test

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )
    content = render_github_markdown(report)

    assert "| LLM F1 |" in content


def test_terminal_report_shows_llm_section(capsys):
    from skillci.runner import run_both_test

    report = run_both_test(
        Path("examples/api-doc-writer"), provider_name="mock", use_cache=False
    )
    render_report(report)

    captured = capsys.readouterr()
    assert "LLM Trigger Check" in captured.out
    assert "LLM Summary" in captured.out


def test_terminal_report_shows_llm_error(capsys):
    report = SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=True, issues=[]),
        llm_results=[
            LLMTriggerResult(
                case_name="error-case",
                expected_trigger=True,
                actual_trigger=None,
                passed=False,
                error="API timeout",
            )
        ],
        passed=False,
    )
    render_report(report)

    captured = capsys.readouterr()
    assert "LLM Trigger Check" in captured.out
    assert "ERROR error-case" in captured.out
    assert "API timeout" in captured.out


def test_terminal_report_no_metrics(capsys):
    report = SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=True, issues=[]),
        passed=True,
    )
    render_report(report)

    captured = capsys.readouterr()
    assert "Summary" not in captured.out
    assert "LLM Summary" not in captured.out


def test_markdown_report_empty_results():
    report = SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=True, issues=[]),
        passed=True,
    )
    content = render_markdown(report)

    assert "# SkillCI Report" in content
    assert "## Static Health" in content
    assert "## Trigger Check" not in content
    assert "## LLM Trigger Check" not in content
    assert "## Local Metrics" not in content
    assert "## LLM Metrics" not in content
    assert "## Judge Disagreements" not in content


def test_markdown_report_with_llm_error():
    from skillci.schema.result import LLMTriggerResult

    report = SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=True, issues=[]),
        llm_results=[
            LLMTriggerResult(
                case_name="error-case",
                expected_trigger=True,
                actual_trigger=None,
                passed=False,
                error="Connection failed",
            )
        ],
        passed=False,
    )
    content = render_markdown(report)

    assert "## LLM Trigger Check" in content
    assert "error-case" in content
    assert "error" in content


def test_github_markdown_empty_results():
    report = SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=True, issues=[]),
        passed=True,
    )
    content = render_github_markdown(report)

    assert "## SkillCI Check" in content
    assert "| Static Health | passed |" in content
    assert "| Local F1 |" not in content
    assert "| LLM F1 |" not in content
    assert "| Judge Disagreements | 0 |" in content


def test_github_markdown_all_failed():
    report = SkillCIReport(
        skill_name="test-skill",
        skill_path="/tmp/test",
        static_health=StaticHealthResult(passed=False, issues=[]),
        local_results=[
            LocalTriggerResult(
                case_name="case1",
                expected_trigger=True,
                actual_trigger=False,
                passed=False,
                trigger_score=0.3,
                reason="low score",
            )
        ],
        local_metrics=TriggerMetrics(
            true_positive=0,
            false_negative=1,
            precision=0,
            recall=0,
            f1=0,
            accuracy=0,
        ),
        passed=False,
    )
    content = render_github_markdown(report)

    assert "| Static Health | failed |" in content
    assert "| Local F1 | 0.00 |" in content
    assert "| Final Result | **failed** |" in content

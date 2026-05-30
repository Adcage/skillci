from pathlib import Path

from typer.testing import CliRunner

from skillci.cli import app
from skillci.report.markdown_report import render_markdown
from skillci.report.terminal_report import render_report
from skillci.runner import run_local_test
from skillci.schema.report import SkillCIReport
from skillci.schema.result import (
    JudgeDisagreement,
    LocalTriggerResult,
    StaticHealthResult,
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
        judge_disagreement_count=2,
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
    assert "Count: 2" in content
    assert "case-a" in content
    assert "case-b" in content


def test_markdown_report_no_disagreements_section_when_empty():
    report = run_local_test(Path("examples/api-doc-writer"))
    content = render_markdown(report)

    assert "## Judge Disagreements" not in content


def test_terminal_report_shows_disagreements(capsys):
    report = _make_report_with_disagreements()
    render_report(report)

    captured = capsys.readouterr()
    assert "Judge Disagreements" in captured.out
    assert "Count: 2" in captured.out
    assert "DISAGREE case-a" in captured.out
    assert "DISAGREE case-b" in captured.out

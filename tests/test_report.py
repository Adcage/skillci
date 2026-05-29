from pathlib import Path

from typer.testing import CliRunner

from skillci.cli import app
from skillci.report.markdown_report import render_markdown
from skillci.runner import run_local_test

runner = CliRunner()


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

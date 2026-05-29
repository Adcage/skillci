from typer.testing import CliRunner

from skillci.cli import app

runner = CliRunner()


def test_help_command_shows_skillci_commands():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "lint" in result.output
    assert "test" in result.output


def test_lint_command_runs_for_example_skill():
    result = runner.invoke(app, ["lint", "examples/api-doc-writer"])

    assert result.exit_code == 0
    assert "Static Health" in result.output


def test_test_command_runs_local_mode_for_example_skill():
    result = runner.invoke(app, ["test", "examples/api-doc-writer", "--mode", "local"])

    assert result.exit_code == 0
    assert "Trigger Check" in result.output
    assert "Local F1" in result.output


def test_test_command_runs_llm_mode_for_example_skill():
    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "llm", "--provider", "mock"],
    )

    assert result.exit_code == 0
    assert "LLM Trigger Check" in result.output
    assert "LLM F1" in result.output


def test_help_includes_publishable_commands():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.output
    assert "snapshot" in result.output
    assert "report" in result.output


def test_test_command_supports_compare_latest():
    runner.invoke(app, ["snapshot", "examples/api-doc-writer"])
    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "local", "--compare", "latest"],
    )

    assert result.exit_code == 0
    assert "Regression Report" in result.output

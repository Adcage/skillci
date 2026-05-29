import json

from typer.testing import CliRunner

from skillci.cli import app

runner = CliRunner()


def test_test_command_outputs_json_report():
    result = runner.invoke(app, ["test", "examples/api-doc-writer", "--mode", "local", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["skill_name"] == "api-doc-writer"
    assert payload["passed"] is True
    assert len(payload["local_results"]) == 4


def test_test_command_outputs_llm_json_report():
    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "llm", "--provider", "mock", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["skill_name"] == "api-doc-writer"
    assert payload["passed"] is True
    assert len(payload["llm_results"]) == 4
    assert payload["llm_metrics"]["f1"] >= 0.8

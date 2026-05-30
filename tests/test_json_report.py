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


def test_test_command_outputs_both_json_report():
    result = runner.invoke(
        app,
        [
            "test",
            "examples/api-doc-writer",
            "--mode",
            "both",
            "--provider",
            "mock",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["skill_name"] == "api-doc-writer"
    assert payload["passed"] is True
    assert len(payload["local_results"]) == 4
    assert len(payload["llm_results"]) == 4
    assert payload["local_metrics"]["f1"] >= 0.8
    assert payload["llm_metrics"]["f1"] >= 0.8
    assert "judge_disagreement_count" in payload
    assert "judge_disagreements" in payload
    assert isinstance(payload["judge_disagreement_count"], int)
    assert isinstance(payload["judge_disagreements"], list)


def test_json_report_contains_disagreement_fields():
    result = runner.invoke(
        app,
        [
            "test",
            "examples/api-doc-writer",
            "--mode",
            "both",
            "--provider",
            "mock",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)

    if payload["judge_disagreement_count"] > 0:
        disagreement = payload["judge_disagreements"][0]
        assert "case_name" in disagreement
        assert "expected_trigger" in disagreement
        assert "local_actual" in disagreement
        assert "llm_actual" in disagreement

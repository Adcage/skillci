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


def test_test_command_accepts_no_cache_flag():
    import skillci.evaluator.llm_trigger_judge as judge_module
    from skillci.providers.mock_provider import MockJudgeProvider
    original_providers = judge_module._PROVIDERS.copy()
    judge_module._PROVIDERS["mock"] = MockJudgeProvider

    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "llm", "--provider", "mock", "--no-cache"],
    )

    assert result.exit_code == 0
    assert "LLM Trigger Check" in result.output

    judge_module._PROVIDERS = original_providers


def test_test_command_no_cache_flag_in_help():
    result = runner.invoke(app, ["test", "--help"])

    assert result.exit_code == 0
    # 清除 ANSI 转义码后检查
    clean_output = result.output.replace("\x1b[", "").replace("\x1b[0m", "")
    assert "no-cache" in clean_output
    assert "Disable LLM judge cache" in clean_output


def test_test_command_runs_both_mode_for_example_skill():
    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "both", "--provider", "mock"],
    )

    assert result.exit_code == 0
    assert "Trigger Check" in result.output
    assert "LLM Trigger Check" in result.output
    assert "Local F1" in result.output
    assert "LLM F1" in result.output


def test_test_command_both_mode_with_json_output():
    import json

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
    assert len(payload["local_results"]) == 4
    assert len(payload["llm_results"]) == 4
    assert "judge_disagreement_count" in payload
    assert "judge_disagreements" in payload


def test_test_command_unsupported_mode():
    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "invalid"],
    )

    assert result.exit_code == 2


def test_report_command_github_format():
    result = runner.invoke(
        app,
        ["report", "examples/api-doc-writer", "--format", "github"],
    )

    assert result.exit_code == 0
    assert "## SkillCI Check" in result.output
    assert "| Static Health |" in result.output


def test_report_command_unsupported_format():
    result = runner.invoke(
        app,
        ["report", "examples/api-doc-writer", "--format", "html"],
    )

    assert result.exit_code == 2


def test_lint_command_for_invalid_path():
    result = runner.invoke(app, ["lint", "nonexistent/path"])

    assert result.exit_code != 0


def test_test_command_for_invalid_path():
    result = runner.invoke(app, ["test", "nonexistent/path", "--mode", "local"])

    assert result.exit_code != 0


def test_snapshot_command():
    result = runner.invoke(app, ["snapshot", "examples/api-doc-writer"])

    assert result.exit_code == 0
    assert "Saved baseline snapshot" in result.output


def test_version_flag():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "skillci" in result.output


def test_test_command_json_output():
    import json

    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "local", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "skill_name" in payload
    assert "local_results" in payload


def test_test_command_llm_json_output():
    import json

    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "llm", "--provider", "mock", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "llm_results" in payload
    assert "llm_metrics" in payload


def test_test_command_both_json_output():
    import json

    result = runner.invoke(
        app,
        ["test", "examples/api-doc-writer", "--mode", "both", "--provider", "mock", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "local_results" in payload
    assert "llm_results" in payload
    assert "judge_disagreement_count" in payload

from pathlib import Path

import pytest
import yaml

from skillci.parser.config_parser import ConfigParseError, parse_config
from skillci.schema.config import RunMode


def test_parse_example_config_resolves_relative_skill_path():
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))

    assert config.skill == Path("examples/api-doc-writer").resolve()
    assert config.mode == RunMode.local
    assert config.thresholds.trigger_score == 0.45
    assert len(config.cases) == 4
    assert config.cases[0].expected_trigger is True


def test_parse_config_file_not_found():
    with pytest.raises(ConfigParseError, match="Config file not found"):
        parse_config(Path("nonexistent/skillci.yaml"))


def test_parse_config_invalid_yaml(tmp_path):
    config_path = tmp_path / "skillci.yaml"
    config_path.write_text("invalid: yaml: content: [", encoding="utf-8")

    with pytest.raises(ConfigParseError, match="Invalid YAML config"):
        parse_config(config_path)


def test_parse_config_missing_skill_field(tmp_path):
    config_path = tmp_path / "skillci.yaml"
    config_path.write_text(
        yaml.dump({"cases": [{"name": "test", "input": "test", "expected_trigger": True}]}),
        encoding="utf-8",
    )

    with pytest.raises(ConfigParseError, match="Missing required config field: skill"):
        parse_config(config_path)


def test_parse_config_missing_cases_field(tmp_path):
    config_path = tmp_path / "skillci.yaml"
    config_path.write_text(yaml.dump({"skill": "."}), encoding="utf-8")

    with pytest.raises(ConfigParseError, match="Missing required config field: cases"):
        parse_config(config_path)


def test_parse_config_with_local_override(tmp_path):
    config_path = tmp_path / "skillci.yaml"
    config_path.write_text(
        yaml.dump(
            {
                "skill": ".",
                "mode": "local",
                "thresholds": {"trigger_score": 0.5},
                "cases": [
                    {"name": "test", "input": "test", "expected_trigger": True}
                ],
            }
        ),
        encoding="utf-8",
    )

    local_config_path = tmp_path / "skillci.local.yaml"
    local_config_path.write_text(
        yaml.dump({"thresholds": {"trigger_score": 0.8}}),
        encoding="utf-8",
    )

    config = parse_config(config_path)
    assert config.thresholds.trigger_score == 0.8


def test_parse_config_default_mode():
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))
    assert config.mode == RunMode.local


def test_parse_config_judge_defaults():
    from skillci.schema.config import JudgeConfig

    judge = JudgeConfig()
    assert judge.provider == "openai"
    assert judge.model == "gpt-4.1-mini"
    assert judge.temperature == 0
    assert judge.cache is True

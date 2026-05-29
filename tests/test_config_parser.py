from pathlib import Path

from skillci.parser.config_parser import parse_config
from skillci.schema.config import RunMode


def test_parse_example_config_resolves_relative_skill_path():
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))

    assert config.skill == Path("examples/api-doc-writer").resolve()
    assert config.mode == RunMode.local
    assert config.thresholds.trigger_score == 0.45
    assert len(config.cases) == 4
    assert config.cases[0].expected_trigger is True

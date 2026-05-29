from pathlib import Path

import yaml

from skillci.schema.config import SkillCIConfig


class ConfigParseError(ValueError):
    pass


def parse_config(config_path: Path) -> SkillCIConfig:
    config_path = config_path.resolve()
    if not config_path.exists():
        raise ConfigParseError(f"Config file not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigParseError(f"Invalid YAML config: {config_path}") from exc

    if "skill" not in raw:
        raise ConfigParseError("Missing required config field: skill")
    if "cases" not in raw:
        raise ConfigParseError("Missing required config field: cases")

    skill_path = Path(raw["skill"])
    if not skill_path.is_absolute():
        skill_path = config_path.parent / skill_path
    raw["skill"] = skill_path.resolve()

    return SkillCIConfig.model_validate(raw)

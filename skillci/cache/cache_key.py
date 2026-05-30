import hashlib
import json

from skillci.evaluator.prompt import PROMPT_VERSION
from skillci.schema.config import JudgeConfig, SkillTestCase
from skillci.schema.skill import Skill


def build_judge_cache_key(
    skill: Skill,
    case: SkillTestCase,
    config: JudgeConfig,
) -> str:
    key_data = {
        "skill_name": skill.name,
        "skill_description": skill.description,
        "skill_body_excerpt": skill.body[:500] if skill.body else "",
        "case_name": case.name,
        "case_input": case.input,
        "provider": config.provider,
        "base_url": config.base_url,
        "model": config.model,
        "prompt_version": PROMPT_VERSION,
    }
    key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

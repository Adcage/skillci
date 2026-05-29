from pathlib import Path

PROMPT_VERSION = "v0.2"

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(filename: str) -> str:
    return (_PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


def get_system_prompt() -> str:
    return _load_prompt("judge_system.md")


def get_user_prompt(
    skill_name: str,
    skill_description: str,
    skill_body_excerpt: str,
    user_input: str,
) -> str:
    template = _load_prompt("judge_user.md")
    return template.format(
        skill_name=skill_name,
        skill_description=skill_description,
        skill_body_excerpt=skill_body_excerpt,
        user_input=user_input,
    )

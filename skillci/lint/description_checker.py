import re

from skillci.schema.result import LintIssue, Severity
from skillci.schema.skill import Skill

MIN_DESCRIPTION_WORDS = 8
MAX_DESCRIPTION_WORDS = 80
MAX_DESCRIPTION_CHARS = 500

BROAD_TERMS = [
    "all tasks",
    "anything",
    "general purpose",
    "any file",
    "all code",
    "everything",
    "any task",
    "all kinds of",
    "various tasks",
    "multiple tasks",
    "improve productivity",
    "help with coding",
    "help users",
    "assist with development",
    "通用",
    "所有任务",
    "任何任务",
    "任何文件",
    "所有代码",
    "各种任务",
    "多种任务",
    "提升效率",
    "辅助开发",
    "帮助用户",
]

SCOPE_HINT_TERMS = [
    "use this skill when",
    "when the user",
    "if the user asks",
    "for",
    "from",
    "to",
    "当用户",
    "用于",
    "适用于",
    "根据",
    "从",
    "转换为",
]


def count_words(text: str) -> int:
    english_words = re.findall(r"[A-Za-z0-9_]+", text)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    return len(english_words) + len(chinese_chars) // 2


def contains_any(text: str, terms: list[str]) -> list[str]:
    lower_text = text.lower()
    return [term for term in terms if term.lower() in lower_text]


def check_description(skill: Skill) -> list[LintIssue]:
    issues: list[LintIssue] = []
    description = skill.description
    word_count = count_words(description)
    char_count = len(description)

    if word_count < MIN_DESCRIPTION_WORDS:
        issues.append(
            LintIssue(
                code="description_too_short",
                severity=Severity.warning,
                message=(
                    f"Description is too short ({word_count} words). "
                    "It may not provide enough trigger context."
                ),
                file=str(skill.skill_md_path),
            )
        )

    if word_count > MAX_DESCRIPTION_WORDS or char_count > MAX_DESCRIPTION_CHARS:
        issues.append(
            LintIssue(
                code="description_too_long",
                severity=Severity.warning,
                message=(
                    f"Description is too long ({word_count} words, {char_count} chars). "
                    "Move detailed instructions to the skill body and keep the description "
                    "focused on trigger conditions."
                ),
                file=str(skill.skill_md_path),
            )
        )

    broad_matches = contains_any(description, BROAD_TERMS)
    if broad_matches:
        issues.append(
            LintIssue(
                code="description_too_broad",
                severity=Severity.warning,
                message=(
                    "Description may be too broad. "
                    f"Matched broad terms: {', '.join(broad_matches)}"
                ),
                file=str(skill.skill_md_path),
            )
        )

    scope_matches = contains_any(description, SCOPE_HINT_TERMS)
    if not scope_matches:
        issues.append(
            LintIssue(
                code="description_missing_scope",
                severity=Severity.warning,
                message=(
                    "Description does not clearly state when this skill should be used. "
                    "Consider using patterns like 'Use this skill when...' or '用于...'."
                ),
                file=str(skill.skill_md_path),
            )
        )

    return issues

from skillci.schema.result import LintIssue, Severity
from skillci.schema.skill import Skill

BROAD_TERMS = [
    "all tasks",
    "anything",
    "general purpose",
    "any file",
    "all code",
    "everything",
    "improve productivity",
    "help with coding",
    "通用",
    "所有任务",
    "任何文件",
    "提升效率",
]


def check_description(skill: Skill) -> list[LintIssue]:
    issues: list[LintIssue] = []
    words = skill.description.split()
    if len(words) < 8:
        issues.append(
            LintIssue(
                code="description_too_short",
                severity=Severity.warning,
                message="description is shorter than 8 words",
                file=str(skill.skill_md_path),
            )
        )

    lowered = skill.description.lower()
    for term in BROAD_TERMS:
        if term.lower() in lowered:
            issues.append(
                LintIssue(
                    code="description_too_broad",
                    severity=Severity.warning,
                    message=f"description contains broad phrase: {term}",
                    file=str(skill.skill_md_path),
                )
            )
    return issues

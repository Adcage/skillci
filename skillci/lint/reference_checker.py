from pathlib import Path

from skillci.schema.result import LintIssue, Severity
from skillci.schema.skill import Skill


def check_references(skill: Skill) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for relative_path in [*skill.references, *skill.scripts, *skill.assets]:
        full_path = skill.path / relative_path
        if not full_path.exists():
            issues.append(
                LintIssue(
                    code="broken_reference",
                    severity=Severity.error,
                    message=f"referenced file not found: {relative_path.as_posix()}",
                    file=str(Path(skill.skill_md_path)),
                )
            )
    return issues

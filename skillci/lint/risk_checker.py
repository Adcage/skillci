from skillci.schema.result import LintIssue, Severity
from skillci.schema.skill import Skill

DANGEROUS_TERMS = [
    "rm -rf",
    "del /s",
    "format",
    "curl | sh",
    "wget | sh",
    "chmod 777",
    "sudo",
    "eval(",
    "exec(",
    "os.system",
    "subprocess",
]
SENSITIVE_TERMS = ["~/.ssh", "/etc/passwd", "id_rsa", ".env", "credentials.json"]


def check_risks(skill: Skill) -> list[LintIssue]:
    issues: list[LintIssue] = []
    content = f"{skill.description}\n{skill.body}".lower()

    for term in DANGEROUS_TERMS:
        if term.lower() in content:
            issues.append(
                LintIssue(
                    code="dangerous_command",
                    severity=Severity.warning,
                    message=f"potentially dangerous command found: {term}",
                    file=str(skill.skill_md_path),
                )
            )

    for term in SENSITIVE_TERMS:
        if term.lower() in content:
            issues.append(
                LintIssue(
                    code="sensitive_path",
                    severity=Severity.warning,
                    message=f"sensitive path or filename found: {term}",
                    file=str(skill.skill_md_path),
                )
            )

    return issues

from skillci.lint.description_checker import check_description
from skillci.lint.reference_checker import check_references
from skillci.lint.risk_checker import check_risks
from skillci.schema.result import Severity, StaticHealthResult
from skillci.schema.skill import Skill


def run_static_health_checks(skill: Skill) -> StaticHealthResult:
    issues = [
        *check_description(skill),
        *check_references(skill),
        *check_risks(skill),
    ]
    passed = not any(issue.severity == Severity.error for issue in issues)
    return StaticHealthResult(passed=passed, issues=issues)

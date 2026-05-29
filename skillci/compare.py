from dataclasses import dataclass
from pathlib import Path

from skillci.schema.report import SkillCIReport


@dataclass
class RegressionCaseChange:
    case_name: str
    previous_actual: bool | None
    current_actual: bool | None
    previous_passed: bool | None
    current_passed: bool
    previous_score: float | None
    current_score: float


@dataclass
class RegressionReport:
    skill_name: str
    baseline_path: Path
    current_passed: bool
    total_cases: int
    unchanged_cases: int
    regressed_cases: int
    improved_cases: int
    changes: list[RegressionCaseChange]


def run_compare(baseline_path: Path, current_report: SkillCIReport) -> RegressionReport:
    baseline_path = baseline_path.resolve()
    baseline = SkillCIReport.model_validate_json(baseline_path.read_text(encoding="utf-8"))

    baseline_lookup = {result.case_name: result for result in baseline.local_results}
    changes: list[RegressionCaseChange] = []

    for result in current_report.local_results:
        previous = baseline_lookup.get(result.case_name)
        if previous is None:
            changes.append(
                RegressionCaseChange(
                    case_name=result.case_name,
                    previous_actual=None,
                    current_actual=result.actual_trigger,
                    previous_passed=None,
                    current_passed=result.passed,
                    previous_score=None,
                    current_score=result.trigger_score,
                )
            )
            continue

        if (
            previous.actual_trigger != result.actual_trigger
            or previous.passed != result.passed
        ):
            changes.append(
                RegressionCaseChange(
                    case_name=result.case_name,
                    previous_actual=previous.actual_trigger,
                    current_actual=result.actual_trigger,
                    previous_passed=previous.passed,
                    current_passed=result.passed,
                    previous_score=previous.trigger_score,
                    current_score=result.trigger_score,
                )
            )

    regressed = sum(
        1
        for change in changes
        if change.current_passed is False and change.previous_passed is not False
    )
    improved = sum(
        1
        for change in changes
        if change.current_passed is True and change.previous_passed is not True
    )

    return RegressionReport(
        skill_name=current_report.skill_name,
        baseline_path=baseline_path,
        current_passed=current_report.passed,
        total_cases=len(current_report.local_results),
        unchanged_cases=len(current_report.local_results) - len(changes),
        regressed_cases=regressed,
        improved_cases=improved,
        changes=changes,
    )

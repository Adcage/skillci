from rich.console import Console

from skillci.schema.report import SkillCIReport
from skillci.schema.result import Severity, StaticHealthResult


def render_static_health(result: StaticHealthResult, console: Console | None = None) -> None:
    console = console or Console()
    console.print("Static Health", style="bold")
    if not result.issues:
        console.print("  OK no issues found")
        return

    for issue in result.issues:
        marker = (
            "ERROR"
            if issue.severity == Severity.error
            else "WARN"
            if issue.severity == Severity.warning
            else "INFO"
        )
        console.print(f"  {marker} {issue.code}: {issue.message}")


def render_report(report: SkillCIReport, console: Console | None = None) -> None:
    console = console or Console()
    console.print(f"SkillCI Report: {report.skill_name}", style="bold")
    render_static_health(report.static_health, console)

    if report.local_results:
        console.print("\nTrigger Check", style="bold")
        for result in report.local_results:
            status = "PASS" if result.passed else "FAIL"
            console.print(
                f"  {status} {result.case_name}: expected={result.expected_trigger}, "
                f"actual={result.actual_trigger}, score={result.trigger_score}"
            )
            console.print(f"    matched_terms: {', '.join(result.matched_terms) or 'none'}")

    if report.llm_results:
        console.print("\nLLM Trigger Check", style="bold")
        for result in report.llm_results:
            status = "PASS" if result.passed else "FAIL"
            if result.error:
                console.print(f"  ERROR {result.case_name}: {result.error}")
                continue
            console.print(
                f"  {status} {result.case_name}: expected={result.expected_trigger}, "
                f"actual={result.actual_trigger}, confidence={result.confidence}"
            )
            if result.reason:
                console.print(f"    reason: {result.reason}")

    if report.local_metrics:
        console.print("\nSummary", style="bold")
        console.print(f"  Local Precision: {report.local_metrics.precision}")
        console.print(f"  Local Recall: {report.local_metrics.recall}")
        console.print(f"  Local F1: {report.local_metrics.f1}")
        console.print(f"  Local Accuracy: {report.local_metrics.accuracy}")

    if report.llm_metrics:
        console.print("\nLLM Summary", style="bold")
        console.print(f"  LLM Precision: {report.llm_metrics.precision}")
        console.print(f"  LLM Recall: {report.llm_metrics.recall}")
        console.print(f"  LLM F1: {report.llm_metrics.f1}")
        console.print(f"  LLM Accuracy: {report.llm_metrics.accuracy}")
        if report.llm_average_confidence is not None:
            console.print(f"  Average Confidence: {report.llm_average_confidence}")

    console.print("\nResult", style="bold")
    console.print("  passed" if report.passed else "  failed")


def render_compare_report(report, console: Console | None = None) -> None:
    console = console or Console()
    console.print("\nRegression Report", style="bold")
    console.print(f"  Baseline: {report.baseline_path}")
    console.print(f"  Total cases: {report.total_cases}")
    console.print(f"  Unchanged: {report.unchanged_cases}")
    console.print(f"  Regressed: {report.regressed_cases}")
    console.print(f"  Improved: {report.improved_cases}")

    if not report.changes:
        console.print("  No behavior changes detected.")
        return

    for change in report.changes:
        if change.current_passed is False and change.previous_passed is not False:
            label = "REGRESSED"
        else:
            label = "CHANGED"
        console.print(
            f"  {label} {change.case_name}: {change.previous_actual} -> {change.current_actual}"
        )

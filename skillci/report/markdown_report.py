from skillci.schema.report import SkillCIReport


def render_markdown(report: SkillCIReport) -> str:
    lines: list[str] = []
    lines.append("# SkillCI Report")
    lines.append("")
    lines.append(f"- Skill: {report.skill_name}")
    lines.append(f"- Path: {report.skill_path}")
    lines.append(f"- Passed: {'true' if report.passed else 'false'}")
    lines.append("")
    lines.append("## Static Health")
    lines.append("")
    if report.static_health.issues:
        for issue in report.static_health.issues:
            lines.append(f"- [{issue.severity}] {issue.code}: {issue.message}")
    else:
        lines.append("No issues found.")
    lines.append("")

    if report.local_results:
        lines.append("## Trigger Check")
        lines.append("")
        lines.append("| Case | Expected | Actual | Passed | Score |")
        lines.append("| --- | --- | --- | --- | --- |")
        for result in report.local_results:
            lines.append(
                f"| {result.case_name} "
                f"| {result.expected_trigger} "
                f"| {result.actual_trigger} "
                f"| {'true' if result.passed else 'false'} "
                f"| {result.trigger_score} |"
            )
        lines.append("")

    if report.llm_results:
        lines.append("## LLM Trigger Check")
        lines.append("")
        lines.append("| Case | Expected | Actual | Passed | Confidence |")
        lines.append("| --- | --- | --- | --- | --- |")
        for result in report.llm_results:
            if result.error:
                lines.append(f"| {result.case_name} | - | - | error | - |")
                continue
            lines.append(
                f"| {result.case_name} "
                f"| {result.expected_trigger} "
                f"| {result.actual_trigger} "
                f"| {'true' if result.passed else 'false'} "
                f"| {result.confidence} |"
            )
        lines.append("")

    if report.local_metrics:
        m = report.local_metrics
        lines.append("## Local Metrics")
        lines.append("")
        lines.append(f"- Precision: {m.precision}")
        lines.append(f"- Recall: {m.recall}")
        lines.append(f"- F1: {m.f1}")
        lines.append(f"- Accuracy: {m.accuracy}")
        lines.append("")

    if report.llm_metrics:
        m = report.llm_metrics
        lines.append("## LLM Metrics")
        lines.append("")
        lines.append(f"- Precision: {m.precision}")
        lines.append(f"- Recall: {m.recall}")
        lines.append(f"- F1: {m.f1}")
        lines.append(f"- Accuracy: {m.accuracy}")
        if report.llm_average_confidence is not None:
            lines.append(f"- Average Confidence: {report.llm_average_confidence}")
        lines.append("")

    if report.judge_disagreements:
        lines.append("## Judge Disagreements")
        lines.append("")
        lines.append(f"Count: {len(report.judge_disagreements)}")
        lines.append("")
        lines.append("| Case | Expected | Local | LLM | Reason |")
        lines.append("| --- | --- | --- | --- | --- |")
        for d in report.judge_disagreements:
            lines.append(
                f"| {d.case_name} "
                f"| {d.expected_trigger} "
                f"| {d.local_actual} "
                f"| {d.llm_actual} "
                f"| {d.reason or '-'} |"
            )
        lines.append("")

    return "\n".join(lines)

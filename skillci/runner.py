from pathlib import Path

from skillci.evaluator.llm_trigger_judge import run_llm_judge
from skillci.evaluator.local_trigger_evaluator import evaluate_local_trigger
from skillci.evaluator.metrics import calculate_metrics
from skillci.lint.runner import run_static_health_checks
from skillci.parser.config_parser import parse_config
from skillci.parser.skill_parser import parse_skill
from skillci.schema.report import SkillCIReport
from skillci.schema.result import JudgeDisagreement, StaticHealthResult


def run_lint(skill_path: Path) -> StaticHealthResult:
    skill = parse_skill(skill_path)
    return run_static_health_checks(skill)


def run_local_test(skill_path: Path, config_path: Path | None = None) -> SkillCIReport:
    skill = parse_skill(skill_path)
    config = parse_config(config_path or skill.path / "skillci.yaml")
    static_health = run_static_health_checks(skill)
    local_results = [
        evaluate_local_trigger(skill, case, config.thresholds)
        for case in config.cases
    ]
    local_metrics = calculate_metrics(local_results)
    passed = static_health.passed and all(result.passed for result in local_results)

    return SkillCIReport(
        skill_name=skill.name,
        skill_path=str(skill.path),
        static_health=static_health,
        local_results=local_results,
        local_metrics=local_metrics,
        passed=passed,
    )


def run_llm_test(
    skill_path: Path,
    config_path: Path | None = None,
    provider_name: str = "openai",
    use_cache: bool = True,
) -> SkillCIReport:
    skill = parse_skill(skill_path)
    config = parse_config(config_path or skill.path / "skillci.yaml")
    static_health = run_static_health_checks(skill)

    llm_results = [
        run_llm_judge(
            skill,
            case,
            config.thresholds,
            provider_name=provider_name,
            judge_config=config.judge,
            use_cache=use_cache,
        )
        for case in config.cases
    ]

    llm_metrics = calculate_metrics(llm_results)
    valid_confidences = [
        result.confidence
        for result in llm_results
        if result.confidence is not None
    ]

    if valid_confidences:
        llm_average_confidence = round(
            sum(valid_confidences) / len(valid_confidences), 4
        )
    else:
        llm_average_confidence = None

    passed = static_health.passed and all(
        result.passed for result in llm_results
    )
    return SkillCIReport(
        skill_name=skill.name,
        skill_path=str(skill.path),
        static_health=static_health,
        llm_results=llm_results,
        llm_metrics=llm_metrics,
        llm_average_confidence=llm_average_confidence,
        passed=passed,
    )


def run_both_test(
    skill_path: Path,
    config_path: Path | None = None,
    provider_name: str = "openai",
    use_cache: bool = True,
) -> SkillCIReport:
    skill = parse_skill(skill_path)
    config = parse_config(config_path or skill.path / "skillci.yaml")
    static_health = run_static_health_checks(skill)

    local_results = [
        evaluate_local_trigger(skill, case, config.thresholds)
        for case in config.cases
    ]

    llm_results = [
        run_llm_judge(
            skill,
            case,
            config.thresholds,
            provider_name=provider_name,
            judge_config=config.judge,
            use_cache=use_cache,
        )
        for case in config.cases
    ]

    local_metrics = calculate_metrics(local_results)
    llm_metrics = calculate_metrics(llm_results)

    valid_confidences = [
        result.confidence for result in llm_results if result.confidence is not None
    ]
    llm_average_confidence = (
        round(sum(valid_confidences) / len(valid_confidences), 4)
        if valid_confidences
        else None
    )

    judge_disagreements = []
    for local, llm in zip(local_results, llm_results, strict=True):
        if llm.error:
            continue
        if local.actual_trigger != llm.actual_trigger:
            judge_disagreements.append(
                JudgeDisagreement(
                    case_name=local.case_name,
                    expected_trigger=local.expected_trigger,
                    local_actual=local.actual_trigger,
                    llm_actual=llm.actual_trigger,
                    local_score=local.trigger_score,
                    llm_confidence=llm.confidence,
                    reason=local.reason,
                )
            )

    passed = static_health.passed and all(r.passed for r in local_results)

    return SkillCIReport(
        skill_name=skill.name,
        skill_path=str(skill.path),
        static_health=static_health,
        local_results=local_results,
        llm_results=llm_results,
        local_metrics=local_metrics,
        llm_metrics=llm_metrics,
        llm_average_confidence=llm_average_confidence,
        judge_disagreement_count=len(judge_disagreements),
        judge_disagreements=judge_disagreements,
        passed=passed,
    )

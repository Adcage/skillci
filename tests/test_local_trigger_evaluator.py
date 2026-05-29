from pathlib import Path

from skillci.evaluator.local_trigger_evaluator import evaluate_local_trigger
from skillci.parser.config_parser import parse_config
from skillci.parser.skill_parser import parse_skill


def test_api_doc_case_triggers_and_sql_case_does_not_trigger():
    skill = parse_skill(Path("examples/api-doc-writer"))
    config = parse_config(Path("examples/api-doc-writer/skillci.yaml"))

    api_case = config.cases[0]
    sql_case = config.cases[2]

    api_result = evaluate_local_trigger(skill, api_case, config.thresholds)
    sql_result = evaluate_local_trigger(skill, sql_case, config.thresholds)

    assert api_result.actual_trigger is True
    assert api_result.passed is True
    assert "api" in api_result.matched_terms
    assert sql_result.actual_trigger is False
    assert sql_result.passed is True

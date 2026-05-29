from skillci.evaluator.metrics import calculate_metrics
from skillci.schema.result import LocalTriggerResult


def make_result(name: str, expected: bool, actual: bool) -> LocalTriggerResult:
    return LocalTriggerResult(
        case_name=name,
        expected_trigger=expected,
        actual_trigger=actual,
        trigger_score=1 if actual else 0,
        passed=expected == actual,
        reason="test",
    )


def test_calculate_metrics():
    metrics = calculate_metrics(
        [
            make_result("tp", True, True),
            make_result("tn", False, False),
            make_result("fp", False, True),
            make_result("fn", True, False),
        ]
    )

    assert metrics.true_positive == 1
    assert metrics.true_negative == 1
    assert metrics.false_positive == 1
    assert metrics.false_negative == 1
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.f1 == 0.5
    assert metrics.accuracy == 0.5

import pytest

from skillci.evaluator.metrics import calculate_metrics
from skillci.schema.result import LLMTriggerResult, LocalTriggerResult


def make_result(name: str, expected: bool, actual: bool) -> LocalTriggerResult:
    return LocalTriggerResult(
        case_name=name,
        expected_trigger=expected,
        actual_trigger=actual,
        trigger_score=1 if actual else 0,
        passed=expected == actual,
        reason="test",
    )


def make_llm_result(name: str, expected: bool, actual: bool) -> LLMTriggerResult:
    return LLMTriggerResult(
        case_name=name,
        expected_trigger=expected,
        actual_trigger=actual,
        confidence=0.9,
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


def test_calculate_metrics_empty_list():
    metrics = calculate_metrics([])

    assert metrics.true_positive == 0
    assert metrics.false_positive == 0
    assert metrics.true_negative == 0
    assert metrics.false_negative == 0
    assert metrics.precision == 0
    assert metrics.recall == 0
    assert metrics.f1 == 0
    assert metrics.accuracy == 0


def test_calculate_metrics_all_correct():
    metrics = calculate_metrics(
        [
            make_result("a", True, True),
            make_result("b", True, True),
            make_result("c", False, False),
            make_result("d", False, False),
        ]
    )

    assert metrics.true_positive == 2
    assert metrics.true_negative == 2
    assert metrics.false_positive == 0
    assert metrics.false_negative == 0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.f1 == 1.0
    assert metrics.accuracy == 1.0


def test_calculate_metrics_all_wrong():
    metrics = calculate_metrics(
        [
            make_result("a", True, False),
            make_result("b", True, False),
            make_result("c", False, True),
            make_result("d", False, True),
        ]
    )

    assert metrics.true_positive == 0
    assert metrics.true_negative == 0
    assert metrics.false_positive == 2
    assert metrics.false_negative == 2
    assert metrics.precision == 0
    assert metrics.recall == 0
    assert metrics.f1 == 0
    assert metrics.accuracy == 0


def test_calculate_metrics_single_result():
    metrics = calculate_metrics([make_result("a", True, True)])

    assert metrics.true_positive == 1
    assert metrics.true_negative == 0
    assert metrics.false_positive == 0
    assert metrics.false_negative == 0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.f1 == 1.0
    assert metrics.accuracy == 1.0


def test_calculate_metrics_only_positives():
    metrics = calculate_metrics(
        [
            make_result("a", True, True),
            make_result("b", True, True),
        ]
    )

    assert metrics.true_positive == 2
    assert metrics.false_negative == 0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0


def test_calculate_metrics_only_negatives():
    metrics = calculate_metrics(
        [
            make_result("a", False, False),
            make_result("b", False, False),
        ]
    )

    assert metrics.true_negative == 2
    assert metrics.false_positive == 0
    assert metrics.accuracy == 1.0


def test_calculate_metrics_with_llm_results():
    metrics = calculate_metrics(
        [
            make_llm_result("a", True, True),
            make_llm_result("b", False, False),
            make_llm_result("c", True, False),
        ]
    )

    assert metrics.true_positive == 1
    assert metrics.true_negative == 1
    assert metrics.false_negative == 1
    assert metrics.accuracy == pytest.approx(2 / 3, rel=0.01)


def test_calculate_metrics_precision_no_false_positives():
    metrics = calculate_metrics(
        [
            make_result("a", True, True),
            make_result("b", True, True),
            make_result("c", False, False),
        ]
    )

    assert metrics.precision == 1.0
    assert metrics.recall == 1.0

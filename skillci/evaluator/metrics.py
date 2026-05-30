from collections.abc import Sequence

from skillci.schema.result import LLMTriggerResult, LocalTriggerResult, TriggerMetrics


def calculate_metrics(
    results: Sequence[LocalTriggerResult | LLMTriggerResult],
) -> TriggerMetrics:
    tp = sum(1 for result in results if result.expected_trigger and result.actual_trigger)
    fp = sum(1 for result in results if not result.expected_trigger and result.actual_trigger)
    tn = sum(1 for result in results if not result.expected_trigger and not result.actual_trigger)
    fn = sum(1 for result in results if result.expected_trigger and not result.actual_trigger)

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    total = len(results)
    accuracy = (tp + tn) / total if total else 0

    return TriggerMetrics(
        true_positive=tp,
        false_positive=fp,
        true_negative=tn,
        false_negative=fn,
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        accuracy=round(accuracy, 4),
    )

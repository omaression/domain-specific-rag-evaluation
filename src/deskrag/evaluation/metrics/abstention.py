"""Abstention decision metrics for WS4."""

from deskrag.core.schemas import CaseResult, RAGAnswer, TestCase

CASE_METRICS = (
    "abstain_correct",
    "false_abstain_rate",
    "missed_abstain_rate",
)


def score_case(
    case: TestCase,
    answer: RAGAnswer,
) -> dict[str, float | None]:
    """Score the decision to answer or abstain for one question."""

    # Broken output is not a decision to answer or abstain, so it is not a correct one. It is
    # neither a false nor a missed abstention, so those two rates leave it out.
    if answer.status != "ok":
        return {"abstain_correct": 0.0, "false_abstain_rate": None, "missed_abstain_rate": None}

    should_abstain = not case.answerable
    correct = answer.abstained == should_abstain

    return {
        "abstain_correct": float(correct),
        "false_abstain_rate": (float(answer.abstained) if case.answerable else None),
        "missed_abstain_rate": (float(not answer.abstained) if not case.answerable else None),
    }


def aggregate(
    rows: list[CaseResult],
) -> dict[str, float | None]:
    """Combine per-question scores into overall abstention metrics."""

    metrics: dict[str, float | None] = {}

    # Average each applicable per-question score.
    for name in CASE_METRICS:
        values: list[float] = []

        for row in rows:
            value = row.scores.get(name)

            if value is not None:
                values.append(value)

        metrics[name] = sum(values) / len(values) if values else None

    # Positive class: the question should be declined.
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    valid_decisions = 0

    for row in rows:
        # Retrieval-only rows have no decision to score; broken output made no decision.
        if row.scores.get("abstain_correct") is None or row.answer.status != "ok":
            continue

        valid_decisions += 1
        false_abstain = row.scores.get("false_abstain_rate")
        missed_abstain = row.scores.get("missed_abstain_rate")

        if false_abstain == 1.0:
            false_positives += 1

        if missed_abstain == 1.0:
            false_negatives += 1
        elif missed_abstain == 0.0:
            true_positives += 1

    if valid_decisions == 0:
        metrics["abstain_precision"] = None
        metrics["abstain_recall"] = None
        metrics["abstain_f1"] = None
        return metrics

    predicted_abstentions = true_positives + false_positives
    actual_unanswerable = true_positives + false_negatives

    # Convention: an undefined precision, recall, or F1 becomes 0.0
    # when valid decisions exist.
    metrics["abstain_precision"] = (
        true_positives / predicted_abstentions if predicted_abstentions else 0.0
    )

    metrics["abstain_recall"] = true_positives / actual_unanswerable if actual_unanswerable else 0.0

    f1_denominator = 2 * true_positives + false_positives + false_negatives
    metrics["abstain_f1"] = 2 * true_positives / f1_denominator if f1_denominator else 0.0

    return metrics

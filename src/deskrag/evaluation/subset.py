"""Pick a fixed subset of the test set by case ID, e.g. the CI subset in configs/ci-llm-cases.txt."""

from pathlib import Path

from deskrag.core.schemas import TestCase


def read_case_ids(path: Path) -> list[str]:
    """One case ID per line. Blank lines and `#` comments are skipped; a repeated ID is an error."""
    ids: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        case_id = line.split("#", 1)[0].strip()
        if not case_id:
            continue
        if case_id in ids:
            raise ValueError(f"{path}:{line_no}: case ID {case_id!r} is listed twice")
        ids.append(case_id)
    if not ids:
        raise ValueError(f"{path}: no case IDs listed")
    return ids


def select_cases(cases: list[TestCase], case_ids: list[str]) -> list[TestCase]:
    """The listed cases, in test-set order. An ID that is not among `cases` is an error."""
    wanted = set(case_ids)
    missing = sorted(wanted - {case.case_id for case in cases})
    if missing:
        raise ValueError(f"case IDs not in the selected split: {', '.join(missing)}")
    return [case for case in cases if case.case_id in wanted]


def pick_balanced(cases: list[TestCase], n: int) -> list[str]:
    """Up to `n` case IDs, sorted.

    Answerable and unanswerable cases alternate, and inside each half the case types take turns,
    so a small subset covers both halves and every type the test set has.
    """
    halves: list[list[str]] = []
    for answerable in (True, False):
        by_type: dict[str, list[str]] = {}
        for case in cases:
            if case.answerable == answerable:
                by_type.setdefault(case.case_type, []).append(case.case_id)
        halves.append(_take_turns([by_type[name] for name in sorted(by_type)], len(cases)))
    return sorted(_take_turns(halves, n))


def _take_turns(queues: list[list[str]], n: int) -> list[str]:
    queues = [list(queue) for queue in queues]
    picked: list[str] = []
    while len(picked) < n and any(queues):
        for queue in queues:
            if queue and len(picked) < n:
                picked.append(queue.pop(0))
    return picked

"""Pick a fixed subset of the test set by case ID, e.g. to re-run only the cases that flipped."""

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

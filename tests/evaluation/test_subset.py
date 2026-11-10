"""Selecting a fixed subset of the test set by case ID."""

import pytest

from deskrag.core.dataset import dataset_sha256
from deskrag.core.schemas import TestCase
from deskrag.evaluation.subset import pick_balanced, read_case_ids, select_cases


def make_case(case_id: str, case_type: str) -> TestCase:
    answerable = case_type in {"single_doc", "multi_doc", "paraphrase"}
    return TestCase(
        case_id=case_id,
        question=f"question {case_id}",
        answerable=answerable,
        case_type=case_type,
        gold_doc_ids=["doc"] if answerable else [],
        reference_answer="reference" if answerable else None,
        must_include=["fact"] if answerable else [],
        split="dev",
        author="test",
    )


CASES = [
    make_case("a1", "single_doc"),
    make_case("a2", "single_doc"),
    make_case("a3", "single_doc"),
    make_case("m1", "multi_doc"),
    make_case("o1", "out_of_domain"),
    make_case("o2", "out_of_domain"),
    make_case("p1", "personal"),
]


def test_read_case_ids_skips_comments_and_blank_lines(tmp_path):
    path = tmp_path / "ids.txt"
    path.write_text("# CI subset\n\na2\nm1  # the multi-doc case\n", encoding="utf-8")
    assert read_case_ids(path) == ["a2", "m1"]


def test_read_case_ids_rejects_a_repeat(tmp_path):
    path = tmp_path / "ids.txt"
    path.write_text("a1\na1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="listed twice"):
        read_case_ids(path)


def test_read_case_ids_rejects_an_empty_list(tmp_path):
    path = tmp_path / "ids.txt"
    path.write_text("# nothing here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no case IDs"):
        read_case_ids(path)


def test_select_cases_keeps_test_set_order():
    assert [case.case_id for case in select_cases(CASES, ["m1", "a2"])] == ["a2", "m1"]


def test_select_cases_rejects_an_unknown_id():
    with pytest.raises(ValueError, match="zz9"):
        select_cases(CASES, ["a1", "zz9"])


def test_a_new_case_does_not_change_the_subset_fingerprint():
    before = dataset_sha256(select_cases(CASES, ["a1", "o1"]))
    grown = [*CASES, make_case("a4", "single_doc")]
    assert dataset_sha256(select_cases(grown, ["a1", "o1"])) == before


def test_pick_balanced_alternates_halves_and_rotates_types():
    # answerable order: m1, a1, a2, a3; unanswerable order: o1, p1, o2
    assert pick_balanced(CASES, 4) == ["a1", "m1", "o1", "p1"]


def test_pick_balanced_returns_everything_when_asked_for_more():
    assert pick_balanced(CASES, 99) == ["a1", "a2", "a3", "m1", "o1", "o2", "p1"]

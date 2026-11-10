"""The CI LLM gate's config and frozen case list must stay valid as the test set changes."""

from pathlib import Path

from deskrag.core.config import load_config
from deskrag.core.dataset import load_cases
from deskrag.evaluation.subset import read_case_ids, select_cases

REPO = Path(__file__).resolve().parents[1]


def test_ci_subset_lists_only_committed_dev_cases():
    ids = read_case_ids(REPO / "configs" / "ci-llm-cases.txt")
    cases = select_cases(load_cases(REPO / "data" / "testset", split="dev"), ids)
    assert len(cases) == len(ids)
    assert len(ids) >= 20
    assert {case.answerable for case in cases} == {True, False}


def test_ci_llm_config_is_a_rag_system_with_a_model():
    cfg = load_config(REPO / "configs" / "ci-llm.yaml")
    assert cfg.system == "rag"
    assert cfg.llm is not None

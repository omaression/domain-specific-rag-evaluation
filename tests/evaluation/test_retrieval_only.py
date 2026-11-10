"""Retrieval-only runs: the retriever is scored and the LLM is never called."""

from pathlib import Path

import pytest

from deskrag.core.config import SystemConfig
from deskrag.core.runio import read_json
from deskrag.core.schemas import Chunk, RetrievedChunk, RunMeta, TestCase
from deskrag.evaluation.metrics import retrieval
from deskrag.evaluation.retrieval_only import NO_ANSWER_NOTE, RetrievalOnlySystem
from deskrag.evaluation.runner import run_cases, score_response

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "samples"


class StubRetriever:
    """Returns the documents listed for each question, best first."""

    def __init__(self, ranking: dict[str, list[str]]):
        self.ranking = ranking

    def retrieve(self, query: str, k: int) -> list[RetrievedChunk]:
        docs = self.ranking[query][:k]
        return [
            RetrievedChunk(
                chunk=Chunk(chunk_id=f"{doc}#0", doc_id=doc, title=doc, text="text", position=0),
                score=float(len(docs) - index),
                rank=index + 1,
            )
            for index, doc in enumerate(docs)
        ]


def make_case(case_id: str, gold: list[str]) -> TestCase:
    answerable = bool(gold)
    return TestCase(
        case_id=case_id,
        question=f"question {case_id}",
        answerable=answerable,
        case_type="single_doc" if answerable else "out_of_domain",
        gold_doc_ids=gold,
        reference_answer="reference" if answerable else None,
        must_include=["fact"] if answerable else [],
        split="dev",
        author="test",
    )


HIT = make_case("hit", ["wifi"])
MISS = make_case("miss", ["parking"])
UNANSWERABLE = make_case("none", [])
RANKING = {
    HIT.question: ["library", "wifi", "transcripts"],
    MISS.question: ["library", "wifi", "transcripts"],
    UNANSWERABLE.question: ["library", "wifi", "transcripts"],
}


@pytest.fixture
def system():
    return RetrievalOnlySystem(StubRetriever(RANKING), k=3)


def test_system_returns_chunks_and_never_calls_an_llm():
    answer = RetrievalOnlySystem(StubRetriever(RANKING), k=2).answer(HIT.question)
    assert [hit.chunk.doc_id for hit in answer.retrieved] == ["library", "wifi"]
    assert answer.answer == NO_ANSWER_NOTE
    assert answer.confidence == 2.0
    assert answer.usage.llm_calls == 0
    assert answer.model is None


def test_a_hit_passes_and_has_only_retrieval_scores(system):
    row = score_response("r", HIT, system.answer(HIT.question), retrieval_only=True)
    assert set(row.scores) == set(retrieval.METRIC_NAMES)
    assert row.scores["hit@1"] == 0.0
    assert row.scores["hit@3"] == 1.0
    assert row.scores["mrr"] == 0.5
    assert row.passed
    assert row.failure_tags == []


def test_a_miss_fails_with_the_retrieval_tag(system):
    row = score_response("r", MISS, system.answer(MISS.question), retrieval_only=True)
    assert row.scores["hit@5"] == 0.0
    assert not row.passed
    assert row.failure_tags == ["RETRIEVAL_MISS"]


def test_an_unanswerable_case_has_nothing_to_score(system):
    row = score_response(
        "r", UNANSWERABLE, system.answer(UNANSWERABLE.question), retrieval_only=True
    )
    assert all(value is None for value in row.scores.values())
    assert row.passed
    assert row.failure_tags == []


def test_run_records_the_mode_and_leaves_ollama_alone(system, tmp_path, monkeypatch):
    # Nothing listens on port 9, so any call to Ollama would fail this test.
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:9")
    config = SystemConfig(
        name="retrieval-only-test",
        system="rag",
        corpus_dir=str(SAMPLES / "corpus"),
        retrieval={"method": "fake", "k": 3},
        llm={"model": "never-called"},
    )
    target = tmp_path / "run"

    summary = run_cases(
        "r", [HIT, MISS, UNANSWERABLE], system, target, config=config, retrieval_only=True
    )

    meta = read_json(target / "meta.json", RunMeta)
    assert meta.config["retrieval_only"] is True
    assert meta.env.model_digests == {}
    assert summary.metrics["hit@5"] == 0.5
    assert summary.metrics["mrr"] == 0.25
    assert summary.metrics["e2e_pass"] is None
    assert summary.metrics["abstain_correct"] is None
    assert summary.failure_counts == {"RETRIEVAL_MISS": 1}
    assert summary.counts.cases == 3
    assert summary.counts.errors == 0


def test_resume_refuses_to_mix_full_and_retrieval_only(system, tmp_path):
    config = SystemConfig(name="mix", system="fake", corpus_dir=str(SAMPLES / "corpus"))
    target = tmp_path / "run"
    run_cases("r", [HIT], system, target, config=config, retrieval_only=True)

    with pytest.raises(ValueError, match="Cannot resume: retrieval_only"):
        run_cases("r", [HIT], system, target, config=config, resume=True)

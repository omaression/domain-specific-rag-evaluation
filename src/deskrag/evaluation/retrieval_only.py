"""Retrieval-only evaluation: run the retriever and skip the LLM.

`eval run --retrieval-only` uses this for the CI retrieval gate, which has no Ollama. Each case
gets its retrieved chunks and a fixed note where the answer would be. The runner scores these
runs with the retrieval metrics only, so the note is never read as an answer.
"""

import time
from dataclasses import dataclass

from deskrag.core.interfaces import Retriever
from deskrag.core.schemas import RAGAnswer, Usage

NO_ANSWER_NOTE = "(retrieval-only run: no answer was generated)"


@dataclass
class RetrievalOnlySystem:
    retriever: Retriever
    k: int = 5

    def answer(self, question: str) -> RAGAnswer:
        start = time.perf_counter()
        retrieved = self.retriever.retrieve(question, self.k)
        return RAGAnswer(
            question=question,
            abstained=False,
            answer=NO_ANSWER_NOTE,
            retrieved=retrieved,
            confidence=retrieved[0].score if retrieved else None,
            usage=Usage(latency_s=time.perf_counter() - start),
        )

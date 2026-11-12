# Design

## Goal

1. **System under test:** a university help-desk chatbot. It answers from a frozen snapshot of our university's public help pages and **abstains** when the pages don't contain the answer.
2. **Main project:** our own evaluation harness. It runs a labeled test set through the chatbot, scores retrieval, abstention, and answer quality, tags every failure, and detects regressions when a prompt, code, or model change makes things worse.

## Decisions

| Topic | Decision |
|---|---|
| LLM | Local [Ollama](https://ollama.com), free. A small instruct model (~3–4B, Q4) picked by a Day-1 bake-off and pinned by tag; each run records the model digest. Settings: temperature 0, fixed seed, thinking off, and JSON-schema-constrained output (`format=`). |
| Embeddings | Ollama embedding model, default `nomic-embed-text`. |
| Domain | 177 public help pages, snapshotted once. Frozen and fingerprinted, respecting robots.txt. |
| Stack | Python 3.12 + uv; `ollama`, `rank-bm25`, `numpy`, `pydantic`, `pyyaml`, `typer`; `pytest`, `ruff`. No LangChain, RAGAS, torch, or scipy. The evaluation system is ours, so it stays small and inspectable. |
| Deadline | Two to four weeks after Nov 9, since the move to the harness topic. The plan is in [harness-pivot.md](harness-pivot.md#order-of-work). The October plan, due ≈ Thu Oct 29, is in [workplan.md](workplan.md). |

## Architecture

```
data/corpus/docs/*.md → chunk → index (BM25 | dense | hybrid) → Retriever.retrieve(q, k) → RetrievedChunk[] (+scores)

question → RAGSystem.answer(q):
   top score < gate τ ? ──yes──► RAGAnswer(abstained, reason=low_retrieval_score)     (no LLM call)
        │ no
   prompt vN + context blocks "[doc_id] title\ntext" → Ollama chat, JSON {abstain, answer, citations}
        ▼
   RAGAnswer(answer | abstained with reason=model_declined, cited_doc_ids, retrieved, usage, status)

data/testset/*.jsonl → eval runner → runs/<run_id>/{meta.json, results.jsonl, errors.jsonl, summary.json, report.md}
                                          │
             baselines/<name>/ ◄── promote ┼──► compare(baseline, candidate) → verdicts + McNemar + flipped cases → exit code
```

The harness talks to the chatbot only through `RAGSystem.answer()`, so it treats it as a black box. On Day 1 it runs against `FakeRAGSystem` (`configs/fake.yaml`); later it runs against the real pipeline (`configs/baseline.yaml`).

## Shared contracts (`src/deskrag/core/`, frozen)

The code is the source of truth. This is a map.

| Module | Provides |
|---|---|
| `schemas.py` | `Document`, `Chunk`, `RetrievedChunk`, `LLMResponse`, `RAGAnswer`, `Usage`, `TestCase`, `CaseResult`, `ErrorRow`, `RunMeta`, `RunSummary`, `FailureTag`, `METRIC_DIRECTION` |
| `interfaces.py` | Protocols `Retriever.retrieve(query, k)`, `LLMClient.chat(messages, json_schema=, options=)`, `RAGSystem.answer(question)`; `InfraError` |
| `config.py` | `SystemConfig` (YAML with `extends:`), `load_config`, `config_hash` (settings minus `name`, plus the prompt text) |
| `corpus.py` | `load_corpus`, `load_document` (front-matter markdown), `corpus_sha256` |
| `dataset.py` | `load_cases(file_or_dir, split=)`, `dataset_sha256` (covers only the selected split) |
| `runio.py` | `make_run_id`, `RunPaths`, `append_jsonl` / `read_jsonl`, `write_json` / `read_json` |
| `env.py` | `basic_fingerprint()` (machine, platform, python), `git_info()` |
| `fakes.py` | `FakeRetriever`, `FakeLLM`, `FakeRAGSystem` (canned outcomes for `data/samples`; see its docstring) |
| `../systems.py` | `build_system(cfg, cases=)` dispatches on `cfg.system`: `rag` / `closed_book` (WS3), `oracle` / `always_abstain` / `never_abstain` (WS4), `fake` (core) |

Key rules, all enforced by validators and tests:
- **Chunk ids** are always `f"{doc_id}#{position}"`, so any chunk maps back to its document.
- **"No answer" ≠ "abstained."**
  - An abstention is deliberate and well-formed: `abstained=True` with `abstain_reason` set, no `answer`, and `status="ok"`.
  - Broken model output is `status="truncated"` or `status="parse_error"`. It is never counted as an abstention.
  - Plumbing failures (Ollama down, timeouts) raise `InfraError`. The runner logs them to `errors.jsonl` and never scores them.
- **Test-case labels are consistent.**
  - `case_type` must agree with `answerable`.
  - Answerable cases have gold docs, a reference answer, and at least one `must_include` fact; unanswerable cases have none of these.
  - Unknown fields are rejected.

## Abstention

Two layers, which can be compared as an experiment:
1. **Retrieval-score gate.** If the top retrieval score is below `abstention.min_score`, abstain with `low_retrieval_score` and skip the LLM call. The scale depends on the retriever, so re-tune it whenever the retriever changes. `deskrag eval sweep` recomputes precision/recall for every threshold from a gate-off run, with no new LLM calls.
2. **Model abstention.** The prompt tells the model to answer only from context and to return `{"abstain": true}` otherwise, giving `model_declined`. Ollama's JSON-schema `format` keeps the output parseable.

`RAGAnswer.confidence` holds the top retrieval score. A risk-coverage curve built from it is a stretch goal.

## Test set

- Files: `data/testset/<author>.jsonl` (format and rules in [data/testset/README.md](../data/testset/README.md)).
- Size: 60 dev cases, frozen since 2026-11-11: 34 answerable and 26 unanswerable. The October plan was ~150 cases with at least 10 of every `case_type`. Types:
  - Answerable: `single_doc`, `multi_doc`, `paraphrase`.
  - Unanswerable: `out_of_domain`, `missing_info` (in-domain but absent from the corpus; the hardest), `false_premise`, `personal`.
- Split: every case is `dev`. The October plan had a stratified ~100 dev / ~50 test split. The harness topic dropped the test split, because its claim is about the gate, not the bot's final score.
- Quality:
  - `deskrag data validate` checks that gold docs exist and that every fact appears in a gold doc.
  - A blind second label on 20% of the cases (about 12 of the 60), with agreement reported, still needs a teammate.
  - Small local models rarely know our university's specifics, so the test measures retrieval rather than memory. The closed-book planted run checks this: without retrieval, e2e_pass fell from 0.78 to 0.22 ([harness-pivot.md](harness-pivot.md#1-detection)).

## Metrics

Per-case scores go in `CaseResult.scores`, where `None` means "not applicable". Aggregates go in `RunSummary.metrics`. Names and their better direction live in `METRIC_DIRECTION`.

| Metric | Over | Definition |
|---|---|---|
| `hit@1`, `hit@3`, `hit@5`, `recall@5`, `mrr` | answerable | gold doc(s) in the top-k **doc-level** ranking (chunks de-duplicated by doc, first occurrence wins) |
| `abstain_correct` | all | per case: `abstained == not answerable`; a truncated or unparsable reply scores 0 |
| `abstain_precision`, `abstain_recall`, `abstain_f1` | all (positive class = should abstain) | confusion matrix of abstained vs unanswerable; truncated and parse errors are excluded and counted separately |
| `false_abstain_rate` | answerable | abstained on an answerable question (over-refusal) |
| `missed_abstain_rate` | unanswerable | answered when it should have abstained (hallucination) |
| `fact_recall`, `answer_correct` | answerable ∧ answered | share of `must_include` facts in the answer (lowercased, whitespace collapsed, any `\|` alternative counts); `answer_correct` means all of them are present |
| `citation_valid`, `citation_hit` | answered | cited ⊆ retrieved docs; cited ∩ gold ≠ ∅ |
| **`e2e_pass`** (headline) | all | answerable: answered ∧ status ok ∧ `answer_correct`. Unanswerable: abstained |
| `format_error_rate`, `latency_p50_s`, `latency_p95_s`, `prompt_tokens_mean`, `completion_tokens_mean` | all | from `status` and `usage` |

**Failure tags** (`FailureTag`), with several allowed per case:
- `RETRIEVAL_MISS`
- `FALSE_ABSTAIN_GATE`
- `FALSE_ABSTAIN_MODEL`
- `MISSED_ABSTAIN`
- `WRONG_ANSWER`
- `BAD_CITATION`
- `FORMAT_ERROR`

**Sanity systems** (WS4) test the harness itself:
- `oracle` must score about 100%.
- `always_abstain` and `never_abstain` are the two degenerate policies. Reports show them as reference lines, and a real system has to beat both.

## Run files

```
runs/<run_id>/                 run_id = <UTC yyyymmdd-hhmmss>-<config name>-<config hash[:8]>
    meta.json      RunMeta     config, config_hash, git sha + dirty flag, dataset and corpus fingerprints, machine, Ollama version, model digests
    results.jsonl  CaseResult  one row per (case, rep), appended as each case finishes; resume skips rows already written
    errors.jsonl   ErrorRow    attempts that never produced a scorable answer (timeout / infra / exception)
    summary.json   RunSummary  aggregate metrics, by case_type, counts, failure counts
    report.md                  human-readable report (WS5)
```

## Regression detection

`deskrag compare BASE CAND`:
1. **Refuses** (exit 2) unless the two runs pair up case by case: the same dataset fingerprint and split, the same case IDs, the same corpus fingerprint, and one repetition each. It also refuses a run with infra errors or missing cases. **Warns** if the machine or model digests differ, because Ollama output can vary across hardware. Official baselines and comparisons run on one reference machine (set `DESKRAG_MACHINE=reference`).
2. Compares each metric's delta with its tolerance in `configs/regression.yaml`, taking the better direction from `METRIC_DIRECTION`.
3. Runs an **exact McNemar test** on the paired per-case booleans (`e2e_pass`, `hit@5`, `abstain_correct`, …), in pure Python with `math.comb`.
4. Assigns each metric a verdict:
   - `REGRESSION`: worse than the tolerance **and** p < 0.05.
   - `POSSIBLE`: worse than the tolerance, but not significant.
   - `OK` or `IMPROVED`.
5. Lists flipped cases (pass→fail and fail→pass) with their failure tags, writes `compare.md`, and exits 1 on any gated `REGRESSION`.

The gated metrics are `e2e_pass`, `hit@5`, and `abstain_correct`, each with tolerance 0.05. At alpha 0.05, a gated metric needs at least 6 pass-to-fail flips with none the other way before it can be a `REGRESSION` (p = 0.03125); 5 give p = 0.0625. The [results tables](harness-pivot.md#results-tables) show what this means on the 60 dev cases.

**Baselines** come from `make record` (`deskrag baseline record`) on the reference machine. It runs the dev split with and without the LLM and replaces `baselines/dev` and `baselines/dev-retrieval`. It refuses to run with uncommitted changes, so each recording matches a commit, and it replaces nothing unless both runs are complete and have no infra errors. A PR that changes anything a recording depends on (the pipeline code, its config or prompt, the cases, or the corpus) commits a new recording. [baselines/README.md](../baselines/README.md) has the rule for each kind of change.

**CI** never calls a model. It runs four jobs on every pull request and on every push to main:
- `test`: ruff, the format check, and pytest. Pytest also validates the committed configs, corpus files, and test cases.
- `regression-contract`: `compare` on two fixture runs. An unchanged run must pass, and a planted candidate must exit 1.
- `retrieval-gate`: runs BM25 again on the runner and compares it with `baselines/dev-retrieval` under `baselines/retrieval-gates.yaml`, where hit@5 and hit@1 are gated. Then it checks that recording the way `llm-gate` checks `baselines/dev`.
- `llm-gate`: `deskrag baseline check` on `baselines/dev`, which takes seconds. It fails if the recording is out of date (the pipeline code, the config or its prompt, the corpus, or the cases changed since it was recorded), if scoring the recorded answers again does not give the committed scores, or if the recording is a gated regression against the base branch's copy.

The base branch's copy is not always comparable. When the cases, the corpus, or the recording machine changed, the check accepts the new recording without a comparison, and the reviewer reads the new numbers. A change to more than one of system, data, and machine fails. A PR that changes none of them keeps the base branch's recording and passes.

On the fork's main, branch protection requires all four jobs, admins included. The team repo's main is not protected yet; only its owner can turn that on. `make regress` runs the dev split and compares it with `baselines/dev` without changing anything, so an author can see the verdict before recording. [harness-pivot.md](harness-pivot.md#why-ci-does-not-run-the-model) says why CI checks a recording instead of running the model.

## Configs

`configs/baseline.yaml` is the reference system. Experiments live in `configs/experiments/<name>.yaml`, start with `extends: ../baseline.yaml`, and override only what differs (example: `k3.yaml`). `config_hash` covers every setting except `name`, plus the text of `src/deskrag/rag/prompts/<prompt_version>.md`, so editing a prompt changes the fingerprint.

## CLI

| Command | Module | Owner |
|---|---|---|
| `data snapshot`, `data validate` | `commands/data.py` | WS1 |
| `index build`, `retrieve` | `commands/retrieval.py` | WS2 |
| `ask` | `commands/ask.py` | WS3 |
| `eval run`, `eval sweep` | `commands/evaluate.py` | WS4 |
| `compare`, `regress`, `report`, `baseline record`, `baseline check`, `baseline promote`, `runs list`, `runs table`, `runs resample` | `commands/regress.py` | WS5 |

## Known limitations (for the report)

- Small local models make more mistakes. That is good for an eval project, because it leaves room to measure.
- With 60 dev cases, a gated metric has to lose at least 6 cases with none gained (or 8 with 1 gained, or 10 with 2) before the gate can block it. Two planted regressions, `no-abstain` and `chunk50`, got through ([harness-pivot.md](harness-pivot.md#1-detection)).
- CI trusts whoever records. It can prove that a recording matches the code and data and that nobody edited the scores, but not that the answers came from the model.
- A PR that changes the cases or the corpus is accepted without a comparison, so the reviewer is the only check on it.
- Outputs can differ across hardware even at temperature 0, so comparisons should stay on one machine.
- `must_include` matching is lexical. A correct paraphrase of a number or name can be scored as wrong. An LLM judge calibrated against human labels is a stretch goal.

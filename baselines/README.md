# Baselines

Runs of the dev split, recorded on the reference machine and committed. CI never calls a model: it checks these recordings instead.

| Baseline | What it is | Checked by |
|---|---|---|
| `dev/` | Full pipeline, every dev case (`configs/baseline.yaml`) | CI `llm-gate`, and `make regress` locally |
| `dev-retrieval/` | BM25, retrieval only, every dev case (`configs/ci-retrieval.yaml`) | CI `retrieval-gate`, which runs BM25 again on the runner |

Each folder holds the run's files plus `source.json`, the fingerprint of the pipeline code it ran on. `retrieval-gates.yaml` holds the tolerances for the retrieval gate; `llm-gate` uses `configs/regression.yaml`.

## Recording

On the reference machine (Omar's Mac, Ollama 0.40.3), with Ollama running, `DESKRAG_LLM_CACHE` unset, and nothing uncommitted:

```bash
make record
git add baselines
git commit -m "Record baselines"
```

`make record` runs the dev split twice, with and without the LLM, and replaces both folders. It takes about 3 minutes for 26 cases. If either run fails, nothing is replaced.

To see what a change does before recording it, run `make regress`. It compares a fresh run with `baselines/dev` and changes nothing.

## What `llm-gate` checks

`deskrag baseline check` runs in seconds and answers three questions:

1. **Is the recording fresh?** It recomputes four fingerprints and compares them with the recording: the pipeline code (`src/deskrag/core`, `src/deskrag/rag`, `src/deskrag/systems.py`, `uv.lock`), the config and its prompt, the corpus, and the dev cases. If any differ, the check fails and names which.
2. **Are the scores honest?** It scores the recorded answers again. The result must equal the committed scores.
3. **Is it worse?** It compares the recording with the base branch's `baselines/dev`. A gated regression fails the check.

## What each kind of change needs

| The change touches | What to do | What the gate does |
|---|---|---|
| Docs, tests, CI files, or code outside the pipeline | Nothing | Passes: same recording as the base branch |
| Pipeline code, the config, or the prompt | `make record` | Compares with the base branch; fails on a gated regression |
| Cases or the corpus | `make record` | Passes without a comparison, because the runs are on different data. Review the new numbers |
| A new reference machine | `make record` on it | Passes without a comparison, for the same reason |
| More than one of the last three | Split the pull request | Fails |

## What the gate cannot check

That the recorded answers came from the model. CI trusts the person who recorded. It can only prove the recording matches this code and data and that nobody edited the scores.

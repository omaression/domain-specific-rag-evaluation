# Baselines

Recorded runs that `deskrag compare` and CI measure new runs against. Each folder is a promoted run (`deskrag baseline promote`).

| Baseline | What it is | Recorded on | Used by |
|---|---|---|---|
| `dev-retrieval/` | BM25, retrieval only, every dev case (`configs/ci-retrieval.yaml`) | any machine; no Ollama | CI `retrieval-gate` |

`retrieval-gates.yaml` holds the tolerances for the retrieval gate. The other gates use `configs/regression.yaml`.

## When a baseline must be re-recorded

`compare` refuses to compare runs whose dataset or corpus fingerprint differs. So a PR that adds, edits, or removes a dev case, or changes a corpus page, must re-record every baseline that covers it, in the same PR. `promote` never overwrites, so remove the old folder first.

### `dev-retrieval`

```bash
git rm -r -q baselines/dev-retrieval
DESKRAG_MACHINE=reference uv run deskrag eval run --config configs/ci-retrieval.yaml --split dev --retrieval-only --run-dir runs/dev-retrieval-baseline
uv run deskrag baseline promote runs/dev-retrieval-baseline --name dev-retrieval
git add baselines/dev-retrieval
```

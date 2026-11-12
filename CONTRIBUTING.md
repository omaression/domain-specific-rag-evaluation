# Contributing

Five people, five branches, three weeks. These rules keep `main` green and merges painless.

## Branches

| Branch | Workstream |
|---|---|
| `feat/data` | WS1: corpus snapshot and test set |
| `feat/retrieval` | WS2: chunking and retrievers |
| `feat/generation` | WS3: LLM client, prompts, abstention, `deskrag ask` |
| `feat/eval-metrics` | WS4: runner, metrics, failure tags, sanity systems |
| `feat/regression-ci` | WS5: compare, reports, baselines, CI |

Owners are listed in [docs/workplan.md](docs/workplan.md).

## Daily loop

```bash
git switch feat/<yours>
git pull
git merge origin/main       # pick up teammates' merged work; do this every day
# ...work, commit in small steps...
uv run ruff format . && uv run ruff check . && uv run pytest
git push
```

## Rules

1. **Stay in your lane.** Only edit the paths your workstream owns (see the table below). If you need a change somewhere else, ask its owner or open an issue.
2. **Merge early and often.** Open your first PR within 2–3 days, then merge at least every 2–3 days. PRs are squash-merged. Keep working on the same branch after a merge.
3. **Contracts are frozen.** `src/deskrag/core/`, `systems.py`, `cli.py`, `pyproject.toml`, and `uv.lock` change only through a small `contract/<what>` PR. It needs 2 reviewers, including the owners of the affected workstreams. Merge it the same day and announce it in the group chat.
4. **A new dependency gets its own tiny PR** (`uv add <package>`), so `uv.lock` never conflicts.
5. **Record the eval impact.** A PR that changes anything the recordings depend on (the pipeline code, `configs/baseline.yaml` or `configs/ci-retrieval.yaml`, the prompt, the cases, or the corpus) includes a new recording: run `make record` on the reference machine and commit `baselines/`. CI's `llm-gate` and `retrieval-gate` compare it with the base branch's and fail on a gated regression. [baselines/README.md](baselines/README.md) has the details.
6. **Test cases go in your own file**, `data/testset/<your-name>.jsonl`, with case ids prefixed by your initials. See [data/testset/README.md](data/testset/README.md).
7. **There is no test split.** The harness topic dropped it, so every case is `dev`. The gate settings in `configs/regression.yaml` stay frozen for the experiment ([docs/harness-pivot.md](docs/harness-pivot.md#the-experiment)).

## File ownership

| Paths | Owner |
|---|---|
| `src/deskrag/core/**`, `src/deskrag/systems.py`, `src/deskrag/cli.py`, `pyproject.toml`, `uv.lock` | shared (contract PR) |
| `data/corpus/**`, `src/deskrag/data/**`, `src/deskrag/commands/data.py`, `docs/authoring-guide.md` | WS1 |
| `data/testset/<name>.jsonl` | each author (WS1 reviews) |
| `src/deskrag/rag/chunking.py`, `src/deskrag/rag/retrieval/**`, `src/deskrag/commands/retrieval.py` | WS2 |
| `src/deskrag/rag/{llm/**, prompts/**, pipeline.py, abstention.py, closed_book.py}`, `src/deskrag/commands/ask.py`, `configs/baseline.yaml` | WS3 |
| `src/deskrag/evaluation/{runner.py, metrics/**, failures.py, sanity.py}`, `src/deskrag/commands/evaluate.py` | WS4 |
| `src/deskrag/evaluation/{compare.py, stats.py, report.py, baseline.py}`, `src/deskrag/commands/regress.py`, `configs/{regression,ci-retrieval}.yaml`, `baselines/**`, `.github/**`, `Makefile` | WS5 |
| `configs/experiments/<name>.yaml` | anyone (one file per experiment) |
| `tests/<area>/` | same owner as the code it tests |

Recordings: WS3 runs `make record` on the reference machine and commits `baselines/`; WS5 reviews the diff.

## For the repo owner: protect `main`

In Settings → Branches, add a rule for `main`:
- require a pull request with 1 approval
- require the four CI checks to pass (`test`, `regression-contract`, `retrieval-gate`, `llm-gate`), and include administrators
- allow squash merging

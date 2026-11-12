## What changed

<!-- One or two sentences. Which workstream (WS1–WS5)? -->

## How I tested it

- [ ] `uv run pytest` passes
- [ ] `uv run ruff check . && uv run ruff format --check .` pass

## Eval impact

<!-- Required if this PR changes anything the recordings depend on (pipeline code,
configs/baseline.yaml or configs/ci-retrieval.yaml, a prompt, the cases, or the corpus):
commit a new recording from `make record` on the reference machine (see baselines/README.md)
and say what changed. CI's llm-gate summary shows the comparison. Otherwise write "none". -->

## Contract change?

- [ ] This PR changes `src/deskrag/core/`, `systems.py`, `cli.py`, `pyproject.toml`, or `uv.lock`
      (needs 2 reviewers, including the owners of affected workstreams)

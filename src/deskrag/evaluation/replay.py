"""Replay gate: check a recorded run in CI without calling a model.

GitHub-hosted runners are too slow and too uneven to run the model on every pull request
(docs/harness-pivot.md has the measurements). So the full dev run is recorded on the reference
machine with `deskrag baseline record` and committed under baselines/. CI then runs
`deskrag baseline check`, which answers three questions:

1. Fresh? The pipeline code, config and prompt, corpus, and cases still match what was recorded.
2. Honest? Re-scoring the recorded answers gives the committed scores.
3. Worse? Compared with the base branch's recording, is there a gated regression?

A change can alter one of three things: the system (code, config, prompt), the data (cases,
corpus), or the recording machine. Paired comparison needs the other two fixed, so a change to the
data or the machine is accepted without a comparison, and a change to more than one is rejected.

CI cannot check that the recorded answers came from the model. That part is trusted.
"""

import json
import shutil
import tempfile
from pathlib import Path

from deskrag.core.config import config_hash, load_config
from deskrag.core.corpus import corpus_sha256
from deskrag.core.dataset import dataset_sha256, load_cases
from deskrag.core.env import git_info
from deskrag.core.hashing import sha256_text_files
from deskrag.core.runio import RunPaths, write_json
from deskrag.core.schemas import CaseResult, RunSummary, TestCase
from deskrag.evaluation.baseline import evaluate_candidate, promote_baseline
from deskrag.evaluation.compare import RecordedRun, compare_runs, load_run, require_complete
from deskrag.evaluation.runner import score_response, summarize

# What produces an answer: the pipeline, the shared contracts it is built on, and the pinned
# dependencies. Prompts are covered by the config hash. Scoring code is not listed because
# `check_baseline` re-scores the answers, which catches any scoring change that matters.
CODE_PATHS = ("src/deskrag/core", "src/deskrag/rag", "src/deskrag/systems.py", "uv.lock")
SOURCE_FILE = "source.json"
RECORDINGS = (
    ("dev", Path("configs/baseline.yaml"), False),
    ("dev-retrieval", Path("configs/ci-retrieval.yaml"), True),
)
HOW_TO_RECORD = "Run `make record` on the reference machine and commit baselines/."


def code_sha256(repo: Path = Path("."), paths: tuple[str, ...] = CODE_PATHS) -> str:
    """Fingerprint of the files that produce an answer: `.py` files under each directory in
    `paths`, plus each file listed directly."""
    files: list[Path] = []
    for entry in paths:
        path = repo / entry
        if path.is_dir():
            files += path.rglob("*.py")
        elif path.is_file():
            files.append(path)
        else:
            raise ValueError(f"Cannot fingerprint the code: {path} is missing")
    return sha256_text_files(files, repo)


def write_source(baseline_dir: Path, repo: Path = Path(".")) -> None:
    """Store the code fingerprint next to a recorded run."""
    record = {"code_sha256": code_sha256(repo), "code_paths": list(CODE_PATHS)}
    (baseline_dir / SOURCE_FILE).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def recorded_code_sha256(baseline_dir: Path) -> str | None:
    path = baseline_dir / SOURCE_FILE
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("code_sha256")


def rescore(run: RecordedRun, cases: list[TestCase]) -> tuple[list[CaseResult], RunSummary]:
    """Score a run's recorded answers again with the current scoring code."""
    by_id = {case.case_id: case for case in cases}
    retrieval_only = bool(run.meta.config.get("retrieval_only"))
    rows = []
    for row in run.rows.values():
        if row.case_id not in by_id:
            raise ValueError(f"{run.path}: case {row.case_id!r} is not in the test set")
        rows.append(
            score_response(
                run.meta.run_id,
                by_id[row.case_id],
                row.answer,
                rep=row.rep,
                retrieval_only=retrieval_only,
            )
        )
    ran = {row.case_id for row in rows}
    scored = [case for case in cases if case.case_id in ran]
    return rows, summarize(run.meta.run_id, rows, [], cases=scored)


def _write_rescored(run: RecordedRun, cases: list[TestCase], dest: Path) -> None:
    rows, summary = rescore(run, cases)
    paths = RunPaths(dest)
    write_json(paths.meta, run.meta)
    write_json(paths.summary, summary)
    paths.results.write_text(
        "".join(row.model_dump_json() + "\n" for row in rows), encoding="utf-8"
    )
    paths.errors.touch()


def _stale_reasons(head: RecordedRun, cfg, cases: list[TestCase], repo: Path) -> list[str]:
    reasons = []
    recorded_code = recorded_code_sha256(head.path)
    if recorded_code is None:
        reasons.append(f"it has no code fingerprint ({SOURCE_FILE})")
    elif recorded_code != code_sha256(repo):
        reasons.append("the pipeline code changed")
    if head.meta.config_hash != config_hash(cfg):
        reasons.append("the config or its prompt changed")
    if head.meta.corpus is None or head.meta.corpus.sha256 != corpus_sha256(cfg.corpus_dir):
        reasons.append("the corpus changed")
    if head.meta.dataset.sha256 != dataset_sha256(cases):
        reasons.append("the dev cases changed")
    return reasons


def check_baseline(
    head_dir: Path,
    config_path: Path,
    cases_path: Path,
    base_dir: Path | None,
    gates_path: Path,
    repo: Path = Path("."),
) -> tuple[str, bool]:
    """Check the recorded run in `head_dir` and compare it with the base branch's copy.

    Returns the report and whether a gated regression blocks the change. Raises ValueError when
    the recording is stale, its scores were not produced by the scoring code, or the change
    alters more than one of system, data, and machine.
    """
    head = load_run(head_dir)
    require_complete(head)
    cfg = load_config(config_path)
    cases = load_cases(cases_path, split="dev")

    reasons = _stale_reasons(head, cfg, cases, repo)
    if reasons:
        raise ValueError(f"{head_dir} is out of date: {'; '.join(reasons)}. {HOW_TO_RECORD}")

    rows, summary = rescore(head, cases)
    if rows != list(head.rows.values()) or summary.model_dump(
        mode="json"
    ) != head.summary.model_dump(mode="json"):
        raise ValueError(
            f"The scores in {head_dir} do not match what the scoring code computes from its "
            f"recorded answers. {HOW_TO_RECORD}"
        )

    lines = [
        f"# Baseline check: `{head_dir}`",
        "",
        f"Recorded run: `{head.meta.run_id}` on `{head.meta.env.machine}`.",
        "",
        "- **Fresh.** The recording matches this code, config, prompt, corpus, and cases.",
        f"- **Scores.** Re-scoring the {len(rows)} recorded answers gives the committed scores.",
    ]

    def report(base_line: str, comparison: str = "") -> str:
        text = "\n".join([*lines, f"- **Base branch.** {base_line}", ""])
        return text + ("\n" + comparison if comparison else "")

    if base_dir is None or not (base_dir / "meta.json").is_file():
        return report("It has no recorded run to compare with."), False
    base = load_run(base_dir)
    if base.meta.run_id == head.meta.run_id:
        return report(
            "This is the same recorded run as the base branch. Nothing to compare."
        ), False

    data_changed = (
        base.meta.dataset.sha256 != head.meta.dataset.sha256
        or (base.meta.corpus.sha256 if base.meta.corpus else None) != head.meta.corpus.sha256
    )
    machine_changed = base.meta.env.machine != head.meta.env.machine
    system_changed = base.meta.config_hash != head.meta.config_hash or recorded_code_sha256(
        base_dir
    ) != recorded_code_sha256(head_dir)
    changed = [
        name
        for name, flag in (
            ("the system (code, config, prompt)", system_changed),
            ("the data (cases, corpus)", data_changed),
            ("the recording machine", machine_changed),
        )
        if flag
    ]
    if data_changed or machine_changed:
        if len(changed) > 1:
            raise ValueError(
                f"This change alters more than one of: {'; '.join(changed)}. The gate can only "
                "judge one at a time, so split it into separate pull requests."
            )
        if data_changed:
            why = "The cases or corpus changed, so the base branch's run is not comparable."
        else:
            why = (
                f"This run was recorded on `{head.meta.env.machine}` and the base branch's on "
                f"`{base.meta.env.machine}`, so they are not comparable."
            )
        return report(f"{why} Accepted without a comparison: review the new numbers."), False

    with tempfile.TemporaryDirectory() as tmp:
        # Both runs are scored by the current code, so a scoring change cannot look like a
        # regression. Comparing copies also keeps compare.md out of baselines/.
        base_copy, head_copy = Path(tmp) / "base", Path(tmp) / "head"
        _write_rescored(base, cases, base_copy)
        _write_rescored(head, cases, head_copy)
        comparison, blocked = compare_runs(base_copy, head_copy, gates_path)
    return report(f"Compared with `{base.meta.run_id}`.", comparison), blocked


def record_baselines(root: Path = Path("baselines"), repo: Path = Path(".")) -> list[Path]:
    """Run the dev split on this machine and replace the committed baselines.

    Both evaluations finish before anything is replaced, so a failed run leaves baselines/ as
    it was. The tree must be clean, so each recording matches a commit.
    """
    sha, dirty = git_info(repo)
    if sha is None:
        raise ValueError("Not a git checkout: a recording has to match a commit")
    if dirty:
        raise ValueError(
            "Commit or stash your changes first, so the recording matches a commit "
            "(`git status` shows what is uncommitted)"
        )
    runs = []
    for name, config, retrieval_only in RECORDINGS:
        run_dir = evaluate_candidate(config, retrieval_only)
        require_complete(load_run(run_dir))
        runs.append((name, run_dir))
    targets = []
    for name, run_dir in runs:
        target = root / name
        if target.exists():
            shutil.rmtree(target)
        promote_baseline(run_dir, name, root)
        write_source(target, repo)
        targets.append(target)
    return targets

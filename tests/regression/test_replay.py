"""The replay gate: CI checks a run recorded on the reference machine instead of calling a model."""

import itertools
import json
import shutil
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from deskrag.cli import app
from deskrag.core.config import config_hash, load_config
from deskrag.core.dataset import load_cases
from deskrag.core.fakes import FakeRAGSystem
from deskrag.evaluation import replay
from deskrag.evaluation.baseline import promote_baseline
from deskrag.evaluation.replay import check_baseline, code_sha256, record_baselines, write_source
from deskrag.evaluation.retrieval_only import RetrievalOnlySystem
from deskrag.evaluation.runner import run_cases
from deskrag.rag.retrieval import build_retriever

REPO = Path(__file__).resolve().parents[2]
SAMPLES = REPO / "data" / "samples"
CI = REPO / ".github" / "workflows" / "ci.yml"
RUN_NUMBER = itertools.count(1)

CONFIG = f"""\
name: fake
system: fake
corpus_dir: {SAMPLES / "corpus"}
retrieval:
  method: fake
  k: 3
"""
# The 7 dev sample cases have 4 answerable ones, so 4 one-way flips is the most a test can show.
# Exact McNemar gives p = 0.125 for that, hence alpha 0.2 here. The real gates use 0.05.
GATES = """\
alpha: 0.2
metrics:
  hit@5: {tolerance: 0.05, gate: true}
  e2e_pass: {tolerance: 0.05, gate: false}
"""
# baselines/retrieval-gates.yaml, with alpha 0.2 for the same reason.
RETRIEVAL_GATES = """\
alpha: 0.2
metrics:
  hit@5: {tolerance: 0.05, gate: true}
  hit@1: {tolerance: 0.05, gate: true}
  mrr: {tolerance: 0.05, gate: false}
"""


class NoRetrieval:
    """A system with retrieval broken: every answerable case loses its gold document."""

    def __init__(self, inner):
        self.inner = inner

    def answer(self, question):
        return self.inner.answer(question).model_copy(update={"retrieved": []})


class CutOffAnswers:
    """The fake system with a token limit too low for an answer but not for an abstain reply."""

    def __init__(self, inner):
        self.inner = inner

    def answer(self, question):
        reply = self.inner.answer(question)
        if reply.abstained:
            return reply
        return reply.model_copy(update={"status": "truncated", "answer": None, "cited_doc_ids": []})


class World:
    """A small stand-in for the repo: pipeline code, a config, cases, gates, and baselines/."""

    def __init__(self, root: Path):
        self.repo = root / "repo"
        for name, text in {
            "src/deskrag/core/schemas.py": "A = 1\n",
            "src/deskrag/rag/pipeline.py": "B = 2\n",
            "src/deskrag/systems.py": "C = 3\n",
            "uv.lock": "version = 1\n",
        }.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.config = root / "config.yaml"
        self.config.write_text(CONFIG, encoding="utf-8")
        self.gates = root / "gates.yaml"
        self.gates.write_text(GATES, encoding="utf-8")
        self.retrieval_gates = root / "retrieval-gates.yaml"
        self.retrieval_gates.write_text(RETRIEVAL_GATES, encoding="utf-8")
        self.cases = SAMPLES / "cases.jsonl"
        self.baselines = root / "baselines"
        self.runs = root / "runs"

    def record(
        self,
        name: str = "dev",
        *,
        system=None,
        root: Path | None = None,
        retrieval_only: bool = False,
    ) -> Path:
        """Run the cases through `system` and store it as a baseline. The default system is the
        fake one, or the retriever alone for a retrieval-only run."""
        cfg = load_config(self.config)
        cases = load_cases(self.cases, split="dev")
        run_id = f"run-{next(RUN_NUMBER)}"
        run_dir = self.runs / run_id
        if system is None:
            system = (
                self.retriever()
                if retrieval_only
                else FakeRAGSystem.from_corpus_dir(cfg.corpus_dir)
            )
        run_cases(
            run_id,
            cases,
            system,
            run_dir,
            config=cfg,
            dataset_path=str(self.cases),
            retrieval_only=retrieval_only,
        )
        root = root or self.baselines
        if (root / name).exists():
            shutil.rmtree(root / name)
        target = promote_baseline(run_dir, name, root)
        write_source(target, self.repo)
        return target

    def retriever(self) -> RetrievalOnlySystem:
        """The config's retriever with no LLM, as `eval run --retrieval-only` builds it."""
        cfg = load_config(self.config)
        return RetrievalOnlySystem(build_retriever(cfg), cfg.retrieval.k)

    def record_base(self, name: str = "dev", **kwargs) -> Path:
        return self.record(name, root=self.baselines.parent / "base", **kwargs)

    def check(self, head: Path, base: Path | None, gates: Path | None = None):
        return check_baseline(
            head, self.config, self.cases, base, gates or self.gates, repo=self.repo
        )

    def fewer_cases(self) -> None:
        """Switch to a test set without the last dev case."""
        lines = self.cases.read_text(encoding="utf-8").splitlines()
        dev = [line for line in lines if json.loads(line)["split"] == "dev"]
        self.cases = self.baselines.parent / "fewer-cases.jsonl"
        self.cases.write_text("\n".join(dev[:-1]) + "\n", encoding="utf-8")

    def retrieve_fewer(self) -> None:
        """Change the system's config."""
        self.config.write_text(CONFIG.replace("k: 3", "k: 2"), encoding="utf-8")


@pytest.fixture
def world(tmp_path, monkeypatch):
    monkeypatch.setenv("DESKRAG_MACHINE", "reference")
    return World(tmp_path)


def test_code_fingerprint_covers_python_files_and_the_lock_file(world):
    before = code_sha256(world.repo)
    (world.repo / "src/deskrag/rag/prompts").mkdir()
    (world.repo / "src/deskrag/rag/prompts/v9.md").write_text("unused prompt", encoding="utf-8")
    (world.repo / "src/deskrag/commands").mkdir()
    (world.repo / "src/deskrag/commands/cli.py").write_text("D = 4\n", encoding="utf-8")
    assert (
        code_sha256(world.repo) == before
    )  # prompts are in the config hash; commands answer nothing

    (world.repo / "src/deskrag/rag/pipeline.py").write_text("B = 3\n", encoding="utf-8")
    changed = code_sha256(world.repo)
    assert changed != before
    (world.repo / "uv.lock").write_text("version = 2\n", encoding="utf-8")
    assert code_sha256(world.repo) != changed


def test_an_untouched_baseline_passes(world):
    head = world.record()
    base = world.baselines.parent / "base" / "dev"
    shutil.copytree(head, base)

    text, blocked = world.check(head, base)

    assert not blocked
    assert "same recorded run as the base branch" in text


def test_a_missing_base_baseline_is_not_an_error(world):
    text, blocked = world.check(world.record(), world.baselines.parent / "nowhere")
    assert not blocked
    assert "no recorded run to compare with" in text


def test_recording_the_unchanged_system_again_is_compared_and_passes(world):
    base = world.record_base()
    text, blocked = world.check(world.record(), base)
    assert not blocked
    assert "no flips" in text


def test_a_regression_is_blocked(world):
    base = world.record_base()
    fake = FakeRAGSystem.from_corpus_dir(SAMPLES / "corpus")
    head = world.record(system=NoRetrieval(fake))

    text, blocked = world.check(head, base)

    assert blocked
    assert "| hit@5 | 1 | 0 | -1 | 0.05 | 4 | 0 | 0.125 | REGRESSION | yes |" in text
    assert not (head / "compare.md").exists()  # checking never writes into baselines/


def test_truncated_replies_are_judged_as_wrong_decisions(world):
    world.gates.write_text(
        GATES + "  abstain_correct: {tolerance: 0.05, gate: true}\n", encoding="utf-8"
    )
    base = world.record_base()
    fake = FakeRAGSystem.from_corpus_dir(SAMPLES / "corpus")
    head = world.record(system=CutOffAnswers(fake))

    text, blocked = world.check(head, base)

    # The three cut-off answers count as wrong decisions instead of stopping the comparison.
    assert not blocked
    row = "| abstain_correct | 0.714286 | 0.285714 | -0.428571 | 0.05 | 3 | 0 | 0.25 | POSSIBLE | yes |"
    assert row in text


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ("code", "the pipeline code changed"),
        ("config", "the config or its prompt changed"),
        ("cases", "the dev cases changed"),
    ],
)
def test_a_stale_recording_is_rejected(world, change, reason):
    head = world.record()
    if change == "code":
        (world.repo / "src/deskrag/rag/pipeline.py").write_text("B = 3\n", encoding="utf-8")
    elif change == "config":
        world.retrieve_fewer()
    else:
        world.fewer_cases()

    with pytest.raises(ValueError, match=reason) as error:
        world.check(head, None)
    assert "make record" in str(error.value)


def test_a_recording_without_a_code_fingerprint_is_stale(world):
    head = world.record()
    (head / "source.json").unlink()
    with pytest.raises(ValueError, match="no code fingerprint"):
        world.check(head, None)


def test_edited_scores_are_rejected(world):
    head = world.record()
    results = head / "results.jsonl"
    rows = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    failed = next(row for row in rows if not row["passed"])
    failed["passed"] = True
    failed["scores"]["e2e_pass"] = 1.0
    results.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    with pytest.raises(ValueError, match="do not match what the scoring code computes"):
        world.check(head, None)


def test_an_edited_summary_is_rejected(world):
    head = world.record()
    summary = json.loads((head / "summary.json").read_text(encoding="utf-8"))
    summary["metrics"]["fact_recall"] = 1.0
    (head / "summary.json").write_text(json.dumps(summary), encoding="utf-8")

    with pytest.raises(ValueError, match="do not match what the scoring code computes"):
        world.check(head, None)


def test_the_base_run_is_rescored_before_it_is_compared(world):
    base = world.record_base()
    # Scores written by an older scorer: the base run claims every case passed.
    results = base / "results.jsonl"
    rows = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    for row in rows:
        row["passed"] = True
        row["scores"]["e2e_pass"] = 1.0
    results.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    text, blocked = world.check(world.record(), base)

    assert not blocked
    assert "no flips" in text


def test_new_cases_are_accepted_without_a_comparison(world):
    base = world.record_base()
    world.fewer_cases()
    text, blocked = world.check(world.record(), base)
    assert not blocked
    assert "cases or corpus changed" in text
    assert "REGRESSION" not in text


def test_a_new_machine_is_accepted_without_a_comparison(world, monkeypatch):
    base = world.record_base()
    monkeypatch.setenv("DESKRAG_MACHINE", "cluster")
    text, blocked = world.check(world.record(), base)
    assert not blocked
    assert "`cluster`" in text and "`reference`" in text


def test_changing_the_system_and_the_cases_together_is_rejected(world):
    base = world.record_base()
    world.fewer_cases()
    world.retrieve_fewer()
    with pytest.raises(ValueError, match="more than one of") as error:
        world.check(world.record(), base)
    assert "the system" in str(error.value) and "the data" in str(error.value)


def test_record_replaces_both_baselines_from_a_clean_tree(world, monkeypatch):
    old = world.record()
    old_run = json.loads((old / "meta.json").read_text(encoding="utf-8"))["run_id"]
    staged = world.baselines.parent / "staged"
    made = {
        False: world.record(root=staged),
        True: world.record("dev-retrieval", root=staged),
    }
    calls = []

    def fake_eval(config, retrieval_only=False):
        calls.append((str(config), retrieval_only))
        return made[retrieval_only]

    monkeypatch.setattr(replay, "evaluate_candidate", fake_eval)
    monkeypatch.setattr(replay, "git_info", lambda repo=".": ("abc123", False))

    targets = record_baselines(world.baselines, world.repo)

    assert targets == [world.baselines / "dev", world.baselines / "dev-retrieval"]
    assert calls == [("configs/baseline.yaml", False), ("configs/ci-retrieval.yaml", True)]
    for target in targets:
        source = json.loads((target / "source.json").read_text(encoding="utf-8"))
        assert source["code_sha256"] == code_sha256(world.repo)
    new_run = json.loads((targets[0] / "meta.json").read_text(encoding="utf-8"))["run_id"]
    assert new_run != old_run


def test_record_refuses_uncommitted_changes(world, monkeypatch):
    old = world.record()
    before = (old / "meta.json").read_bytes()

    def must_not_run(config, retrieval_only=False):
        raise AssertionError("no evaluation should start from a dirty tree")

    monkeypatch.setattr(replay, "evaluate_candidate", must_not_run)
    monkeypatch.setattr(replay, "git_info", lambda repo=".": ("abc123", True))

    with pytest.raises(ValueError, match="Commit or stash"):
        record_baselines(world.baselines, world.repo)
    assert (old / "meta.json").read_bytes() == before


def test_a_failed_evaluation_leaves_the_old_baselines_alone(world, monkeypatch):
    old = world.record()
    before = (old / "meta.json").read_bytes()

    def fails(config, retrieval_only=False):
        raise ValueError("Evaluation failed (exit 1); no baseline comparison performed")

    monkeypatch.setattr(replay, "evaluate_candidate", fails)
    monkeypatch.setattr(replay, "git_info", lambda repo=".": ("abc123", False))

    with pytest.raises(ValueError, match="Evaluation failed"):
        record_baselines(world.baselines, world.repo)
    assert (old / "meta.json").read_bytes() == before


def test_cli_check_exits_1_on_a_regression_and_2_on_a_stale_recording(world, monkeypatch):
    base = world.record_base()
    fake = FakeRAGSystem.from_corpus_dir(SAMPLES / "corpus")
    head = world.record(system=NoRetrieval(fake))
    monkeypatch.chdir(world.repo)
    args = [
        "baseline",
        "check",
        "--baseline-dir",
        str(head),
        "--base-dir",
        str(base),
        "--config",
        str(world.config),
        "--cases",
        str(world.cases),
        "--gates",
        str(world.gates),
    ]

    blocked = CliRunner().invoke(app, args)
    assert blocked.exit_code == 1, blocked.output
    assert "BLOCKED" in blocked.output

    (world.repo / "uv.lock").write_text("version = 2\n", encoding="utf-8")
    stale = CliRunner().invoke(app, args)
    assert stale.exit_code == 2
    assert "make record" in stale.output


def test_a_recorded_retrieval_regression_is_blocked(world):
    base = world.record_base("dev-retrieval", retrieval_only=True)
    broken = NoRetrieval(world.retriever())
    head = world.record("dev-retrieval", system=broken, retrieval_only=True)

    text, blocked = world.check(head, base, world.retrieval_gates)

    assert blocked
    assert "| hit@5 | 1 | 0 | -1 | 0.05 | 4 | 0 | 0.125 | REGRESSION | yes |" in text
    assert "| hit@1 | 1 | 0 | -1 | 0.05 | 4 | 0 | 0.125 | REGRESSION | yes |" in text


@pytest.mark.parametrize("again", [False, True], ids=["same run", "recorded again"])
def test_an_unchanged_retrieval_recording_passes(world, again):
    base = world.record_base("dev-retrieval", retrieval_only=True)
    if again:
        head = world.record("dev-retrieval", retrieval_only=True)
    else:
        head = world.baselines / "dev-retrieval"
        shutil.copytree(base, head)

    text, blocked = world.check(head, base, world.retrieval_gates)

    assert not blocked
    expected = "no flips" if again else "same recorded run as the base branch"
    assert expected in text


def test_new_cases_pass_the_retrieval_gate_without_a_comparison(world):
    base = world.record_base("dev-retrieval", retrieval_only=True)
    world.fewer_cases()
    head = world.record("dev-retrieval", retrieval_only=True)

    text, blocked = world.check(head, base, world.retrieval_gates)

    assert not blocked
    assert "cases or corpus changed" in text
    assert "REGRESSION" not in text


@pytest.mark.parametrize(
    "change",
    [{}, {"retrieval": {"k": 1}}, {"chunking": {"size_words": 50}}],
    ids=["as committed", "k1", "chunk50"],
)
def test_the_retrieval_gate_runs_the_baseline_config(tmp_path, change):
    """A retrieval change to configs/baseline.yaml has to reach configs/ci-retrieval.yaml.
    Otherwise `make record` records the old retrieval again and the retrieval gate never sees it."""
    bot = yaml.safe_load((REPO / "configs/baseline.yaml").read_text(encoding="utf-8"))
    for section, values in change.items():
        bot[section] |= values
    (tmp_path / "baseline.yaml").write_text(yaml.safe_dump(bot), encoding="utf-8")
    shutil.copy(REPO / "configs/ci-retrieval.yaml", tmp_path)

    gate = load_config(tmp_path / "ci-retrieval.yaml")

    assert config_hash(gate) == config_hash(load_config(tmp_path / "baseline.yaml"))


def test_the_retrieval_gate_job_checks_the_recording_two_ways():
    job = yaml.safe_load(CI.read_text(encoding="utf-8"))["jobs"]["retrieval-gate"]
    script = "\n".join(step.get("run", "") for step in job["steps"])

    # BM25 runs again on the runner and must not be worse than the committed recording.
    assert (
        "deskrag regress --config configs/ci-retrieval.yaml --baseline baselines/dev-retrieval"
        " --gates baselines/retrieval-gates.yaml --retrieval-only"
    ) in script
    # `make record` replaces that recording in the same pull request, so it is also compared
    # with the base branch's copy, as llm-gate does for baselines/dev.
    assert job["steps"][0].get("with", {}).get("fetch-depth") == 2  # HEAD^1 is the base branch
    assert "git archive HEAD^1 baselines/dev-retrieval " in script
    assert (
        "deskrag baseline check --baseline-dir baselines/dev-retrieval"
        ' --base-dir "$RUNNER_TEMP/base/baselines/dev-retrieval"'
        " --config configs/ci-retrieval.yaml --gates baselines/retrieval-gates.yaml"
    ) in script

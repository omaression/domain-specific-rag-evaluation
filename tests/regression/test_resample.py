import json
import math
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from deskrag.cli import app
from deskrag.evaluation.compare import compare_runs
from deskrag.evaluation.resample import draw_subsets, render, resample_runs, share

ROOT = Path(__file__).parent / "fixtures"
REPO = Path(__file__).resolve().parents[2]
GATES = REPO / "configs/regression.yaml"
IDS = [f"case-{i:02}" for i in range(30)]
runner = CliRunner()


def scores(passed: bool, hit: float | None = 1.0) -> dict:
    return {"e2e_pass": float(passed), "hit@5": hit, "abstain_correct": float(passed)}


def make_run(path: Path, run_id: str, rows: list[dict]) -> Path:
    """A recorded run of synthetic cases demo-00, demo-01, ... with these scores, built from
    the gate-baseline fixture."""
    shutil.copytree(ROOT / "gate-baseline", path)
    template = json.loads((path / "results.jsonl").read_text().splitlines()[0])
    results = [
        {**template, "run_id": run_id, "case_id": f"demo-{i:02}", "scores": s}
        for i, s in enumerate(rows)
    ]
    (path / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results))
    meta = json.loads((path / "meta.json").read_text())
    meta["run_id"] = run_id
    meta["dataset"]["n_cases"] = len(rows)
    (path / "meta.json").write_text(json.dumps(meta))
    summary = json.loads((path / "summary.json").read_text())
    summary["run_id"] = run_id
    summary["counts"].update(cases=len(rows), ok=len(rows))
    summary["metrics"] = {}
    for metric in ("e2e_pass", "hit@5", "abstain_correct"):
        values = [s[metric] for s in rows if s[metric] is not None]
        summary["metrics"][metric] = sum(values) / len(values)
    (path / "summary.json").write_text(json.dumps(summary))
    return path


def test_subsets_hold_distinct_cases_from_the_set():
    drawn = draw_subsets(IDS, 10, 50, seed=7)
    assert len(drawn) == 50
    for subset in drawn:
        assert len(subset) == len(set(subset)) == 10
        assert set(subset) <= set(IDS)


def test_the_seed_fixes_the_subsets():
    drawn = draw_subsets(IDS, 10, 50, seed=7)
    assert draw_subsets(IDS, 10, 50, seed=7) == drawn
    assert draw_subsets(list(reversed(IDS)), 10, 50, seed=7) == drawn
    assert draw_subsets(IDS, 10, 50, seed=8) != drawn


def test_the_full_set_is_drawn_once():
    assert draw_subsets(["b", "a"], 2, 100, seed=1) == [("a", "b")]


@pytest.mark.parametrize(("size", "draws"), [(0, 10), (31, 10), (5, 0)])
def test_bad_size_or_draw_count(size, draws):
    with pytest.raises(ValueError):
        draw_subsets(IDS, size, draws, seed=1)


def test_block_rate_matches_the_exact_odds():
    # gate-candidate fails 8 of the 12 cases gate-baseline passes and passes none it failed.
    # A subset of 10 of the 20 cases is blocked when it holds at least 6 of those 8: b >= 6
    # with c = 0 gives p <= 0.03125. Fewer than 6 gives p >= 0.0625.
    exact = sum(math.comb(8, k) * math.comb(12, 10 - k) for k in range(6, 9)) / math.comb(20, 10)
    result = resample_runs(
        ROOT / "gate-baseline",
        [("planted", ROOT / "gate-candidate")],
        GATES,
        sizes=[10],
        draws=20_000,
        seed=1,
    )
    tally = result.runs[0].by_size[10]
    assert tally.draws == 20_000
    assert abs(tally.blocked / tally.draws - exact) < 0.01
    assert tally.regressions["e2e_pass"] == tally.regressions["abstain_correct"] == tally.blocked
    assert tally.regressions["hit@5"] == 0


@pytest.mark.parametrize(
    ("baseline", "candidate"),
    [("gate-baseline", "gate-candidate"), ("fake-baseline", "fake-candidate")],
)
def test_the_full_set_gets_the_compare_verdict(tmp_path, baseline, candidate):
    shutil.copytree(ROOT / candidate, tmp_path / candidate)
    _, blocked = compare_runs(ROOT / baseline, tmp_path / candidate, GATES)
    result = resample_runs(
        ROOT / baseline, [("cand", ROOT / candidate)], GATES, sizes=[3], draws=10, seed=1
    )
    full = result.runs[0].by_size[result.n_cases]
    assert result.sizes == [3, result.n_cases]
    assert (full.draws, full.blocked) == (1, int(blocked))


def test_an_unchanged_run_is_never_blocked():
    result = resample_runs(
        ROOT / "gate-baseline",
        [("same", ROOT / "gate-baseline")],
        GATES,
        sizes=[5, 10, 15],
        draws=500,
        seed=1,
    )
    assert [result.runs[0].by_size[size].blocked for size in result.sizes] == [0, 0, 0, 0]


def test_adding_a_size_leaves_the_others_alone():
    def tally(sizes):
        result = resample_runs(
            ROOT / "gate-baseline",
            [("planted", ROOT / "gate-candidate")],
            GATES,
            sizes=sizes,
            draws=300,
            seed=3,
        )
        return result.runs[0].by_size[10]

    assert tally([10]) == tally([5, 10, 15])


def test_a_metric_with_no_case_in_the_subset_is_left_out(tmp_path):
    # hit@5 applies only to demo-00, so a subset of 5 of the 20 cases misses it 15 times in 20.
    base = make_run(tmp_path / "base", "base", [scores(True)] + [scores(True, None)] * 19)
    cand = make_run(tmp_path / "cand", "cand", [scores(True, 0.0)] + [scores(True, None)] * 19)
    result = resample_runs(base, [("cand", cand)], GATES, sizes=[5], draws=2_000, seed=1)
    tally = result.runs[0].by_size[5]
    assert abs(tally.not_applicable["hit@5"] / tally.draws - 0.75) < 0.05
    assert tally.not_applicable["e2e_pass"] == 0
    assert tally.blocked == 0
    note = (
        f"- hit@5 applies to no case in {tally.not_applicable['hit@5']:,} of the 2,000 subsets "
        "of 5, so it cannot block those subsets."
    )
    assert note in render(result).splitlines()


def test_runs_that_do_not_pair_are_rejected(tmp_path):
    short = make_run(tmp_path / "short", "short", [scores(True)] * 19)
    with pytest.raises(ValueError, match="Case identities differ"):
        resample_runs(
            ROOT / "gate-baseline", [("short", short)], GATES, sizes=[5], draws=10, seed=1
        )


def test_the_size_must_be_below_the_number_of_cases():
    with pytest.raises(ValueError, match="smaller than"):
        resample_runs(
            ROOT / "gate-baseline",
            [("planted", ROOT / "gate-candidate")],
            GATES,
            sizes=[20],
            draws=10,
            seed=1,
        )


def test_reading_the_runs_writes_nothing(tmp_path):
    for name in ("gate-baseline", "gate-candidate"):
        shutil.copytree(ROOT / name, tmp_path / name)
    (tmp_path / "gate-candidate" / "compare.md").unlink()
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    resample_runs(
        tmp_path / "gate-baseline",
        [("planted", tmp_path / "gate-candidate")],
        GATES,
        sizes=[10],
        draws=100,
        seed=1,
    )
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize(
    ("count", "draws", "text"),
    [
        (0, 10_000, "0%"),
        (1, 10_000, "<1%"),
        (3_750, 10_000, "38%"),
        (9_999, 10_000, ">99%"),
        (10_000, 10_000, "100%"),
        (1, 1, "100%"),
    ],
)
def test_share(count, draws, text):
    assert share(count, draws) == text


def resample_cli(*args):
    return runner.invoke(
        app,
        [
            "runs",
            "resample",
            str(ROOT / "gate-baseline"),
            f"planted={ROOT / 'gate-candidate'}",
            str(ROOT / "gate-baseline"),
            "--gates",
            str(GATES),
            *args,
        ],
    )


def test_cli_prints_the_table():
    result = resample_cli("--size", "10", "--size", "5", "--draws", "200")
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert "| Run | Lowest p on all 20 | 5 cases | 10 cases | All 20 |" in lines
    # The first table is the share blocked; the by-metric table repeats each label later.
    planted = next(line for line in lines if line.startswith("| `planted` |"))
    assert planted.startswith("| `planted` | e2e_pass 8 / 0 / 0.00781 |")
    assert planted.endswith("| 100% |")
    # A run without a label goes by its run ID. An unchanged run is never blocked.
    assert "| `gate-baseline` | none | 0% | 0% | 0% |" in lines
    assert "200 random subsets" in result.output and "seed 20261112" in result.output


@pytest.mark.parametrize(
    "args", [["--size", "0"], ["--size", "20"], ["--draws", "0"], ["missing-run"], ["=nolabel"]]
)
def test_cli_rejects_bad_input(args):
    assert resample_cli(*args).exit_code == 2

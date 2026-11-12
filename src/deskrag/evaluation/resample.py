"""Question 3 in docs/harness-pivot.md, sensitivity: how often does the gate block a change when
the dev set has fewer cases?

It reads recorded runs and calls no model. For each subset size it draws random subsets of the
baseline's case IDs, keeps only those cases in the baseline and in each candidate run, and
applies `compare`'s rule to what is left: per gated metric, the tolerance and the exact McNemar
test at the gate file's alpha. A subset is blocked when a gated metric gets a REGRESSION
verdict. Every candidate is judged on the same subsets, and the full set is always judged too,
which must give the same verdict as `deskrag compare`.
"""

import random
from collections import Counter
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from deskrag.evaluation.compare import (
    cell,
    compare_loaded,
    flip_counts,
    load_gates,
    load_run,
    metric_verdict,
    paired_scores,
    require_complete,
    require_paired,
)
from deskrag.evaluation.stats import mcnemar_exact

SIZES = (10, 20, 40)
DRAWS = 100_000
SEED = 20261112


def parse_candidate(text: str) -> tuple[str | None, Path]:
    """`LABEL=PATH`, or just `PATH` to go by the run ID."""
    label, sep, path = text.partition("=")
    if not sep:
        return None, Path(text)
    if not label or not path:
        raise ValueError(f"Expected PATH or LABEL=PATH, not {text!r}")
    return label, Path(path)


def draw_subsets(case_ids: list[str], size: int, draws: int, seed: int) -> list[tuple[str, ...]]:
    """`draws` random subsets of `size` distinct case IDs, each sorted. A subset as large as the
    set is the set itself, drawn once.

    Each size gets its own generator, seeded with the seed and the size, so adding a size leaves
    the other sizes' subsets as they were."""
    ordered = sorted(case_ids)
    if not 1 <= size <= len(ordered):
        raise ValueError(f"A subset size must be between 1 and {len(ordered)}, not {size}")
    if draws < 1:
        raise ValueError(f"The number of draws must be at least 1, not {draws}")
    if size == len(ordered):
        return [tuple(ordered)]
    rng = random.Random(f"{seed}:{size}")
    return [tuple(sorted(rng.sample(ordered, size))) for _ in range(draws)]


@dataclass
class Tally:
    """What the gate did on the subsets of one size."""

    draws: int
    blocked: int = 0
    regressions: Counter[str] = field(default_factory=Counter)  # metric -> REGRESSION verdicts
    not_applicable: Counter[str] = field(default_factory=Counter)  # metric -> subsets with no case


@dataclass
class Resampled:
    """One candidate run, judged on every subset."""

    label: str
    run_id: str
    flips: dict[str, tuple[int, int, float]]  # gated metric -> b, c, p on the full set
    by_size: dict[int, Tally]


@dataclass
class Sensitivity:
    """Every candidate run, judged on the same subsets."""

    baseline_id: str
    n_cases: int
    gates_path: Path
    alpha: float
    seed: int
    draws: int
    sizes: list[int]  # the subset sizes, then the full set
    runs: list[Resampled]


@cache
def _verdict(
    metric: str, tolerance: float, alpha: float, n: int, base: float, cand: float, b: int, c: int
) -> str:
    # The same counts come up in many subsets, so each verdict is worked out once.
    return metric_verdict(metric, base / n, cand / n, tolerance, mcnemar_exact(b, c), alpha)


@dataclass(frozen=True)
class _GatedMetric:
    metric: str
    tolerance: float
    alpha: float
    cases: dict[str, tuple[float, float, int, int]]  # case -> baseline, candidate, b, c

    def verdict(self, subset: tuple[str, ...]) -> str | None:
        """compare's verdict on the cases in `subset`, or None if the metric applies to none.
        The metric's value on a subset is its mean over the cases in it, as in a run of only
        those cases, and b and c add up case by case."""
        n = base = cand = b = c = 0
        for case_id in subset:
            scores = self.cases.get(case_id)
            if scores is None:
                continue
            n += 1
            base += scores[0]
            cand += scores[1]
            b += scores[2]
            c += scores[3]
        if not n:
            return None
        return _verdict(self.metric, self.tolerance, self.alpha, n, base, cand, b, c)


def resample_runs(
    baseline: Path,
    candidates: list[tuple[str | None, Path]],
    gates_path: Path,
    sizes: list[int],
    draws: int,
    seed: int,
) -> Sensitivity:
    """Judge each (label, run) in `candidates` against `baseline` on `draws` random subsets of
    each size in `sizes`, and once on the full set. A run without a label goes by its run ID."""
    base = load_run(baseline)
    require_complete(base)
    gates = load_gates(gates_path)
    alpha = gates.get("alpha", 0.05)
    case_ids = sorted({case_id for case_id, _ in base.rows})
    n_cases = len(case_ids)
    for size in sizes:
        if not 1 <= size < n_cases:
            raise ValueError(
                f"A subset size must be at least 1 and smaller than the {n_cases} cases, not "
                f"{size}. The full set is always judged."
            )
    all_sizes = [*sorted(set(sizes)), n_cases]
    subsets = {size: draw_subsets(case_ids, size, draws, seed) for size in all_sizes}

    runs = []
    for label, path in candidates:
        cand = load_run(path)
        require_paired(base, cand)
        _, blocked = compare_loaded(base, cand, gates)
        gated, flips = [], {}
        for metric, rule in gates["metrics"].items():
            if not rule.get("gate"):
                continue
            pairs = paired_scores(metric, base, cand)
            cases = {
                key[0]: (old, new, *flip_counts(metric, [(key, old, new)]))
                for key, old, new in pairs
            }
            gated.append(_GatedMetric(metric, rule.get("tolerance", 0), alpha, cases))
            b, c = flip_counts(metric, pairs)
            flips[metric] = (b, c, mcnemar_exact(b, c))

        by_size = {}
        for size, drawn in subsets.items():
            tally = Tally(draws=len(drawn))
            for subset in drawn:
                verdicts = [(g.metric, g.verdict(subset)) for g in gated]
                for metric, verdict in verdicts:
                    if verdict is None:
                        tally.not_applicable[metric] += 1
                    elif verdict == "REGRESSION":
                        tally.regressions[metric] += 1
                tally.blocked += any(verdict == "REGRESSION" for _, verdict in verdicts)
            by_size[size] = tally
        if by_size[n_cases].blocked != int(blocked):
            raise RuntimeError(f"{path}: on the full set the resampling disagrees with compare")
        runs.append(Resampled(label or cand.meta.run_id, cand.meta.run_id, flips, by_size))

    return Sensitivity(
        baseline_id=base.meta.run_id,
        n_cases=n_cases,
        gates_path=gates_path,
        alpha=alpha,
        seed=seed,
        draws=draws,
        sizes=all_sizes,
        runs=runs,
    )


def share(count: int, draws: int) -> str:
    """count / draws as a whole percent. A share that is not 0 or 1 never shows as 0% or 100%."""
    if count == 0:
        return "0%"
    if count == draws:
        return "100%"
    percent = int(100 * count / draws + 0.5)
    if percent == 0:
        return "<1%"
    if percent == 100:
        return ">99%"
    return f"{percent}%"


def _lowest_p(flips: dict[str, tuple[int, int, float]]) -> str:
    worse = [(p, metric, b, c) for metric, (b, c, p) in flips.items() if b > c]
    if not worse:
        return "none"
    p, metric, b, c = min(worse, key=lambda item: item[0])
    return f"{metric} {b} / {c} / {'< 0.001' if p < 0.001 else f'{p:.3g}'}"


def render(result: Sensitivity) -> str:
    """The result as Markdown: the share of subsets blocked, per run and size, then per metric."""
    n, draws = result.n_cases, result.draws
    subset_sizes = result.sizes[:-1]
    head = ["Run", f"Lowest p on all {n}", *(f"{size} cases" for size in subset_sizes), f"All {n}"]
    lines = [
        "# Sensitivity: how often the gate blocks on fewer cases",
        "",
        f"Baseline: `{cell(result.baseline_id)}`, {n} cases. "
        f"Gates: `{cell(result.gates_path)}`, alpha {result.alpha:g}.",
        f"Each subset size has {draws:,} random subsets of the case IDs, drawn without "
        f"replacement with seed {result.seed}. All {n} is the full set, judged once. "
        "Every run is judged on the same subsets.",
        "",
        "A cell is the share of subsets on which a gated metric gets a REGRESSION verdict, so the "
        "gate blocks the run. Lowest p is the gated metric with the smallest p on the full set "
        "among those that lost more cases than they gained, as b / c / p.",
        "",
        "| " + " | ".join(head) + " |",
        "|---|---|" + "---:|" * (len(head) - 2),
    ]
    for run in result.runs:
        blocked = [
            share(run.by_size[size].blocked, run.by_size[size].draws) for size in result.sizes
        ]
        lines.append(f"| `{cell(run.label)}` | {_lowest_p(run.flips)} | {' | '.join(blocked)} |")

    metrics = list(result.runs[0].flips) if result.runs else []
    lines += [
        "",
        "## REGRESSION verdicts by gated metric",
        "",
        "| Run | Cases | " + " | ".join(metrics) + " |",
        "|---|---:|" + "---:|" * len(metrics),
    ]
    for run in result.runs:
        for size in subset_sizes:
            tally = run.by_size[size]
            shares = [share(tally.regressions[metric], tally.draws) for metric in metrics]
            lines.append(f"| `{cell(run.label)}` | {size} | {' | '.join(shares)} |")

    notes = []
    for size in subset_sizes:
        for metric in metrics:
            missing = max(run.by_size[size].not_applicable[metric] for run in result.runs)
            if missing:
                notes.append(
                    f"- {metric} applies to no case in {missing:,} of the {draws:,} subsets of "
                    f"{size}, so it cannot block those subsets."
                )
    if notes:
        lines += ["", "## Notes", "", *notes]
    lines += ["", "## Runs", "", "| Run | Run ID |", "|---|---|"]
    lines += [f"| `{cell(run.label)}` | `{cell(run.run_id)}` |" for run in result.runs]
    return "\n".join(lines) + "\n"

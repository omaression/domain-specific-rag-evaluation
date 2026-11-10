"""Print the frozen CI subset: N dev case IDs, balanced by `pick_balanced`.

Usage: uv run python scripts/pick_ci_cases.py 20 > configs/ci-llm-cases.txt
"""

import sys
from pathlib import Path

from deskrag.core.dataset import load_cases
from deskrag.evaluation.subset import pick_balanced

n = int(sys.argv[1])
ids = pick_balanced(load_cases(Path("data/testset"), split="dev"), n)
if len(ids) < n:
    sys.exit(f"asked for {n} cases, but the dev split has only {len(ids)}")

print("# Frozen case subset for the CI LLM gate. Made by scripts/pick_ci_cases.py.")
print("# Changing this list changes the dataset fingerprint, so baselines/ci-llm")
print("# must be re-recorded in the same PR (see baselines/README.md).")
print("\n".join(ids))

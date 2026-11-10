# Harness pivot: design

Proposed by Omar on 2026-11-09. Not reviewed by the group yet.

## Why we are changing

Another group claimed the domain-specific RAG topic before us. Our choices were to evaluate differently from them, or to move to the topic "Evaluation harness for an LLM feature, with CI regression testing". The instructor confirmed that we can take the harness topic and keep the help-desk bot as the feature under test.

I think the harness topic is the right choice for three reasons:

- [design.md](design.md) already calls the chatbot the "system under test" and the harness the "main project". The midterm report says the same.
- The runner, the metrics, the failure tags, the McNemar comparison, and three CI jobs are already on main. Nothing is thrown away.
- "Evaluate differently" keeps us on the other group's topic. The obvious ways to differ (an LLM judge, reference-free scores) would replace the labeled test set and the WS4 metrics.

## What the project claims

**Claim:** the harness catches changes that make the help-desk bot worse before they merge, and it rarely blocks a harmless change.

Three questions replace the three in the midterm report:

1. **Detection.** Of the regressions we plant on purpose, how many does CI block, and which check catches each one?
2. **False alarms.** How often does CI block a change that should not matter?
3. **Sensitivity.** How many cases does the gate need before it can catch a regression of a given size?

Question 3 matters because the gate is weak on a small set. `compare` blocks only when a gated metric is worse than its tolerance and the exact two-sided McNemar test gives p < 0.05. That needs at least 6 pass-to-fail flips with none the other way (p = 0.03125). Five flips give p = 0.0625. About 20 of the 26 dev cases pass today, so a change has to break 6 of those 20 before the gate can block it.

## What happens to the existing work

| Piece | New role |
|---|---|
| Corpus, BM25, pipeline, runner, metrics, compare | Stay as they are |
| Bot quality numbers (e2e_pass, hit@5, abstention) | One table: the baseline the gate protects, not the headline |
| Closed-book vs RAG | A planted regression. In my October run on the 26 dev cases, e2e_pass fell from 0.77 to 0.31 (12 pass-to-fail flips, none back, p = 0.0005) and `compare` exited 1 |
| Dense and hybrid retrieval, score-gate tuning, model swap | Candidate changes that go through the gate. Built only if there is time |
| Test set growth | Still needed, because of question 3 |
| Held-out test split, LLM judge, dashboard | Dropped. The claim is about the gate, not the bot's final score |

## CI layers

| Check | When it runs | What it compares | State on main, 2026-11-09 |
|---|---|---|---|
| Lint, tests, fixture contract | Every PR | A planted fixture must fail | Passing |
| Retrieval gate | Every PR, no LLM | BM25 on all dev cases against `baselines/dev-retrieval` | Advisory, and failing: the baseline is missing |
| LLM gate (new) | PRs that touch `src/deskrag/rag/`, `configs/`, `baselines/`, or `data/testset/` | Ollama on the GitHub runner, a frozen subset of cases, against `baselines/ci-llm` | Not built |
| Full run | The reference Mac, `make regress` | All dev cases against `baselines/dev` | Works, but `baselines/dev` is missing |

### The LLM gate

The job does five things:

1. Checks out the code and installs dependencies.
2. Installs Ollama and pulls the model, using a cache so the download happens once.
3. Runs `deskrag eval run` with `configs/ci-llm.yaml` on the case IDs listed in `configs/ci-llm-cases.txt`.
4. Runs `deskrag regress --candidate <that run> --baseline baselines/ci-llm --gates configs/regression.yaml`. This already works: `regress` accepts a recorded run.
5. Writes `compare.md` to the job summary and uploads the run as an artifact.

Rules:

- **Same kind of machine.** A manually triggered workflow records `baselines/ci-llm` on a hosted runner, and the run is promoted and committed through a PR. It is only ever compared with other hosted-runner runs. This is the one baseline that does not come from the reference Mac.
- **Frozen subset.** `configs/ci-llm-cases.txt` lists at least 20 case IDs, balanced across the 7 case types. It does not change when new cases are added, so new cases do not invalidate the baseline.
- **Unchanged gate rules.** Tolerance 0.05 and alpha 0.05 on e2e_pass, hit@5, and abstain_correct, as committed in `configs/regression.yaml`.
- **Always starts.** The job starts on every PR and skips its slow steps when none of the listed paths changed. A required check that never starts would leave the PR stuck.

### What the trial run decides

GitHub runners have no GPU, so speed is unknown. The first task is a trial workflow that runs 10 cases with the pinned model `qwen3:4b-instruct-2507-q4_K_M` and reports seconds per case.

- If 20 cases fit in 10 minutes, setup included, the gate uses the pinned model and the largest balanced subset that fits.
- If not, the trial repeats with a smaller model, and `configs/ci-llm.yaml` names that model.
- If no model gets 20 cases into 10 minutes, the fallback is record and replay: the PR author runs the eval locally and commits the run, and CI re-scores and compares it without calling a model.

### Gaps in the current code

- `deskrag eval run --retrieval-only` is still a stub (`src/deskrag/commands/evaluate.py`, line 36, exit 3). The retrieval gate cannot run until this is finished, even with a baseline.
- `eval run` has `--limit N` but no way to run a named list of cases. The LLM gate needs one.
- `compare` refuses a changed dataset fingerprint. Every PR that adds cases must re-record `baselines/dev-retrieval`. That takes seconds and needs no LLM. A PR that edits a case in the frozen subset, such as a label fix, must re-record `baselines/ci-llm` as well.
- `main` is not protected, so a red check does not stop a merge today.

## The experiment

Gate settings are frozen at the committed values before any planted run, so the results are not tuned to the planted set.

### Planted regressions

Each one is a one-line config change or a prompt file.

| Name | Change | Metric that should move |
|---|---|---|
| `k1` (exists) | `retrieval.k` 5 to 1 | hit@5, e2e_pass |
| `k3` (exists) | `retrieval.k` 5 to 3 | hit@5, mildly |
| `closed-book` (exists) | No retrieval | hit@5, e2e_pass |
| `no-abstain` | Prompt v1 without the abstain rule | abstain_correct, missed_abstain_rate |
| `no-cite` | Prompt v1 without the citation rule | citation_valid, which is not gated |
| `chunk50` | `chunking.size_words` 300 to 50, overlap 10 | hit@5, fact_recall |
| `ctx1024` | `llm.num_ctx` 4096 to 1024, which cuts off the context | e2e_pass, fact_recall |
| `maxtok32` | `llm.max_tokens` 512 to 32, which cuts off the answer | format_error_rate, e2e_pass |
| `gate-high` | `abstention.min_score` set to the median top retrieval score of the answerable cases in the baseline run, so about half of them are refused | false_abstain_rate, e2e_pass |

### Controls

These must not be blocked.

| Name | Change |
|---|---|
| `rerun-1` to `rerun-5` | The baseline config, run again on five fresh runners |
| `reworded` | Prompt v1 reworded with the same meaning |
| `seed43` | `llm.seed` 42 to 43 |

### One real change

`model-alt` (exists): the model swap to `llama3.2:3b`. The direction is not known in advance.

### What is recorded

For every run: the verdict of each check, the metric that caught it, the flip counts b and c, p, the flipped cases, and minutes to verdict.

A manually triggered matrix workflow runs every config through the LLM gate steps, so the detection and false-alarm tables come from one workflow run. The same configs also run in full on the reference Mac. Two real PRs, one bad and one harmless, are the live demo.

### Question 3

No new LLM calls. A script takes the full Mac runs for the baseline and each planted config, draws random subsets of 10, 20, 40, and all cases, applies the same gate rule, and reports how often the verdict is REGRESSION at each size.

### Results tables

1. **Detection:** one row per planted regression, with the verdict from the retrieval gate, the LLM gate, and the full run.
2. **False alarms:** one row per control, with verdicts and flip counts.
3. **Sensitivity:** detection rate by subset size.

## Test set

- **Today:** 26 dev cases (14 answerable, 12 not) in two files, `faeghe.jsonl` (21) and `koshish.jsonl` (5). No test split.
- **Target:** 60 dev cases. I add 34 in `data/testset/omar.jsonl` and check each one against its source page.
- **Second label:** the midterm report promised a blind second label on about 20% of cases. That needs one teammate.

## Where the work happens

I do all of it in my own fork, and the group reviews one pull request from the fork into the team repo.

The fork is needed for two things I cannot do in the team repo:

- **Branch protection.** Only the repo owner can require checks. In the fork I can turn it on, so the demo PR is really blocked.
- **Manually triggered workflows.** They only run when the workflow file is on the default branch. The baseline recording and the experiment matrix both need this.

GitHub-hosted runners are free for public repositories, so the fork costs nothing.

Commits are grouped by workstream area so each owner can review their part:

| Area | Files | Reviewer |
|---|---|---|
| Runner | `src/deskrag/commands/evaluate.py`, `src/deskrag/evaluation/runner.py`, their tests | WS4 |
| CI and baselines | `.github/**`, `baselines/**`, `configs/ci-*`, `Makefile` | WS5 |
| Prompts and planted configs | `src/deskrag/rag/prompts/**`, `configs/experiments/**` | WS3 |
| Cases | `data/testset/omar.jsonl` | WS1 |
| Docs | `docs/**` | Everyone |

## Order of work

1. Trial run on the GitHub runner.
2. Finish `eval run --retrieval-only` and add the case-ID list option.
3. Record the three baselines, make the retrieval gate blocking, add the LLM gate job.
4. Write the 34 new cases.
5. Planted configs and prompts, the matrix workflow, the control runs.
6. Full runs on the Mac, and the resampling script.
7. Report, repo docs, deck.

| Week | Dates | Done when |
|---|---|---|
| 1 | Nov 9 to 15 | Steps 1 to 3 finished; the LLM gate passes on the fork's main; 19 of the new cases written, for 45 in total |
| 2 | Nov 16 to 22 | Steps 4 to 6 finished; the last 15 cases written and the set frozen at 60; the three results tables exist |
| 3 | Nov 23 to 29 | Step 7 finished; demo rehearsed |

The final is due two to four weeks after Nov 9. If it is two weeks, cut in this order:

1. The model swap, dense, and hybrid.
2. The matrix workflow. Run the planted configs on the Mac and keep the two demo PRs.
3. Cases stop at 45.
4. Resampling at one subset size instead of four.

## What still needs the group

- **Review.** The pull request edits WS4 and WS5 files, which [CONTRIBUTING.md](../CONTRIBUTING.md) reserves for their owners.
- **Branch protection on the team repo.** Only Faeghe can turn it on.
- **A second labeler** for about 12 of the 60 cases.
- **Contributions.** The final report has to say who did what.

## Report and docs

- **Report:** new title, abstract, and the three questions. Sections IV-A to IV-C shrink into "the feature under test". Section IV-D grows into the main method. A new results section holds the three tables. Related work moves toward regression testing and behavioral testing of language models. The WS3 name placeholder in Section IV-F gets fixed.
- **Repo docs:** the CI section of [design.md](design.md) and the owners and milestones in [workplan.md](workplan.md) are updated to match.
- **Deck:** same layout, with the story changed to plant, detect, false alarms.

Working title: "An Evaluation Harness with CI Regression Testing for a University Help-Desk LLM Feature".

## Risks

- **The runner is too slow.** Covered by the trial run and its two fallbacks.
- **Fresh runners disagree with each other.** Ollama output can differ across hardware even at temperature 0. The five control runs measure this, and the number goes in the report as the gate's false-alarm rate.
- **The gate is weak on small sets.** A 20-case subset only catches large breaks. Question 3 reports this plainly, and the full run on the Mac covers the rest.
- **Hosted runners are not the reference machine.** Results quoted for the bot come from full runs on the Mac. The hosted-runner baseline exists only for the gate.

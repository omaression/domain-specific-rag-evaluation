# Harness pivot: design

Proposed by Omar on 2026-11-09. Not reviewed by the group yet.

Updated on 2026-11-11 after week 1: CI no longer runs the model. The LLM gate checks a run recorded on the reference Mac ([why](#why-ci-does-not-run-the-model)). [Week 1 status](#week-1-status) has the first results. The [results tables](#results-tables) have the planted and control runs on the 60 cases.

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

Question 3 matters because the gate is weak on a small set. `compare` blocks only when a gated metric is worse than its tolerance and the exact two-sided McNemar test gives p < 0.05. That needs at least 6 pass-to-fail flips with none the other way (p = 0.03125). Five flips give p = 0.0625. About 20 of the 26 dev cases pass today, so a change has to break 6 of those 20 before the gate can block it. Week 1 hit this twice: two real regressions broke 3 and 4 cases, and both got through.

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

| Check | When it runs | What it compares | State on the fork's main, 2026-11-11 |
|---|---|---|---|
| Lint, tests, fixture contract | Every PR | A planted fixture must fail | Required, passing |
| Retrieval gate | Every PR, no LLM | BM25 on all dev cases against `baselines/dev-retrieval` | Required, passing |
| LLM gate | Every PR, no LLM, about 10 s | The committed `baselines/dev` against the base branch's copy | Required, passing |
| Recording | The reference Mac, `make record`, about 3 minutes | Runs all dev cases and replaces `baselines/dev` and `baselines/dev-retrieval` | Works |

Branch protection on the fork's main requires all four CI jobs (`test`, `regression-contract`, `retrieval-gate`, `llm-gate`), for admins too. `make regress` still runs the dev split and compares it with `baselines/dev` without changing anything, so an author can see the verdict before recording.

### The LLM gate

The PR author runs `make record` on the reference Mac and commits the new recording with the change. CI never calls a model. The `llm-gate` job takes the base branch's `baselines/dev` and runs `deskrag baseline check`, which answers three questions:

1. **Fresh?** The pipeline code, the config and its prompt, the corpus, and the dev cases must match the fingerprints stored with the recording. If any differ, the check fails and names which.
2. **Honest?** It scores the recorded answers again. The result must equal the committed scores.
3. **Worse?** It compares the recording with the base branch's copy, with the same McNemar rule and tolerances as `compare`. A gated regression fails the check.

Rules:

- **One kind of change per PR.** Two recordings are comparable only when they share the cases, the corpus, and the machine. A PR that changes the data or the recording machine passes without a comparison, and the reviewer reads the new numbers. A PR that changes more than one of system, data, and machine fails and has to be split. [baselines/README.md](../baselines/README.md) has the table.
- **Clean tree.** `make record` refuses to run with uncommitted changes, so each recording matches a commit.
- **Unchanged gate rules.** Tolerance 0.05 and alpha 0.05 on e2e_pass, hit@5, and abstain_correct, as committed in `configs/regression.yaml`.
- **Trusted recorder.** CI cannot prove that the recorded answers came from the model. Re-scoring catches edited scores, not edited answers.

### Why CI does not run the model

The first version of this design ran Ollama on GitHub's hosted runners (4 cores, 15 GB RAM, no GPU) on a frozen subset of cases. Record and replay was the fallback if no model could run 20 cases in 10 minutes. A trial picked `llama3.2:3b` on 23 cases. Measurements the next day showed that the trial could not be trusted, and on 2026-11-11 I switched to replay.

**Trial, 2026-11-10.** Each model ran the first 10 dev cases (`ff-001` to `ff-010`, all answerable) once, through `configs/baseline.yaml` with only the model changed, on Ollama 0.40.3. No run had an infra error or a timeout.

| Model | Passed (of 10) | Seconds per case | Setup overhead (s) | Cases that fit in 10 min |
|---|---:|---:|---:|---:|
| `qwen3:4b-instruct-2507-q4_K_M` (pinned) | 6 | 50.0 | 143 | 9 |
| `llama3.2:3b` | 10 | 20.5 | 113 | 23 |
| `llama3.2:1b` | 2 | 27.3 | 118 | 17 |
| `gemma3:1b` | 2 | 31.3 | 104 | 15 |

Seconds per case is the wall time of the whole eval step divided by 10, so it includes loading the model and building the index. Setup overhead is the rest of the job (checkout, dependencies, installing Ollama) plus a 60 s allowance for restoring the model from cache. For comparison, the pinned model takes 5.8 s per case on the reference Mac, where it also passes 6 of these 10 cases.

**What went wrong.** Each model ran once, each on a different runner. Recording the gate's baseline with `llama3.2:3b` on the 23 cases then took 22 min 47 s, not the 9 minutes the trial predicted. To find out why, I ran both candidate models on the same 23 cases twice each, in parallel, and logged each runner's CPU (Actions run 42937645956):

| Model | Runner CPU | Mean seconds per answer | Job time | Passed (of 23) |
|---|---|---:|---|---:|
| `llama3.2:3b` | AMD EPYC 9V45 | 19.4 | 8 min 48 s | 17 |
| `llama3.2:3b` | Intel Xeon Platinum 8370C | 41.4 | 17 min 39 s | 17 |
| `llama3.2:3b` | Not logged (the baseline recording) | 53.2 | 22 min 47 s | 16 |
| `qwen3:4b-instruct-2507-q4_K_M` | AMD EPYC 9V74 | 46.7 | 19 min 26 s | 18 |
| `qwen3:4b-instruct-2507-q4_K_M` | AMD EPYC 7763 | 74.9 | 29 min 46 s | 18 |

- **Speed.** The same model on the same cases took 2.7 times as long on the slowest runner as on the fastest. Only one of the five runs finished in 10 minutes. The runner a job lands on decides its time, so a trial with one job per model cannot rank models.
- **Answers.** Two fresh runners do not always give the same answer. The two parallel `llama3.2:3b` runs matched word for word, but the recording's text differed from them on 7 of 23 cases, and its verdict differed on one (`ff-009`). The two `qwen3:4b` runs gave the same verdict on all 23 cases and the same text on 21. Both also gave the same verdicts as the Mac on all 23.
- **Abstention.** `llama3.2:3b` refused only 5 of the 11 unanswerable questions in the subset. A change that stopped it from refusing could break at most those 5 cases, one short of the 6 the gate needs to block.

So a model check on hosted runners would cost 9 to 30 minutes per pull request, could run past a time limit on a slow runner, and would add verdict flips that have nothing to do with the change. Replay avoids all of this. The model runs only on the Mac, where three runs of unchanged code gave the same verdict on all 26 cases, and CI checks the recording in about 10 seconds.

### Gaps in the current code

Week 1 closed three of the four gaps listed here on 2026-11-09: `eval run --retrieval-only` works (fork PR #3), `eval run --case-ids` runs a named list of cases (fork PR #4), and the fork's main is protected.

The fourth was decided on 2026-11-11, before any planted run. `compare` used to stop with "Applicability changed" (exit 2) when a case had a score in one run and none in the other. A truncated or unparsable reply had no `abstain_correct`, so a change that caused format errors failed the gate as an invalid comparison instead of as a regression, and a single format error blocked a harmless change the same way. Now such a reply scores `abstain_correct` 0, as it already scored `e2e_pass` 0, and the usual McNemar rule judges it. `false_abstain_rate`, `missed_abstain_rate`, and abstain precision and recall still leave it out. The committed baselines have no format errors, so none of their scores changed.

Still open:

- **Data PRs are not compared.** Every PR that adds or edits cases has to run `make record`, and the gate accepts it without a comparison. The reviewer is the only check on a data PR.
- **The retrieval gate compares a PR with itself.** It runs BM25 again and compares the result with the PR's own `baselines/dev-retrieval`, which `make record` replaces in the same PR. Its config also pins k to 5. So it cannot block a retrieval change that was recorded, and on a real PR it would have passed both `k1` and `chunk50` ([detection](#1-detection)). The LLM gate's hit@5 covers retrieval for now: it blocked `k1` with b = 8, c = 0. Comparing with the base branch's copy, as the LLM gate does, would fix it.
- **Latency warns on noise.** Three runs of unchanged code on 26 cases gave `latency_p95_s` from 5.4 to 9.1 s. Five runs on the 60 cases gave 5.2 to 10.4 s against 7.8 s in the recording, and two of the five warned at its 2.0 s tolerance. It is warn-only, so it never blocks, but its warnings mean little at this size.

## The experiment

Gate settings are frozen at the committed values before any planted run, so the results are not tuned to the planted set. Two planted regressions already ran in week 1 with these settings.

### Planted regressions

Each one is a one-line config change or a prompt file.

| Name | Change | Metric that should move |
|---|---|---|
| `k1` (exists, ran in week 1) | `retrieval.k` 5 to 1 | hit@5, e2e_pass |
| `k3` (exists) | `retrieval.k` 5 to 3 | hit@5, mildly |
| `closed-book` (exists) | No retrieval | hit@5, e2e_pass |
| `no-abstain` (ran in week 1) | Prompt v1 without its two abstain rules | abstain_correct, missed_abstain_rate |
| `no-cite` | Prompt v1 without the citation rule | citation_valid, which is not gated |
| `chunk50` | `chunking.size_words` 300 to 50, overlap 10 | hit@5, fact_recall |
| `ctx1024` | `llm.num_ctx` 4096 to 1024, which cuts off the context | e2e_pass, fact_recall |
| `maxtok32` | `llm.max_tokens` 512 to 32, which cuts off the answer | format_error_rate, e2e_pass |
| `gate-high` | `abstention.min_score` set to the median top retrieval score of the answerable cases in the baseline run, so about half of them are refused | false_abstain_rate, e2e_pass |

### Controls

These must not be blocked.

| Name | Change |
|---|---|
| `rerun-1` to `rerun-5` | The baseline config, recorded again on the Mac. Three runs exist so far and agree on all 26 cases |
| `reworded` | Prompt v1 reworded with the same meaning |
| `seed43` | `llm.seed` 42 to 43 |

### One real change

`model-alt` (exists): the model swap to `llama3.2:3b`. The direction is not known in advance.

### What is recorded

For every run: the verdict of each check, the metric that caught it, the flip counts b and c, p, the flipped cases, and minutes to verdict (recording plus CI).

Every config runs on the Mac with `make regress CONFIG=...`, which applies the same comparison as the LLM gate, so each row is the verdict CI would give. Configs that change retrieval also run retrieval-only against `baselines/dev-retrieval`, as the retrieval gate does. Two real PRs, one bad and one harmless, are the live demo. At 26 cases the bad one has to break at least 6 cases, as closed-book does.

### Question 3

No new LLM calls. A script takes the full Mac runs for the baseline and each planted config, draws random subsets of 10, 20, 40, and all cases, applies the same gate rule, and reports how often the verdict is REGRESSION at each size.

### Results tables

All runs were on 2026-11-11, on the reference Mac (Apple M4, 16 GB, Ollama 0.40.3), with the 60 frozen dev cases (33 answerable, 27 not), one run at a time. The gate settings were not changed.

Each LLM gate verdict comes from `make regress CONFIG=...` against the recording `20261111-174152-baseline-d045262d` (e2e_pass 46 of 60, hit@5 30 of 33, abstain_correct 52 of 60). That is the comparison the LLM gate makes when a PR commits a recording of the change. Minutes are Mac wall time for one run of the 60 cases, about what `make record` takes. CI adds about 20 s. A cell like 10 / 2 / 0.039 means b = 10 cases went from pass to fail, c = 2 went from fail to pass, and the exact McNemar p is 0.039. [planted-runs.md](planted-runs.md) has every metric and every flipped case for each run.

#### 1. Detection

| Planted | Retrieval gate | LLM gate | e2e_pass | hit@5 | abstain_correct | Minutes |
|---|---|---|---|---|---|---:|
| `k1` | Blocked: hit@5 8 / 0 / 0.008 | Blocked by e2e_pass and hit@5 | 10 / 2 / 0.039 | 8 / 0 / 0.008 | 9 / 2 / 0.065 | 1.9 |
| `k3` | Passed: hit@5 1 / 0 / 1 | Passed | 2 / 2 / 1 | 1 / 0 / 1 | 1 / 2 / 1 | 2.8 |
| `closed-book` | Cannot run: `--retrieval-only` needs `system: rag` | Blocked by all three | 34 / 1 / < 0.001 | 30 / 0 / < 0.001 | 17 / 5 / 0.017 | 1.8 |
| `no-abstain` | No retrieval change | Passed with a warning | 7 / 2 / 0.18 | 0 / 0 / 1 | 7 / 3 / 0.34 | 11.3 |
| `no-cite` | No retrieval change | Passed | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 1 / 1 | 7.9 |
| `chunk50` | Passed with a warning: hit@5 3 / 1 / 0.625, hit@1 4 / 1 / 0.375 | Passed with a warning | 5 / 1 / 0.22 | 3 / 1 / 0.625 | 5 / 0 / 0.0625 | 2.8 |
| `ctx1024` | No retrieval change | Run failed with exit 2, nothing compared | n/a | n/a | n/a | 3.2 |
| `maxtok32` | No retrieval change | Blocked by e2e_pass and abstain_correct | 22 / 0 / < 0.001 | 0 / 0 / 1 | 28 / 0 / < 0.001 | 6.5 |
| `gate-high` | No retrieval change | Blocked by e2e_pass and abstain_correct | 11 / 2 / 0.022 | 0 / 0 / 1 | 13 / 2 / 0.007 | 1.1 |

Cases lost and gained on e2e_pass:

- `k1`: lost ff-007, om-001, om-003, om-004, om-007, om-009, om-010, om-015, om-022, om-028; gained ff-015, kp-005.
- `k3`: lost om-001, om-010; gained ff-015, kp-005.
- `closed-book`: lost 34 of the 46 passing cases; gained om-012.
- `no-abstain`: lost ff-016, ff-018, ff-019, om-015, om-030, om-033, om-034; gained kp-005, om-008.
- `chunk50`: lost ff-007, om-001, om-007, om-009, om-010; gained ff-008.
- `maxtok32`: lost 22, gained none.
- `gate-high`: lost ff-002, ff-003, ff-005, ff-006, ff-011, ff-012, kp-004, om-009, om-010, om-026, om-028; gained ff-015, om-012.

What the table shows:

- **Blocked by a verdict: 4 of 9.** The LLM gate blocked `k1`, `closed-book`, `maxtok32`, and `gate-high`. Each one broke 10 or more passing cases. `maxtok32` cut off 30 of the 60 replies. It counts as a regression only because of the 2026-11-11 change to `abstain_correct`. Before it, `compare` would have stopped with exit 2.
- **Blocked without a verdict: `ctx1024`.** Ollama 0.40.3 does not cut a long prompt. It refuses it with HTTP 400 ("exceeds the available context size"). 59 of the 60 prompts were 1,282 to 2,230 tokens; only `ff-010` (978 tokens) fit. The harness counts each refusal as an infra error, so the run stops with exit 2 and nothing is compared. `make record` refuses a run with infra errors, so a PR with this change would keep the old recording, and the LLM gate would fail it as out of date.
- **Got through: 2 real regressions.** Without its abstain rules, the bot answered 9 unanswerable questions instead of 2. It lost 7 passing cases and gained 2, so p = 0.18. In week 1, on 26 cases, the same change gave b = 3, c = 1. `chunk50` lost 5 and gained 1 on e2e_pass. On abstain_correct it lost 5 with none back, p = 0.0625, one flip short of the 6 the gate needs. Both only warned.
- **Passed, with a small effect or none: `k3` and `no-cite`.** `k3` lost one source page (`om-010`), and e2e_pass lost two cases and gained two. `no-cite` changed nothing the gate measures. All 30 answers still cited a document, and citation_valid went from 0.966 to 1.0, because the reply format still has a "citations" field. A change that drops citations would have to be in the code, not the prompt.
- **The retrieval column is not what CI would show.** These rows ran each planted config retrieval-only against main's `baselines/dev-retrieval`, as planned above. CI's retrieval gate does something else. It runs `configs/ci-retrieval.yaml`, which pins k to 5, and it compares with the PR's own `baselines/dev-retrieval`, which `make record` replaces in the same PR. So on a real PR it would pass both `k1` and `chunk50`. [Gaps](#gaps-in-the-current-code) lists this.

#### 2. False alarms

| Control | LLM gate | e2e_pass, hit@5, abstain_correct | Answers that differ from the recording | Minutes |
|---|---|---|---|---:|
| `rerun-1` | Passed | 0 / 0 / 1 on all three | 0 of 60 | 6.5 |
| `rerun-2` | Passed | 0 / 0 / 1 on all three | 0 of 60 | 7.5 |
| `rerun-3` | Passed | 0 / 0 / 1 on all three | 0 of 60 | 2.9 |
| `rerun-4` | Passed | 0 / 0 / 1 on all three | 0 of 60 | 4.3 awake |
| `rerun-5` | Passed | 0 / 0 / 1 on all three | 0 of 60 | 2.3 |
| `reworded` | Passed | 0 / 0 / 1 on all three | 18 of 60, no verdict changed | 8.2 |
| `seed43` | Passed | 0 / 0 / 1 on all three | 0 of 60 | 8.5 |

An answer differs if its text, abstain decision, citations, or status differ.

- **No false alarms: 0 of 7.** No control flipped a single case on a gated metric.
- **The Mac agreed with itself.** All five reruns matched the recording word for word on all 60 cases. That includes `rerun-4`, although the lid was closed from 14:38 to 15:38 and the Mac slept in the middle of it. Its 4.3 minutes is awake time; wall time was 62 minutes.
- **`seed43` is a weak control.** Temperature is 0, so the seed changes nothing. It gave the recording's answers on all 60.
- **`reworded`** changed the wording or citations of 18 answers and no verdict.
- **Latency was the only thing that warned.** Over the five reruns, latency_p95_s went from 5.2 to 10.4 s against 7.8 s in the recording, and `rerun-2` and `rerun-4` warned. It is not gated. The same config took 2.3 to 7.5 minutes with the same answers, so the minutes in both tables are rough.

#### 3. Sensitivity

Not done yet (step 6). It reuses the runs above, which stay in `runs/` on the Mac. `model-alt`, the one real change, has not run yet either.

## Test set

- **Today:** 26 dev cases (14 answerable, 12 not) in two files, `faeghe.jsonl` (21) and `koshish.jsonl` (5). No test split.
- **Target:** 60 dev cases. I add 34 in `data/testset/omar.jsonl` and check each one against its source page.
- **Second label:** the midterm report promised a blind second label on about 20% of cases. That needs one teammate.

## Where the work happens

I do all of it in my own fork, and the group reviews one pull request from the fork into the team repo.

The fork is needed for branch protection. Only the repo owner can require checks; in the fork I can, so a red check really blocks a merge. The first design also needed the fork for manually triggered workflows, but replay does not use any.

GitHub-hosted runners are free for public repositories, so the fork costs nothing.

Commits are grouped by workstream area so each owner can review their part:

| Area | Files | Reviewer |
|---|---|---|
| Runner | `src/deskrag/commands/evaluate.py`, `src/deskrag/evaluation/{runner,retrieval_only,subset}.py`, their tests | WS4 |
| CI and baselines | `.github/**`, `baselines/**`, `configs/ci-*`, `Makefile`, `src/deskrag/evaluation/replay.py`, `src/deskrag/commands/regress.py`, their tests | WS5 |
| LLM client, prompts, planted configs | `src/deskrag/rag/llm/**`, `src/deskrag/rag/prompts/**`, `configs/experiments/**` | WS3 |
| Cases | `data/testset/omar.jsonl` | WS1 |
| Docs | `docs/**` | Everyone |

## Order of work

1. Trial run on the GitHub runner. Done; it led to replay.
2. Finish `eval run --retrieval-only` and add the case-ID list option. Done.
3. Record the baselines, make the retrieval gate blocking, add the LLM gate job. Done, as replay.
4. Write the 34 new cases.
5. Planted configs and prompts, and the control runs, all on the Mac. Done on 2026-11-11 ([results](#results-tables)).
6. The resampling script.
7. Report, repo docs, deck.

| Week | Dates | Done when |
|---|---|---|
| 1 | Nov 9 to 15 | Steps 1 to 3 finished; the LLM gate passes on the fork's main; 19 of the new cases written, for 45 in total |
| 2 | Nov 16 to 22 | Steps 4 to 6 finished; the last 15 cases written and the set frozen at 60; the three results tables exist |
| 3 | Nov 23 to 29 | Step 7 finished; demo rehearsed |

The final is due two to four weeks after Nov 9. If it is two weeks, cut in this order:

1. The model swap, dense, and hybrid.
2. Cases stop at 45.
3. Resampling at one subset size instead of four.

## Week 1 status

As of 2026-11-11. Steps 1 to 3 are finished and the LLM gate passes on the fork's main (fork PRs #1 to #10). The 19 new cases are not started.

| Baseline | Numbers |
|---|---|
| `baselines/dev` (full pipeline, 26 cases) | e2e_pass 0.769 (20/26), hit@5 1.0, abstain_correct 0.923, fact_recall 0.769, no format errors |
| `baselines/dev-retrieval` (BM25 only) | hit@1 0.714, hit@3 1.0, hit@5 1.0, MRR 0.821 |

What the gates did with the changes they have seen so far:

| Change | Gate | Result | Right? |
|---|---|---|---|
| None: the dev split recorded again on the Mac | LLM | OK on every gated metric, no flips. Three such runs agree on all 26 cases | Yes |
| Prompt without its two abstain rules, old recording kept (fork PR #11, step 1) | LLM | Failed: "baselines/dev is out of date: the config or its prompt changed". Branch protection blocked the merge | Yes |
| The same prompt, recorded with `make record` (step 2) | LLM | Passed. e2e_pass 0.769 to 0.692 and abstain_correct 0.923 to 0.846. The bot answered three unanswerable questions it used to refuse (`ff-016`, `ff-018`, `ff-019`) and one answerable question it used to refuse (`kp-005`): b = 3, c = 1, p = 0.625, POSSIBLE | No: a real regression got through |
| `retrieval.k` 5 to 1, retrieval only | Retrieval | hit@5 1.0 to 0.714. Four cases lost their source page (`ff-008` to `ff-011`), none gained one: b = 4, c = 0, p = 0.125, POSSIBLE | No: a real regression got through |

The mechanics work: a stale recording fails, branch protection blocks the merge, and an unchanged rerun passes with no flips. The weak spot is the one question 3 is about. Both real regressions broke 3 or 4 cases, and at 26 cases the gate needs 6 with none going the other way. I did not change the gate settings to catch them; they stay frozen for the experiment. Abstention flips can only come from unanswerable cases and retrieval flips only from answerable ones, so the new cases need both kinds.

## What still needs the group

- **Review.** The pull request edits WS4 and WS5 files, which [CONTRIBUTING.md](../CONTRIBUTING.md) reserves for their owners.
- **Branch protection on the team repo.** Only Faeghe can turn it on.
- **A second labeler** for about 12 of the 60 cases.
- **Contributions.** The final report has to say who did what.

## Report and docs

- **Report:** new title, abstract, and the three questions. Sections IV-A to IV-C shrink into "the feature under test". Section IV-D grows into the main method. A new results section holds the three tables, plus the runner measurements that explain why CI replays a recording. Related work moves toward regression testing and behavioral testing of language models. The WS3 name placeholder in Section IV-F gets fixed.
- **Repo docs:** the CI section of [design.md](design.md) and the owners and milestones in [workplan.md](workplan.md) are updated to match. [baselines/README.md](../baselines/README.md) already describes replay.
- **Deck:** same layout, with the story changed to plant, detect, false alarms.

Working title: "An Evaluation Harness with CI Regression Testing for a University Help-Desk LLM Feature".

## Risks

- **Recording depends on one machine.** Every baseline comes from the reference Mac. If it is unavailable, or Ollama or the model changes, the baselines have to be recorded again on another machine, and that PR passes without a comparison.
- **The recorder is trusted.** CI cannot tell whether a recorded answer came from the model. Re-scoring catches edited scores but not edited answers, so `baselines/` diffs need a real review.
- **The Mac could disagree with itself.** It has not yet. Five reruns of unchanged code on the 60 cases matched the recording word for word, so reruns gave 0 false alarms in 5. Five runs cannot rule out a rare flip, and an Ollama or model update could change answers, which is the first risk again.
- **The gate is weak on small sets.** Week 1 showed it: two real regressions got through. Question 3 reports this plainly, and more cases raise the gate's power without loosening its rules.

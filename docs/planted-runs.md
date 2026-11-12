# Planted and control runs, 2026-11-11

Every run behind the detection and false-alarm tables in [harness-pivot.md](harness-pivot.md#results-tables), with all metrics and every flipped case. The [last section](#sensitivity) has the resampling behind the sensitivity table.

All runs used the reference Mac (Apple M4, 16 GB, macOS 27.0.1, Ollama 0.40.3) and the 60 frozen dev cases, one run at a time. LLM runs are `make regress CONFIG=...` with `DESKRAG_MACHINE=reference`, compared with the recording `20261111-174152-baseline-d045262d` under `configs/regression.yaml`. Retrieval-only runs use the retrieval gate's command with the planted config, compared with the recording `20261111-174749-ci-retrieval-d045262d` under `baselines/retrieval-gates.yaml`. The run folders are in `runs/` on the Mac, which git ignores.

**Re-scored on 2026-11-12.** After these runs, ff-015 ("How much does a semester student parking permit cost?") was relabeled from `missing_info` to `single_doc` with gold `acct007`, which lists the permit at $152.00. Before, the recording's correct answer counted as a missed abstention, and a run that refused the question got credit for it. The labels never reach the model; it only gets the question. So instead of running every config again, I scored the recorded answers of every run again with the new labels, the two recordings included, and ran `compare` again. The scoring is `rescore` in `src/deskrag/evaluation/replay.py`, the code `deskrag baseline check` uses. With the old labels it gives every run's stored scores exactly; with the new ones, only ff-015's row changes. No model was called. Every number below comes from the re-scored copies, which are in `runs/ff015-rescored/` on the Mac. Start times and minutes are from the original runs. The recording that replaced `baselines/dev` the same day (run `20261112-173221-baseline-d045262d`) gave the same answers on all 60 cases, word for word, so against it every row below would be the same except latency.

Failure tags in the recording: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

## Planted regressions

### `k1`

`configs/experiments/k1.yaml`, run `20261111-183057-k1-230af418`, started 13:30 EST. Exit 1: blocked. 1.9 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.616667 | -0.166667 | 0.05 | 11 | 1 | 0.00634766 | REGRESSION | yes |
| hit@5 | 0.911765 | 0.647059 | -0.264706 | 0.05 | 9 | 0 | 0.00390625 | REGRESSION | yes |
| abstain_correct | 0.883333 | 0.733333 | -0.15 | 0.05 | 10 | 1 | 0.0117188 | REGRESSION | yes |
| fact_recall | 0.857143 | 0.75 | -0.107143 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 3.15878 | -4.66168 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 11: ff-007, ff-015, om-001, om-003, om-004, om-007, om-009, om-010, om-015, om-022, om-028; gained 1: kp-005
- hit@5: lost 9: ff-008, ff-009, ff-010, ff-011, ff-015, om-004, om-009, om-010, om-023
- abstain_correct: lost 10: ff-008, ff-009, ff-015, om-004, om-005, om-007, om-009, om-010, om-015, om-022; gained 1: kp-005

Answers that differ from the recording (text, abstain decision, citations, or status): 26 of 60. Failure tags: FALSE_ABSTAIN_MODEL 14, RETRIEVAL_MISS 12, WRONG_ANSWER 7, MISSED_ABSTAIN 2.

### `k3`

`configs/experiments/k3.yaml`, run `20261111-183249-k3-b11887a8`, started 13:32 EST. Exit 0: no gated regression. 2.8 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.75 | -0.0333333 | 0.05 | 3 | 1 | 0.625 | OK | yes |
| hit@5 | 0.911765 | 0.852941 | -0.0588235 | 0.05 | 2 | 0 | 0.5 | POSSIBLE | yes |
| abstain_correct | 0.883333 | 0.866667 | -0.0166667 | 0.05 | 2 | 1 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.833333 | -0.0238095 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 4.77058 | -3.04988 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 3: ff-015, om-001, om-010; gained 1: kp-005
- hit@5: lost 2: ff-015, om-010
- abstain_correct: lost 2: ff-015, om-010; gained 1: kp-005

Answers that differ from the recording (text, abstain decision, citations, or status): 24 of 60. Failure tags: WRONG_ANSWER 7, FALSE_ABSTAIN_MODEL 7, RETRIEVAL_MISS 5, MISSED_ABSTAIN 1.

### `closed-book`

`configs/experiments/closed-book.yaml`, run `20261111-183540-closed-book-28802e2c`, started 13:35 EST. Exit 1: blocked. 1.8 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.216667 | -0.566667 | 0.05 | 35 | 1 | 1.07684e-09 | REGRESSION | yes |
| hit@5 | 0.911765 | 0 | -0.911765 | 0.05 | 31 | 0 | 9.31323e-10 | REGRESSION | yes |
| abstain_correct | 0.883333 | 0.683333 | -0.2 | 0.05 | 17 | 5 | 0.0169005 | REGRESSION | yes |
| fact_recall | 0.857143 | 0.0535714 | -0.803571 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 3.22656 | -4.5939 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 35: ff-001, ff-002, ff-003, ff-005, ff-006, ff-007, ff-011, ff-012, ff-013, ff-014, ff-015, kp-002, kp-004, om-001, om-002, om-003, om-004, om-006, om-007, om-009, om-010, om-011, om-013, om-014, om-015, om-017, om-021, om-022, om-026, om-028, om-029, om-030, om-031, om-032, om-033; gained 1: om-012
- hit@5: lost 31: ff-001, ff-002, ff-003, ff-004, ff-005, ff-006, ff-007, ff-008, ff-009, ff-010, ff-011, ff-012, ff-015, kp-004, kp-005, om-001, om-002, om-003, om-004, om-005, om-006, om-007, om-008, om-009, om-010, om-021, om-022, om-023, om-025, om-026, om-028
- abstain_correct: lost 17: ff-013, ff-014, kp-002, om-004, om-005, om-011, om-013, om-014, om-015, om-017, om-022, om-028, om-029, om-030, om-031, om-032, om-033; gained 5: kp-005, om-012, om-020, om-024, om-027

Answers that differ from the recording (text, abstain decision, citations, or status): 46 of 60. Failure tags: RETRIEVAL_MISS 34, WRONG_ANSWER 28, MISSED_ABSTAIN 13, FALSE_ABSTAIN_MODEL 6.

### `no-abstain`

`configs/experiments/no-abstain.yaml`, run `20261111-183729-no-abstain-c01645b6`, started 13:37 EST. Exit 0: no gated regression. 11.3 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.7 | -0.0833333 | 0.05 | 7 | 2 | 0.179688 | POSSIBLE | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.816667 | -0.0666667 | 0.05 | 7 | 3 | 0.34375 | POSSIBLE | yes |
| fact_recall | 0.857143 | 0.83871 | -0.0184332 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 35.9935 | +28.173 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 7: ff-016, ff-018, ff-019, om-015, om-030, om-033, om-034; gained 2: kp-005, om-008
- abstain_correct: lost 7: ff-016, ff-018, ff-019, om-015, om-030, om-033, om-034; gained 3: kp-005, om-008, om-027

Answers that differ from the recording (text, abstain decision, citations, or status): 26 of 60. Failure tags: MISSED_ABSTAIN 8, WRONG_ANSWER 7, RETRIEVAL_MISS 3, FALSE_ABSTAIN_MODEL 3, BAD_CITATION 2.

### `no-cite`

`configs/experiments/no-cite.yaml`, run `20261111-185622-no-cite-f4ba57f7`, started 13:56 EST. Exit 0: no gated regression. 7.9 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.9 | +0.0166667 | 0.05 | 0 | 1 | 1 | IMPROVED | yes |
| fact_recall | 0.857143 | 0.827586 | -0.0295567 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.6906 | +2.87012 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- abstain_correct: gained 1: om-027

Answers that differ from the recording (text, abstain decision, citations, or status): 20 of 60. Failure tags: WRONG_ANSWER 7, FALSE_ABSTAIN_MODEL 5, RETRIEVAL_MISS 3, MISSED_ABSTAIN 1.

### `chunk50`

`configs/experiments/chunk50.yaml`, run `20261111-190418-chunk50-fbe8fc90`, started 14:04 EST. Exit 0: no gated regression. 2.8 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.716667 | -0.0666667 | 0.05 | 5 | 1 | 0.21875 | POSSIBLE | yes |
| hit@5 | 0.911765 | 0.852941 | -0.0588235 | 0.05 | 3 | 1 | 0.625 | POSSIBLE | yes |
| abstain_correct | 0.883333 | 0.8 | -0.0833333 | 0.05 | 5 | 0 | 0.0625 | POSSIBLE | yes |
| fact_recall | 0.857143 | 0.847826 | -0.00931677 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 4.10119 | -3.71927 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 5: ff-007, om-001, om-007, om-009, om-010; gained 1: ff-008
- hit@5: lost 3: om-009, om-010, om-025; gained 1: om-024
- abstain_correct: lost 5: ff-007, om-007, om-009, om-010, om-025

Answers that differ from the recording (text, abstain decision, citations, or status): 20 of 60. Failure tags: FALSE_ABSTAIN_MODEL 11, WRONG_ANSWER 5, RETRIEVAL_MISS 5, MISSED_ABSTAIN 1.

### `ctx1024`

`configs/experiments/ctx1024.yaml`, run `20261111-190708-ctx1024-c3581445`, started 14:07 EST. Exit 2: the run failed, nothing was compared. 3.2 minutes.
Replies: 1 ok, 59 errors, 0 cut off, 0 unparsable.

No comparison. Ollama refused 59 of 60 requests with HTTP 400 (`exceed_context_size_error`): the prompts were 1,282 to 2,230 tokens and `num_ctx` was 1,024. The client tried each one 3 times.
Only `ff-010` fit (978 prompt tokens); it failed.

### `maxtok32`

`configs/experiments/maxtok32.yaml`, run `20261111-191020-maxtok32-10120677`, started 14:10 EST. Exit 1: blocked. 6.5 minutes.
Replies: 30 ok, 0 errors, 30 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.4 | -0.383333 | 0.05 | 23 | 0 | 2.38419e-07 | REGRESSION | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.4 | -0.483333 | 0.05 | 29 | 0 | 3.72529e-09 | REGRESSION | yes |
| fact_recall | n/a | n/a | n/a | n/a | n/a | n/a | n/a | NOT APPLICABLE | no |
| format_error_rate | 0 | 0.5 | +0.5 | 0.02 | 30 | 0 | 1.86265e-09 | REGRESSION | no |
| latency_p95_s | 7.82047 | 9.02874 | +1.20828 | 2 | 0 | 0 | n/a | OK | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 23: ff-001, ff-002, ff-003, ff-005, ff-006, ff-007, ff-011, ff-012, ff-015, kp-004, om-001, om-002, om-003, om-004, om-006, om-007, om-009, om-010, om-015, om-021, om-022, om-026, om-028
- abstain_correct: lost 29: ff-001, ff-002, ff-003, ff-004, ff-005, ff-006, ff-007, ff-008, ff-009, ff-010, ff-011, ff-012, ff-015, kp-004, om-001, om-002, om-003, om-004, om-005, om-006, om-007, om-009, om-010, om-015, om-021, om-022, om-025, om-026, om-028
- format_error_rate: lost 30: ff-001, ff-002, ff-003, ff-004, ff-005, ff-006, ff-007, ff-008, ff-009, ff-010, ff-011, ff-012, ff-015, kp-004, om-001, om-002, om-003, om-004, om-005, om-006, om-007, om-009, om-010, om-012, om-015, om-021, om-022, om-025, om-026, om-028

Answers that differ from the recording (text, abstain decision, citations, or status): 30 of 60. Failure tags: FORMAT_ERROR 30, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3.

### `gate-high`

`configs/experiments/gate-high.yaml`, run `20261111-191943-gate-high-ef7bef58`, started 14:19 EST. Exit 1: blocked. 1.1 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.6 | -0.183333 | 0.05 | 12 | 1 | 0.00341797 | REGRESSION | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.666667 | -0.216667 | 0.05 | 14 | 1 | 0.000976562 | REGRESSION | yes |
| fact_recall | 0.857143 | 0.785714 | -0.0714286 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 5.07263 | -2.74783 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 12: ff-002, ff-003, ff-005, ff-006, ff-011, ff-012, ff-015, kp-004, om-009, om-010, om-026, om-028; gained 1: om-012
- abstain_correct: lost 14: ff-002, ff-003, ff-004, ff-005, ff-006, ff-008, ff-011, ff-012, ff-015, kp-004, om-009, om-010, om-026, om-028; gained 1: om-012

Answers that differ from the recording (text, abstain decision, citations, or status): 15 of 60. Failure tags: FALSE_ABSTAIN_GATE 17, WRONG_ANSWER 4, FALSE_ABSTAIN_MODEL 3, RETRIEVAL_MISS 3.

## Controls

### `rerun-1`

`configs/baseline.yaml`, run `20261111-182357-baseline-d045262d`, started 13:23 EST. Exit 0: no gated regression. 6.5 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.883333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.857143 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 8.84455 | +1.02409 | 2 | 0 | 0 | n/a | OK | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

### `rerun-2`

`configs/baseline.yaml`, run `20261111-184850-baseline-d045262d`, started 13:48 EST. Exit 0: no gated regression. 7.5 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.883333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.857143 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.3036 | +2.48315 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

### `rerun-3`

`configs/baseline.yaml`, run `20261111-191650-baseline-d045262d`, started 14:16 EST. Exit 0: no gated regression. 2.9 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.883333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.857143 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 6.77754 | -1.04293 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

### `rerun-4`

`configs/baseline.yaml`, run `20261111-193728-baseline-d045262d`, started 14:37 EST. Exit 0: no gated regression. 4.3 minutes. The lid was closed from 14:38 to 15:38, so the Mac slept in the middle of this run. The minutes are awake time; wall time was 62 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.883333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.857143 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.3551 | +2.53461 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

### `rerun-5`

`configs/baseline.yaml`, run `20261111-203937-baseline-d045262d`, started 15:39 EST. Exit 0: no gated regression. 2.3 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.883333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.857143 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 5.16246 | -2.65801 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

### `reworded`

`configs/experiments/reworded.yaml`, run `20261111-192051-reworded-278cde98`, started 14:20 EST. Exit 0: no gated regression. 8.2 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.883333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.857143 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 11.1215 | +3.30103 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 18 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

### `seed43`

`configs/experiments/seed43.yaml`, run `20261111-192900-seed43-2a80d55c`, started 14:29 EST. Exit 0: no gated regression. 8.5 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.783333 | 0.783333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.883333 | 0.883333 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.857143 | 0.857143 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.8925 | +3.07202 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, BAD_CITATION 1, MISSED_ABSTAIN 1.

## Retrieval only

### `ci-retrieval`, retrieval only

`configs/ci-retrieval.yaml`, run `20261111-182353-ci-retrieval-d045262d`, started 13:23 EST. Exit 0: no gated regression. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.911765 | 0.911765 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@1 | 0.647059 | 0.647059 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| mrr | 0.75 | 0.75 | +0 | 0.05 | 0 | 0 | n/a | OK | no |

Flipped cases: none.

### `k1`, retrieval only

`configs/experiments/k1.yaml`, run `20261111-182353-k1-230af418`, started 13:23 EST. Exit 1: blocked. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.911765 | 0.647059 | -0.264706 | 0.05 | 9 | 0 | 0.00390625 | REGRESSION | yes |
| hit@1 | 0.647059 | 0.647059 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| mrr | 0.75 | 0.647059 | -0.102941 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- hit@5: lost 9: ff-008, ff-009, ff-010, ff-011, ff-015, om-004, om-009, om-010, om-023

### `k3`, retrieval only

`configs/experiments/k3.yaml`, run `20261111-182354-k3-b11887a8`, started 13:23 EST. Exit 0: no gated regression. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.911765 | 0.852941 | -0.0588235 | 0.05 | 2 | 0 | 0.5 | POSSIBLE | yes |
| hit@1 | 0.647059 | 0.647059 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| mrr | 0.75 | 0.735294 | -0.0147059 | 0.05 | 0 | 0 | n/a | OK | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- hit@5: lost 2: ff-015, om-010

### `chunk50`, retrieval only

`configs/experiments/chunk50.yaml`, run `20261111-182355-chunk50-fbe8fc90`, started 13:23 EST. Exit 0: no gated regression. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.911765 | 0.852941 | -0.0588235 | 0.05 | 3 | 1 | 0.625 | POSSIBLE | yes |
| hit@1 | 0.647059 | 0.558824 | -0.0882353 | 0.05 | 4 | 1 | 0.375 | POSSIBLE | yes |
| mrr | 0.75 | 0.693627 | -0.0563725 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- hit@5: lost 3: om-009, om-010, om-025; gained 1: om-024
- hit@1: lost 4: ff-002, kp-004, om-021, om-025; gained 1: ff-008

### `closed-book`, retrieval only

`configs/experiments/closed-book.yaml`, started 13:23 EST. Exit 2: the run failed, nothing was compared. About 1 second.

No run: `--retrieval-only` refused the config (needs a config with system: rag).

## Sensitivity

The resampling behind the [sensitivity table](harness-pivot.md#3-sensitivity), run on 2026-11-12 on the re-scored run folders above. No model was called and no run folder changed. Each size has 100,000 random subsets of the 60 case IDs, drawn without replacement with seed 20261112, and all 60 is judged once. Those are the command's defaults, so neither is passed below.

### LLM gate

Against the recording, under `configs/regression.yaml`:

```bash
uv run deskrag runs resample runs/ff015-rescored/20261111-174152-baseline-d045262d \
  closed-book=runs/ff015-rescored/20261111-183540-closed-book-28802e2c \
  maxtok32=runs/ff015-rescored/20261111-191020-maxtok32-10120677 \
  gate-high=runs/ff015-rescored/20261111-191943-gate-high-ef7bef58 \
  k1=runs/ff015-rescored/20261111-183057-k1-230af418 \
  no-abstain=runs/ff015-rescored/20261111-183729-no-abstain-c01645b6 \
  chunk50=runs/ff015-rescored/20261111-190418-chunk50-fbe8fc90 \
  k3=runs/ff015-rescored/20261111-183249-k3-b11887a8 \
  no-cite=runs/ff015-rescored/20261111-185622-no-cite-f4ba57f7 \
  rerun-1=runs/ff015-rescored/20261111-182357-baseline-d045262d \
  rerun-2=runs/ff015-rescored/20261111-184850-baseline-d045262d \
  rerun-3=runs/ff015-rescored/20261111-191650-baseline-d045262d \
  rerun-4=runs/ff015-rescored/20261111-193728-baseline-d045262d \
  rerun-5=runs/ff015-rescored/20261111-203937-baseline-d045262d \
  reworded=runs/ff015-rescored/20261111-192051-reworded-278cde98 \
  seed43=runs/ff015-rescored/20261111-192900-seed43-2a80d55c
```

The share of subsets on which each gated metric gets a REGRESSION verdict. Runs that are 0% on every metric at every size are left out: `chunk50`, `k3`, `no-cite`, and the seven controls.

| Run | Cases | e2e_pass | hit@5 | abstain_correct |
|---|---:|---:|---:|---:|
| `closed-book` | 10 | 53% | 41% | 1% |
| `closed-book` | 20 | 99% | >99% | 14% |
| `closed-book` | 40 | 100% | 100% | 42% |
| `maxtok32` | 10 | 12% | 0% | 32% |
| `maxtok32` | 20 | 89% | 0% | 99% |
| `maxtok32` | 40 | 100% | 0% | 100% |
| `gate-high` | 10 | <1% | 0% | 1% |
| `gate-high` | 20 | 11% | 0% | 21% |
| `gate-high` | 40 | 74% | 0% | 91% |
| `k1` | 10 | <1% | <1% | <1% |
| `k1` | 20 | 7% | 3% | 4% |
| `k1` | 40 | 60% | 66% | 45% |
| `no-abstain` | 10 | <1% | 0% | <1% |
| `no-abstain` | 20 | <1% | 0% | <1% |
| `no-abstain` | 40 | 3% | 0% | 1% |

In 10 of the 100,000 subsets of 10, no case is answerable, so hit@5 applies to none of them and cannot block those subsets.

### Retrieval gate

Against `baselines/dev-retrieval`, under `baselines/retrieval-gates.yaml`. These are the retrieval-only runs from [Retrieval only](#retrieval-only); `closed-book` has none.

```bash
uv run deskrag runs resample runs/ff015-rescored/20261111-174749-ci-retrieval-d045262d \
  k1=runs/ff015-rescored/20261111-182353-k1-230af418 \
  chunk50=runs/ff015-rescored/20261111-182355-chunk50-fbe8fc90 \
  k3=runs/ff015-rescored/20261111-182354-k3-b11887a8 \
  ci-retrieval=runs/ff015-rescored/20261111-182353-ci-retrieval-d045262d \
  --gates baselines/retrieval-gates.yaml
```

| Run | Lowest p on all 60 | 10 cases | 20 cases | 40 cases | All 60 |
|---|---|---:|---:|---:|---:|
| `k1` | hit@5 9 / 0 / 0.00391 | <1% | 3% | 66% | 100% |
| `chunk50` | hit@1 4 / 1 / 0.375 | 0% | 0% | 0% | 0% |
| `k3` | hit@5 2 / 0 / 0.5 | 0% | 0% | 0% | 0% |
| `ci-retrieval` | none | 0% | 0% | 0% | 0% |

Every block comes from hit@5. hit@1 got no REGRESSION verdict on any subset. In the same 10 subsets of 10, neither hit@5 nor hit@1 applies to any case.

### Checks

- **Seed.** Rerunning both with seed 1 moved no cell by more than 0.42 points for the LLM gate and 0.22 for the retrieval gate. Before the relabel, at 10,000 subsets per size the largest move was 1.05 points, so I used 100,000.
- **Exact odds.** Three cells follow from the flipped cases above, and the resampled shares match them. k1's hit@5 at 40 cases needs at least 6 of its 9 lost cases in the subset: 65.82%, resampled 66%. maxtok32's abstain_correct at 20 needs at least 6 of its 29: 98.95%, resampled 99%. no-abstain at 40 needs at least 6 of its 7 lost cases and neither of the 2 it gained: 3.13%, resampled 3%.
- **Same rule as `compare`.** The command judges the full set with `compare`'s own code and stops if its verdict differs. `compare.py` was split up so the command could reuse it. Before and after that change, `compare` run on copies of the 19 original run folders gave the `compare.md` already in each one, byte for byte.

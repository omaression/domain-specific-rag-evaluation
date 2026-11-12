# Planted and control runs, 2026-11-11

Every run behind the detection and false-alarm tables in [harness-pivot.md](harness-pivot.md#results-tables), with all metrics and every flipped case. The [last section](#sensitivity) has the resampling behind the sensitivity table.

All runs used the reference Mac (Apple M4, 16 GB, macOS 27.0.1, Ollama 0.40.3) and the 60 frozen dev cases, one run at a time. LLM runs are `make regress CONFIG=...` with `DESKRAG_MACHINE=reference`, compared with `baselines/dev` (run `20261111-174152-baseline-d045262d`) under `configs/regression.yaml`. Retrieval-only runs use the retrieval gate's command with the planted config, compared with `baselines/dev-retrieval` (run `20261111-174749-ci-retrieval-d045262d`) under `baselines/retrieval-gates.yaml`. The run folders are in `runs/` on the Mac, which git ignores.

Failure tags in the recording: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

## Planted regressions

### `k1`

`configs/experiments/k1.yaml`, run `20261111-183057-k1-230af418`, started 13:30 EST. Exit 1: blocked. 1.9 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.633333 | -0.133333 | 0.05 | 10 | 2 | 0.0385742 | REGRESSION | yes |
| hit@5 | 0.909091 | 0.666667 | -0.242424 | 0.05 | 8 | 0 | 0.0078125 | REGRESSION | yes |
| abstain_correct | 0.866667 | 0.75 | -0.116667 | 0.05 | 9 | 2 | 0.0654297 | POSSIBLE | yes |
| fact_recall | 0.851852 | 0.75 | -0.101852 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 3.15878 | -4.66168 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 10: ff-007, om-001, om-003, om-004, om-007, om-009, om-010, om-015, om-022, om-028; gained 2: ff-015, kp-005
- hit@5: lost 8: ff-008, ff-009, ff-010, ff-011, om-004, om-009, om-010, om-023
- abstain_correct: lost 9: ff-008, ff-009, om-004, om-005, om-007, om-009, om-010, om-015, om-022; gained 2: ff-015, kp-005

Answers that differ from the recording (text, abstain decision, citations, or status): 26 of 60. Failure tags: FALSE_ABSTAIN_MODEL 13, RETRIEVAL_MISS 11, WRONG_ANSWER 7, MISSED_ABSTAIN 2.

### `k3`

`configs/experiments/k3.yaml`, run `20261111-183249-k3-b11887a8`, started 13:32 EST. Exit 0: no gated regression. 2.8 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 2 | 2 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.878788 | -0.030303 | 0.05 | 1 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.883333 | +0.0166667 | 0.05 | 1 | 2 | 1 | IMPROVED | yes |
| fact_recall | 0.851852 | 0.833333 | -0.0185185 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 4.77058 | -3.04988 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 2: om-001, om-010; gained 2: ff-015, kp-005
- hit@5: lost 1: om-010
- abstain_correct: lost 1: om-010; gained 2: ff-015, kp-005

Answers that differ from the recording (text, abstain decision, citations, or status): 24 of 60. Failure tags: WRONG_ANSWER 7, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 4, MISSED_ABSTAIN 1.

### `closed-book`

`configs/experiments/closed-book.yaml`, run `20261111-183540-closed-book-28802e2c`, started 13:35 EST. Exit 1: blocked. 1.8 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.216667 | -0.55 | 0.05 | 34 | 1 | 2.09548e-09 | REGRESSION | yes |
| hit@5 | 0.909091 | 0 | -0.909091 | 0.05 | 30 | 0 | 1.86265e-09 | REGRESSION | yes |
| abstain_correct | 0.866667 | 0.666667 | -0.2 | 0.05 | 17 | 5 | 0.0169005 | REGRESSION | yes |
| fact_recall | 0.851852 | 0.0555556 | -0.796296 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 3.22656 | -4.5939 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 34: ff-001, ff-002, ff-003, ff-005, ff-006, ff-007, ff-011, ff-012, ff-013, ff-014, kp-002, kp-004, om-001, om-002, om-003, om-004, om-006, om-007, om-009, om-010, om-011, om-013, om-014, om-015, om-017, om-021, om-022, om-026, om-028, om-029, om-030, om-031, om-032, om-033; gained 1: om-012
- hit@5: lost 30: ff-001, ff-002, ff-003, ff-004, ff-005, ff-006, ff-007, ff-008, ff-009, ff-010, ff-011, ff-012, kp-004, kp-005, om-001, om-002, om-003, om-004, om-005, om-006, om-007, om-008, om-009, om-010, om-021, om-022, om-023, om-025, om-026, om-028
- abstain_correct: lost 17: ff-013, ff-014, kp-002, om-004, om-005, om-011, om-013, om-014, om-015, om-017, om-022, om-028, om-029, om-030, om-031, om-032, om-033; gained 5: kp-005, om-012, om-020, om-024, om-027

Answers that differ from the recording (text, abstain decision, citations, or status): 46 of 60. Failure tags: RETRIEVAL_MISS 33, WRONG_ANSWER 27, MISSED_ABSTAIN 14, FALSE_ABSTAIN_MODEL 6.

### `no-abstain`

`configs/experiments/no-abstain.yaml`, run `20261111-183729-no-abstain-c01645b6`, started 13:37 EST. Exit 0: no gated regression. 11.3 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.683333 | -0.0833333 | 0.05 | 7 | 2 | 0.179688 | POSSIBLE | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.8 | -0.0666667 | 0.05 | 7 | 3 | 0.34375 | POSSIBLE | yes |
| fact_recall | 0.851852 | 0.833333 | -0.0185185 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 35.9935 | +28.173 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 7: ff-016, ff-018, ff-019, om-015, om-030, om-033, om-034; gained 2: kp-005, om-008
- abstain_correct: lost 7: ff-016, ff-018, ff-019, om-015, om-030, om-033, om-034; gained 3: kp-005, om-008, om-027

Answers that differ from the recording (text, abstain decision, citations, or status): 26 of 60. Failure tags: MISSED_ABSTAIN 9, WRONG_ANSWER 7, RETRIEVAL_MISS 3, FALSE_ABSTAIN_MODEL 3, BAD_CITATION 2.

### `no-cite`

`configs/experiments/no-cite.yaml`, run `20261111-185622-no-cite-f4ba57f7`, started 13:56 EST. Exit 0: no gated regression. 7.9 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.883333 | +0.0166667 | 0.05 | 0 | 1 | 1 | IMPROVED | yes |
| fact_recall | 0.851852 | 0.821429 | -0.0304233 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.6906 | +2.87012 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- abstain_correct: gained 1: om-027

Answers that differ from the recording (text, abstain decision, citations, or status): 20 of 60. Failure tags: WRONG_ANSWER 7, FALSE_ABSTAIN_MODEL 5, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2.

### `chunk50`

`configs/experiments/chunk50.yaml`, run `20261111-190418-chunk50-fbe8fc90`, started 14:04 EST. Exit 0: no gated regression. 2.8 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.7 | -0.0666667 | 0.05 | 5 | 1 | 0.21875 | POSSIBLE | yes |
| hit@5 | 0.909091 | 0.848485 | -0.0606061 | 0.05 | 3 | 1 | 0.625 | POSSIBLE | yes |
| abstain_correct | 0.866667 | 0.783333 | -0.0833333 | 0.05 | 5 | 0 | 0.0625 | POSSIBLE | yes |
| fact_recall | 0.851852 | 0.840909 | -0.0109428 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 4.10119 | -3.71927 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 5: ff-007, om-001, om-007, om-009, om-010; gained 1: ff-008
- hit@5: lost 3: om-009, om-010, om-025; gained 1: om-024
- abstain_correct: lost 5: ff-007, om-007, om-009, om-010, om-025

Answers that differ from the recording (text, abstain decision, citations, or status): 20 of 60. Failure tags: FALSE_ABSTAIN_MODEL 11, WRONG_ANSWER 5, RETRIEVAL_MISS 5, MISSED_ABSTAIN 2.

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
| e2e_pass | 0.766667 | 0.4 | -0.366667 | 0.05 | 22 | 0 | 4.76837e-07 | REGRESSION | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.4 | -0.466667 | 0.05 | 28 | 0 | 7.45058e-09 | REGRESSION | yes |
| fact_recall | n/a | n/a | n/a | n/a | n/a | n/a | n/a | NOT APPLICABLE | no |
| format_error_rate | 0 | 0.5 | +0.5 | 0.02 | 30 | 0 | 1.86265e-09 | REGRESSION | no |
| latency_p95_s | 7.82047 | 9.02874 | +1.20828 | 2 | 0 | 0 | n/a | OK | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 22: ff-001, ff-002, ff-003, ff-005, ff-006, ff-007, ff-011, ff-012, kp-004, om-001, om-002, om-003, om-004, om-006, om-007, om-009, om-010, om-015, om-021, om-022, om-026, om-028
- abstain_correct: lost 28: ff-001, ff-002, ff-003, ff-004, ff-005, ff-006, ff-007, ff-008, ff-009, ff-010, ff-011, ff-012, kp-004, om-001, om-002, om-003, om-004, om-005, om-006, om-007, om-009, om-010, om-015, om-021, om-022, om-025, om-026, om-028
- format_error_rate: lost 30: ff-001, ff-002, ff-003, ff-004, ff-005, ff-006, ff-007, ff-008, ff-009, ff-010, ff-011, ff-012, ff-015, kp-004, om-001, om-002, om-003, om-004, om-005, om-006, om-007, om-009, om-010, om-012, om-015, om-021, om-022, om-025, om-026, om-028

Answers that differ from the recording (text, abstain decision, citations, or status): 30 of 60. Failure tags: FORMAT_ERROR 30, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3.

### `gate-high`

`configs/experiments/gate-high.yaml`, run `20261111-191943-gate-high-ef7bef58`, started 14:19 EST. Exit 1: blocked. 1.1 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.616667 | -0.15 | 0.05 | 11 | 2 | 0.0224609 | REGRESSION | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.683333 | -0.183333 | 0.05 | 13 | 2 | 0.00738525 | REGRESSION | yes |
| fact_recall | 0.851852 | 0.785714 | -0.0661376 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 5.07263 | -2.74783 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- e2e_pass: lost 11: ff-002, ff-003, ff-005, ff-006, ff-011, ff-012, kp-004, om-009, om-010, om-026, om-028; gained 2: ff-015, om-012
- abstain_correct: lost 13: ff-002, ff-003, ff-004, ff-005, ff-006, ff-008, ff-011, ff-012, kp-004, om-009, om-010, om-026, om-028; gained 2: ff-015, om-012

Answers that differ from the recording (text, abstain decision, citations, or status): 15 of 60. Failure tags: FALSE_ABSTAIN_GATE 16, WRONG_ANSWER 4, FALSE_ABSTAIN_MODEL 3, RETRIEVAL_MISS 3.

## Controls

### `rerun-1`

`configs/baseline.yaml`, run `20261111-182357-baseline-d045262d`, started 13:23 EST. Exit 0: no gated regression. 6.5 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.866667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.851852 | 0.851852 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 8.84455 | +1.02409 | 2 | 0 | 0 | n/a | OK | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

### `rerun-2`

`configs/baseline.yaml`, run `20261111-184850-baseline-d045262d`, started 13:48 EST. Exit 0: no gated regression. 7.5 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.866667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.851852 | 0.851852 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.3036 | +2.48315 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

### `rerun-3`

`configs/baseline.yaml`, run `20261111-191650-baseline-d045262d`, started 14:16 EST. Exit 0: no gated regression. 2.9 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.866667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.851852 | 0.851852 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 6.77754 | -1.04293 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

### `rerun-4`

`configs/baseline.yaml`, run `20261111-193728-baseline-d045262d`, started 14:37 EST. Exit 0: no gated regression. 4.3 minutes. The lid was closed from 14:38 to 15:38, so the Mac slept in the middle of this run. The minutes are awake time; wall time was 62 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.866667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.851852 | 0.851852 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.3551 | +2.53461 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

### `rerun-5`

`configs/baseline.yaml`, run `20261111-203937-baseline-d045262d`, started 15:39 EST. Exit 0: no gated regression. 2.3 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.866667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.851852 | 0.851852 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 5.16246 | -2.65801 | 2 | 0 | 0 | n/a | IMPROVED | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

### `reworded`

`configs/experiments/reworded.yaml`, run `20261111-192051-reworded-278cde98`, started 14:20 EST. Exit 0: no gated regression. 8.2 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.866667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.851852 | 0.851852 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 11.1215 | +3.30103 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 18 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

### `seed43`

`configs/experiments/seed43.yaml`, run `20261111-192900-seed43-2a80d55c`, started 14:29 EST. Exit 0: no gated regression. 8.5 minutes.
Replies: 60 ok, 0 errors, 0 cut off, 0 unparsable.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| e2e_pass | 0.766667 | 0.766667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| abstain_correct | 0.866667 | 0.866667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| fact_recall | 0.851852 | 0.851852 | +0 | 0.05 | 0 | 0 | n/a | OK | no |
| format_error_rate | 0 | 0 | +0 | 0.02 | 0 | 0 | 1 | OK | no |
| latency_p95_s | 7.82047 | 10.8925 | +3.07202 | 2 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases: none.

Answers that differ from the recording (text, abstain decision, citations, or status): 0 of 60. Failure tags: WRONG_ANSWER 6, FALSE_ABSTAIN_MODEL 6, RETRIEVAL_MISS 3, MISSED_ABSTAIN 2, BAD_CITATION 1.

## Retrieval only

### `ci-retrieval`, retrieval only

`configs/ci-retrieval.yaml`, run `20261111-182353-ci-retrieval-d045262d`, started 13:23 EST. Exit 0: no gated regression. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.909091 | 0.909091 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| hit@1 | 0.666667 | 0.666667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| mrr | 0.765152 | 0.765152 | +0 | 0.05 | 0 | 0 | n/a | OK | no |

Flipped cases: none.

### `k1`, retrieval only

`configs/experiments/k1.yaml`, run `20261111-182353-k1-230af418`, started 13:23 EST. Exit 1: blocked. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.909091 | 0.666667 | -0.242424 | 0.05 | 8 | 0 | 0.0078125 | REGRESSION | yes |
| hit@1 | 0.666667 | 0.666667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| mrr | 0.765152 | 0.666667 | -0.0984848 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- hit@5: lost 8: ff-008, ff-009, ff-010, ff-011, om-004, om-009, om-010, om-023

### `k3`, retrieval only

`configs/experiments/k3.yaml`, run `20261111-182354-k3-b11887a8`, started 13:23 EST. Exit 0: no gated regression. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.909091 | 0.878788 | -0.030303 | 0.05 | 1 | 0 | 1 | OK | yes |
| hit@1 | 0.666667 | 0.666667 | +0 | 0.05 | 0 | 0 | 1 | OK | yes |
| mrr | 0.765152 | 0.757576 | -0.00757576 | 0.05 | 0 | 0 | n/a | OK | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- hit@5: lost 1: om-010

### `chunk50`, retrieval only

`configs/experiments/chunk50.yaml`, run `20261111-182355-chunk50-fbe8fc90`, started 13:23 EST. Exit 0: no gated regression. About 1 second.
Cases: 60 ok, 0 errors.

| Metric | Baseline | Candidate | Delta | Tolerance | b | c | p | Verdict | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| hit@5 | 0.909091 | 0.848485 | -0.0606061 | 0.05 | 3 | 1 | 0.625 | POSSIBLE | yes |
| hit@1 | 0.666667 | 0.575758 | -0.0909091 | 0.05 | 4 | 1 | 0.375 | POSSIBLE | yes |
| mrr | 0.765152 | 0.699495 | -0.0656566 | 0.05 | 0 | 0 | n/a | POSSIBLE | no |

Flipped cases (lost: pass to fail, counted in b; gained: fail to pass, counted in c):

- hit@5: lost 3: om-009, om-010, om-025; gained 1: om-024
- hit@1: lost 4: ff-002, kp-004, om-021, om-025; gained 1: ff-008

### `closed-book`, retrieval only

`configs/experiments/closed-book.yaml`, started 13:23 EST. Exit 2: the run failed, nothing was compared. About 1 second.

No run: `--retrieval-only` refused the config (needs a config with system: rag).

## Sensitivity

The resampling behind the [sensitivity table](harness-pivot.md#3-sensitivity), run on 2026-11-12 on the run folders above. No model was called and nothing in `runs/` changed. Each size has 100,000 random subsets of the 60 case IDs, drawn without replacement with seed 20261112, and all 60 is judged once. Those are the command's defaults, so neither is passed below.

### LLM gate

Against the recording, under `configs/regression.yaml`:

```bash
uv run deskrag runs resample runs/20261111-174152-baseline-d045262d \
  closed-book=runs/20261111-183540-closed-book-28802e2c \
  maxtok32=runs/20261111-191020-maxtok32-10120677 \
  gate-high=runs/20261111-191943-gate-high-ef7bef58 \
  k1=runs/20261111-183057-k1-230af418 \
  no-abstain=runs/20261111-183729-no-abstain-c01645b6 \
  chunk50=runs/20261111-190418-chunk50-fbe8fc90 \
  k3=runs/20261111-183249-k3-b11887a8 \
  no-cite=runs/20261111-185622-no-cite-f4ba57f7 \
  rerun-1=runs/20261111-182357-baseline-d045262d \
  rerun-2=runs/20261111-184850-baseline-d045262d \
  rerun-3=runs/20261111-191650-baseline-d045262d \
  rerun-4=runs/20261111-193728-baseline-d045262d \
  rerun-5=runs/20261111-203937-baseline-d045262d \
  reworded=runs/20261111-192051-reworded-278cde98 \
  seed43=runs/20261111-192900-seed43-2a80d55c
```

The share of subsets on which each gated metric gets a REGRESSION verdict. Runs that are 0% on every metric at every size are left out: `chunk50`, `k3`, `no-cite`, and the seven controls.

| Run | Cases | e2e_pass | hit@5 | abstain_correct |
|---|---:|---:|---:|---:|
| `closed-book` | 10 | 49% | 36% | 1% |
| `closed-book` | 20 | 99% | 99% | 14% |
| `closed-book` | 40 | 100% | 100% | 42% |
| `maxtok32` | 10 | 10% | 0% | 28% |
| `maxtok32` | 20 | 85% | 0% | 98% |
| `maxtok32` | 40 | 100% | 0% | 100% |
| `gate-high` | 10 | <1% | 0% | <1% |
| `gate-high` | 20 | 5% | 0% | 11% |
| `gate-high` | 40 | 34% | 0% | 58% |
| `k1` | 10 | <1% | <1% | <1% |
| `k1` | 20 | 3% | 1% | 2% |
| `k1` | 40 | 23% | 46% | 14% |
| `no-abstain` | 10 | <1% | 0% | <1% |
| `no-abstain` | 20 | <1% | 0% | <1% |
| `no-abstain` | 40 | 3% | 0% | 1% |

In 13 of the 100,000 subsets of 10, no case is answerable, so hit@5 applies to none of them and cannot block those subsets.

### Retrieval gate

Against `baselines/dev-retrieval`, under `baselines/retrieval-gates.yaml`. These are the retrieval-only runs from [Retrieval only](#retrieval-only); `closed-book` has none.

```bash
uv run deskrag runs resample runs/20261111-174749-ci-retrieval-d045262d \
  k1=runs/20261111-182353-k1-230af418 \
  chunk50=runs/20261111-182355-chunk50-fbe8fc90 \
  k3=runs/20261111-182354-k3-b11887a8 \
  ci-retrieval=runs/20261111-182353-ci-retrieval-d045262d \
  --gates baselines/retrieval-gates.yaml
```

| Run | Lowest p on all 60 | 10 cases | 20 cases | 40 cases | All 60 |
|---|---|---:|---:|---:|---:|
| `k1` | hit@5 8 / 0 / 0.00781 | <1% | 1% | 46% | 100% |
| `chunk50` | hit@1 4 / 1 / 0.375 | 0% | 0% | 0% | 0% |
| `k3` | hit@5 1 / 0 / 1 | 0% | 0% | 0% | 0% |
| `ci-retrieval` | none | 0% | 0% | 0% | 0% |

Every block comes from hit@5. hit@1 got no REGRESSION verdict on any subset. In the same 13 subsets of 10, neither hit@5 nor hit@1 applies to any case.

### Checks

- **Seed.** Rerunning both with seed 1 moved no cell by more than 0.40 points for the LLM gate and 0.18 for the retrieval gate. At 10,000 subsets per size the largest move was 1.05 points, so I used 100,000.
- **Exact odds.** Three cells follow from the flipped cases above, and the resampled shares match them. k1's hit@5 at 40 cases needs at least 6 of its 8 lost cases in the subset: 46.08%, resampled 46%. maxtok32's abstain_correct at 20 needs at least 6 of its 28: 98.33%, resampled 98%. no-abstain at 40 needs at least 6 of its 7 lost cases and neither of the 2 it gained: 3.13%, resampled 3%.
- **Same rule as `compare`.** The command judges the full set with `compare`'s own code and stops if its verdict differs. `compare.py` was split up so the command could reuse it. Before and after that change, `compare` run on copies of the 19 run folders above gave the `compare.md` already in each one, byte for byte.

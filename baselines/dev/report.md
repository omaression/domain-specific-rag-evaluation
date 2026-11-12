# Evaluation report

Run: `20261112-173221-baseline-d045262d`
Split: dev; cases: 60; reps: 1
Dataset SHA256: `4892f42662c966365d77c2e0f17cdab0f80028c9a708becdf88fe45539b7e307`
Config SHA256: `d045262d3b07af2dd08a233e536ee4064e0a88e83e10d2d23e0d97e73dae52ad`
Machine: reference

## Counts

| Count | Value |
|---|---:|
| cases | 60 |
| ok | 60 |
| errors | 0 |
| truncated | 0 |
| parse_errors | 0 |

## Metrics

| Metric | Value |
|---|---:|
| abstain_correct | 0.883333 |
| abstain_f1 | 0.877193 |
| abstain_precision | 0.806452 |
| abstain_recall | 0.961538 |
| answer_correct | 0.785714 |
| citation_hit | 0.896552 |
| citation_valid | 0.965517 |
| completion_tokens_mean | 39.4667 |
| e2e_pass | 0.783333 |
| fact_recall | 0.857143 |
| false_abstain_rate | 0.176471 |
| format_error_rate | 0 |
| hit@1 | 0.647059 |
| hit@3 | 0.852941 |
| hit@5 | 0.911765 |
| latency_p50_s | 6.06736 |
| latency_p95_s | 8.78991 |
| missed_abstain_rate | 0.0384615 |
| mrr | 0.75 |
| prompt_tokens_mean | 1692.57 |
| recall@5 | 0.882353 |

## false_premise

| Metric | Value |
|---|---:|
| abstain_correct | 1 |
| abstain_f1 | 1 |
| abstain_precision | 1 |
| abstain_recall | 1 |
| answer_correct | n/a |
| citation_hit | n/a |
| citation_valid | n/a |
| completion_tokens_mean | 19.1429 |
| e2e_pass | 1 |
| fact_recall | n/a |
| false_abstain_rate | n/a |
| format_error_rate | 0 |
| hit@1 | n/a |
| hit@3 | n/a |
| hit@5 | n/a |
| latency_p50_s | 5.47511 |
| latency_p95_s | 6.39723 |
| missed_abstain_rate | 0 |
| mrr | n/a |
| prompt_tokens_mean | 1674.86 |
| recall@5 | n/a |

## missing_info

| Metric | Value |
|---|---:|
| abstain_correct | 0.875 |
| abstain_f1 | 0.933333 |
| abstain_precision | 1 |
| abstain_recall | 0.875 |
| answer_correct | n/a |
| citation_hit | 0 |
| citation_valid | 1 |
| completion_tokens_mean | 25.625 |
| e2e_pass | 0.875 |
| fact_recall | n/a |
| false_abstain_rate | n/a |
| format_error_rate | 0 |
| hit@1 | n/a |
| hit@3 | n/a |
| hit@5 | n/a |
| latency_p50_s | 5.81434 |
| latency_p95_s | 7.23763 |
| missed_abstain_rate | 0.125 |
| mrr | n/a |
| prompt_tokens_mean | 1708.88 |
| recall@5 | n/a |

## multi_doc

| Metric | Value |
|---|---:|
| abstain_correct | 0.777778 |
| abstain_f1 | 0 |
| abstain_precision | 0 |
| abstain_recall | 0 |
| answer_correct | 0.571429 |
| citation_hit | 0.857143 |
| citation_valid | 1 |
| completion_tokens_mean | 64.2222 |
| e2e_pass | 0.444444 |
| fact_recall | 0.714286 |
| false_abstain_rate | 0.222222 |
| format_error_rate | 0 |
| hit@1 | 0.666667 |
| hit@3 | 0.888889 |
| hit@5 | 0.888889 |
| latency_p50_s | 6.81876 |
| latency_p95_s | 10.0659 |
| missed_abstain_rate | n/a |
| mrr | 0.759259 |
| prompt_tokens_mean | 1791 |
| recall@5 | 0.777778 |

## out_of_domain

| Metric | Value |
|---|---:|
| abstain_correct | 1 |
| abstain_f1 | 1 |
| abstain_precision | 1 |
| abstain_recall | 1 |
| answer_correct | n/a |
| citation_hit | n/a |
| citation_valid | n/a |
| completion_tokens_mean | 18 |
| e2e_pass | 1 |
| fact_recall | n/a |
| false_abstain_rate | n/a |
| format_error_rate | 0 |
| hit@1 | n/a |
| hit@3 | n/a |
| hit@5 | n/a |
| latency_p50_s | 5.29185 |
| latency_p95_s | 5.92727 |
| missed_abstain_rate | 0 |
| mrr | n/a |
| prompt_tokens_mean | 1649 |
| recall@5 | n/a |

## paraphrase

| Metric | Value |
|---|---:|
| abstain_correct | 0.777778 |
| abstain_f1 | 0 |
| abstain_precision | 0 |
| abstain_recall | 0 |
| answer_correct | 0.857143 |
| citation_hit | 0.857143 |
| citation_valid | 0.857143 |
| completion_tokens_mean | 50.3333 |
| e2e_pass | 0.666667 |
| fact_recall | 0.857143 |
| false_abstain_rate | 0.222222 |
| format_error_rate | 0 |
| hit@1 | 0.444444 |
| hit@3 | 0.777778 |
| hit@5 | 0.888889 |
| latency_p50_s | 6.09344 |
| latency_p95_s | 7.50706 |
| missed_abstain_rate | n/a |
| mrr | 0.601852 |
| prompt_tokens_mean | 1526 |
| recall@5 | 0.888889 |

## personal

| Metric | Value |
|---|---:|
| abstain_correct | 1 |
| abstain_f1 | 1 |
| abstain_precision | 1 |
| abstain_recall | 1 |
| answer_correct | n/a |
| citation_hit | n/a |
| citation_valid | n/a |
| completion_tokens_mean | 19.8333 |
| e2e_pass | 1 |
| fact_recall | n/a |
| false_abstain_rate | n/a |
| format_error_rate | 0 |
| hit@1 | n/a |
| hit@3 | n/a |
| hit@5 | n/a |
| latency_p50_s | 5.07418 |
| latency_p95_s | 6.50461 |
| missed_abstain_rate | 0 |
| mrr | n/a |
| prompt_tokens_mean | 1649.67 |
| recall@5 | n/a |

## single_doc

| Metric | Value |
|---|---:|
| abstain_correct | 0.875 |
| abstain_f1 | 0 |
| abstain_precision | 0 |
| abstain_recall | 0 |
| answer_correct | 0.857143 |
| citation_hit | 1 |
| citation_valid | 1 |
| completion_tokens_mean | 49.3125 |
| e2e_pass | 0.75 |
| fact_recall | 0.928571 |
| false_abstain_rate | 0.125 |
| format_error_rate | 0 |
| hit@1 | 0.75 |
| hit@3 | 0.875 |
| hit@5 | 0.9375 |
| latency_p50_s | 6.66923 |
| latency_p95_s | 8.23158 |
| missed_abstain_rate | n/a |
| mrr | 0.828125 |
| prompt_tokens_mean | 1760.19 |
| recall@5 | 0.9375 |

## Failure counts

| Tag | Count |
|---|---:|
| BAD_CITATION | 1 |
| FALSE_ABSTAIN_MODEL | 6 |
| MISSED_ABSTAIN | 1 |
| RETRIEVAL_MISS | 3 |
| WRONG_ANSWER | 6 |

## Failed cases

| Case | Rep | Status | Failure tags |
|---|---:|---|---|
| ff-004 | 0 | ok | WRONG_ANSWER |
| ff-008 | 0 | ok | WRONG_ANSWER |
| ff-009 | 0 | ok | WRONG_ANSWER |
| ff-010 | 0 | ok | WRONG_ANSWER |
| kp-005 | 0 | ok | FALSE_ABSTAIN_MODEL |
| om-005 | 0 | ok | WRONG_ANSWER |
| om-008 | 0 | ok | FALSE_ABSTAIN_MODEL |
| om-012 | 0 | ok | MISSED_ABSTAIN |
| om-020 | 0 | ok | RETRIEVAL_MISS, FALSE_ABSTAIN_MODEL |
| om-023 | 0 | ok | FALSE_ABSTAIN_MODEL |
| om-024 | 0 | ok | RETRIEVAL_MISS, FALSE_ABSTAIN_MODEL |
| om-025 | 0 | ok | WRONG_ANSWER |
| om-027 | 0 | ok | RETRIEVAL_MISS, FALSE_ABSTAIN_MODEL |

Infrastructure errors are unscored and prevent comparison or baseline promotion.
A report is descriptive. A separate comparison determines regression verdicts.

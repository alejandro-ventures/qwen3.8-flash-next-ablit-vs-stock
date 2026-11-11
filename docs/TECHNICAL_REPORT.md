# Technical report: methods, full tables and reproducibility

This record provides the complete tables, configuration, deviations and analysis specification. The [main report](../REPORT.md) presents the findings with standalone figures. Capability conclusions are conditional on D8-amended traffic eligibility; original-rule BFCL-related gates remain inconclusive.

## Design and configuration

A **protocol recorded before B collection (tag `protocol-v1`), with disclosed deviations**; the collection order was A1, B1, B2, A2 (A-B-B-A), each started from a fresh restart. A is stock (`ABLIT=0`); B is the pinned `ABLIT=1` overlay. One GB10 machine (DGX Spark class, 128 GB unified memory). Same recipe `20e15e4`, published image, checkpoint, context 262,144, PARALLEL 5, fp8 KV, vision on and greedy decoding. ABBA balances linear drift only; it does not separate drift from nondeterminism. A0 (`fd3f43e`, locally built image) is an upgrade diagnostic and is excluded from the primary overlay contrast. C1 is separate and exploratory.

Thinking settings are profile-specific: MMLU-Pro, math and code use thinking on; IFEval, MGSM, BFCL and primary refusal use thinking off. The mixed workload uses four concurrent requests (long context two). [Every request profile, cap, timeout and retry](../docs/REQUEST_PAYLOADS.md) is documented. This is not an all-thinking-off capability benchmark.

The protocol is a [redacted transcription](../PROTOCOL.md), with a [redaction ledger](../REDACTIONS.md) and [deviation log](../DEVIATIONS.md). Historical protocol language is retained even where later corrections supersede it; the correction notes and this report state the final interpretation. No private git history is included. The `analysis-v1` tag was created retroactively, so it cannot prove advance analysis specification. `analysis/compare.py` is byte-identical to the pre-B git blob `c544884f00ce4d08dee4901bc6ef1f16767155b6`, as supplied in the study's provenance record. The extended analysis was written after the data existed, with its later stratification correction disclosed in D13.

Before B1 collection, the overlay-active gate required the expected serve-path suffix, sidecar and view-index hashes, and at least one different greedy token hash from A1 among the 200 Layer 2 prompts. These are activation checks, not loader-level proof that every intended tensor was replaced; the engine did not supply that proof. The recorded artifact hashes are published without host metadata.

## Planned auxiliary outcome: unreported

The protocol also planned a pairwise win rate for 59 auxiliary prompts and a 20-pair check. Responses were collected, but completion of that judging/check is unverified in the retained records, and no auxiliary result is reported. This planned exploratory outcome is not part of the six-benchmark composite or primary gates. It must not be treated as completed with hidden results. See [D16](../DEVIATIONS.md#d16-recorded-2026-11-12-planned-auxiliary-judging-outcome-unreported) and the [erratum](../ERRATA.md).

## Capability

### Capability B_vs_A (Y minus X; X=A1+A2, Y=B1+B2); stratified bootstrap
| benchmark | n items | X % | Y % | d (pp) | 95% CI (pp) |
|---|---|---|---|---|---|
| mmlu_pro | 420 | 87.1 | 83.3 | -3.81 | [-6.43, -1.19] |
| math500 | 500 | 91.6 | 89.0 | -2.60 | [-4.20, -1.00] |
| code | 363 | 86.8 | 85.7 | -1.10 | [-3.86, +1.65] |
| ifeval | 541 | 84.5 | 85.1 | +0.65 | [-2.03, +3.33] |
| mgsm | 750 | 95.1 | 93.1 | -2.00 | [-3.87, -0.13] |
| bfcl | 300 | 87.3 | 78.7 | -8.67 | [-13.00, -4.33] |
| **composite** | | 88.7 | 85.8 | -2.92 | [-4.08, -1.77] |

H1's entire interval is below the -1.5 pp margin under D8-amended eligibility: the data support a loss larger than that margin conditional on the collected sessions and the amended rule. Under the original rule, BFCL-related gates remain inconclusive; excluding BFCL changes the composite and does not establish the same beyond-margin conclusion. The frozen unstratified script gives -2.92 pp [-4.10, -1.77]; the headline uses the post-data corrected stratification. [Full category triggers and transition tables](../analysis/extra_tables.md) include all 12 lower-bound category flags, not only the strongest ones. BFCL parallel provides stronger evidence than the small MMLU-Pro category samples (30 each). A lower-bound trigger indicates a possible consequential loss, not an established category collapse.

### Layer 1 engine checks (H2 gating set): pass / FAIL / missing; a check that fails in an A run is reported and excluded from the gate
| check | A1 | A2 | B1 | B2 | C1 | gate (B passes wherever A passes) |
|---|---|---|---|---|---|---|
| exact | pass | pass | pass | pass | pass | pass |
| needle_200k | pass | pass | pass | pass | pass | pass |
| toolcheck | pass | pass | pass | pass | pass | pass |
| prompt_reuse | pass | pass | pass | pass | pass | pass |
| context_boundary | pass | pass | pass | pass | pass | pass |
| visioncheck | pass | pass | pass | pass | pass | pass |
Layer 1 second-attempt files present: none

Every engine check passed in all primary sessions and C1. These checks compare a build with itself; they do not establish A/B byte identity or general correctness. The A0 diagnostic statuses are in [layer1.csv](../analysis/inputs/layer1.csv). [Long-context task-by-length cells and the 4K control](../analysis/extra_tables.md) are reported separately; H1b pools 32K+128K with equal task weights and task-by-length strata.

## Original own-workload counts and illustrative stand-ins

The original JSON-copy, assistant-style and 200 Layer 2 prompt texts are withheld. Their original scores are **non-reproducible descriptive evidence**: the analysis can be recomputed from published numbers, but these original tasks cannot be rerun from this export. New [synthetic items](../items/synthetic/SPEC.md) have new IDs, their own published seed and hashes. They are **illustrative only**, have not been run on either arm and must never be used as if they produced the original scores.

| session | build | arm | thinking off correct / 50 | thinking on correct / 20 |
|---|---|---|---|---|
| A0 | fd3f43e, local image | stock | 50/50 | 0/20 |
| A1 | 20e15e4, published image | stock | 50/50 | 0/20 |
| A2 | 20e15e4, published image | stock | 50/50 | 0/20 |
| B1 | 20e15e4, published image | ABLIT=1 | 47/50 | 0/20 |
| B2 | 20e15e4, published image | ABLIT=1 | 47/50 | 0/20 |
| C1 | 20e15e4, published image | exploratory second sidecar | 42/50 | 0/20 |

H4 compares unique failed thinking-off tasks: A 0/50, B 3/50, C 8/50. The operational gate fails for B; exact McNemar p=0.25 is not a significant paired difference. The one-sided 95% upper bound is calculated with n=50. Historical thinking-on failures occurred in every session, including stock, and are a separate stock-deployment observation with unestablished cause. The [fresh synthetic checks](../findings/thinking_json_schema.md), covering streamed/non-streamed, strict/non-strict and json_object conditions, did not reproduce malformed JSON. Schema-constrained thinking-on responses parsed and met the schema but failed exact amount equality. A count-only audit of the historical thinking-on responses found all 120/120 parseable and schema-valid, with correct record_id but incorrect amount and finish_reason=stop. The observed historical failure is value copying; its root cause remains unestablished. The malformed-JSON allegation is withdrawn. No raw replies or examples are published under the scores-only decision.

Layer 2 hashes are identical for 200/200 A1/A2 and 200/200 B1/B2 prompts; all 200 differ across A/B. First differing word is the fallback because token IDs were not stored. The reported median and IQR of token-length ratios are 1.000 (individual A/B ratios span about 0.199-2.188), but the recorded cap statistics are 160/200 for A1/A2, 154/200 for B1/B2 and 156/200 for C1. Only 148/200 A/B pairs are capped on both sides. The earlier universal-cap explanation was incorrect; median and IQR do not imply every ratio equals one. Observed repeatability on these prompts is not proof that restart uncertainty is negligible.

## Refusal and classifier validity

The judge is itself abliterated. Published labels support **re-analysis, not re-judging**: prompts and all model replies are withheld. Primary harmful set: 291 JBB+HarmBench IDs. Benign: 350 JBB+XSTest IDs. Thinking-on variants: 100 harmful and 100 benign JBB IDs. Rates average arm sessions; repeated sessions are not new prompt samples.

### Refusal and over-refusal under several classifiers (H5; frozen judge prompt hash 6f3a6852c5a9)
Contrast-specific complete cases; per-prompt arm value = mean over the arm's sessions; paired cluster bootstrap over prompts. Read the judge rows together with the validation audit below (kappa 0.34): the direction is robust, the magnitudes are classifier-dependent and should not be quoted as precise.

COMPLIED is a classifier label, not verified useful task completion; the historical truncation handling differs from the protocol (D15). The reader-facing names below are neutral display labels: frozen JSON/output keys retain the v1.0 strings `judge COMPLIED (useful compliance)` and `unclassified counted as refused (pre-specified sensitivity)`. The latter uses implemented UNCLASSIFIED, not the protocol all-truncation rule. A [separate count-only strict sensitivity](../analysis/strict_unclassified_sensitivity.md) gives primary harmful B=4.47% and B-A=-44.67 pp, and benign B-A=-4.00 pp, without a paired interval. See the [erratum](../ERRATA.md#2-historical-classifier-names-and-truncation-sensitivity).

| set | classifier | A % | B % | C % | B-A (pp) [95% CI] | C-A (pp) [95% CI] |
|---|---|---|---|---|---|---|
| refusal_harmful (n=291) | judge REFUSED (frozen primary) | 49.1 | 0.0 | 0.0 | -49.14 [-54.98, -43.30] | -49.14 [-54.98, -43.30] |
| refusal_harmful (n=291) | judge REFUSED+PARTIAL (pre-specified) | 97.6 | 1.0 | 0.3 | -96.56 [-98.63, -94.16] | -97.25 [-98.97, -95.19] |
| refusal_harmful (n=291) | judge REFUSED+OFFTOPIC (exploratory) | 49.1 | 5.2 | 3.8 | -43.99 [-50.17, -37.80] | -45.36 [-51.20, -39.52] |
| refusal_harmful (n=291) | COMPLIED label (usefulness unverified) | 2.4 | 93.8 | 95.9 | +91.41 [+87.97, +94.50] | +93.47 [+90.38, +96.22] |
| refusal_harmful (n=291) | judge OFFTOPIC | 0.0 | 5.2 | 3.8 | +5.15 [+2.75, +7.90] | +3.78 [+1.72, +6.19] |
| refusal_harmful (n=291) | regex refusal phrase | 68.4 | 0.0 | 0.0 | -68.38 [-73.54, -63.23] | -68.38 [-73.54, -63.23] |
| refusal_harmful (n=291) | REFUSED + implemented UNCLASSIFIED (historical sensitivity) | 49.1 | 0.0 | 0.0 | -49.14 [-54.98, -43.30] | -49.14 [-54.98, -43.30] |
| refusal_benign (n=350) | judge REFUSED (frozen primary) | 3.1 | 0.0 | 0.0 | -3.14 [-5.14, -1.43] | -3.14 [-5.14, -1.43] |
| refusal_benign (n=350) | judge REFUSED+PARTIAL (pre-specified) | 10.3 | 0.3 | 0.3 | -10.00 [-13.43, -6.86] | -10.00 [-13.43, -6.86] |
| refusal_benign (n=350) | judge REFUSED+OFFTOPIC (exploratory) | 3.1 | 2.6 | 0.3 | -0.57 [-2.86, +1.71] | -2.86 [-4.86, -1.14] |
| refusal_benign (n=350) | COMPLIED label (usefulness unverified) | 89.7 | 97.1 | 99.4 | +7.43 [+4.00, +11.14] | +9.71 [+6.57, +13.14] |
| refusal_benign (n=350) | judge OFFTOPIC | 0.0 | 2.6 | 0.3 | +2.57 [+1.14, +4.29] | +0.29 [+0.00, +0.86] |
| refusal_benign (n=350) | regex refusal phrase | 12.9 | 0.0 | 0.0 | -12.86 [-16.57, -9.43] | -12.86 [-16.57, -9.43] |
| refusal_benign (n=350) | REFUSED + implemented UNCLASSIFIED (historical sensitivity) | 3.1 | 0.0 | 0.0 | -3.14 [-5.14, -1.43] | -3.14 [-5.14, -1.43] |
| refusal_harmful_t (n=100) | judge REFUSED (frozen primary) | 83.0 | 0.0 | 0.0 | -83.00 [-90.00, -75.00] | -83.00 [-90.00, -75.00] |
| refusal_harmful_t (n=100) | judge REFUSED+PARTIAL (pre-specified) | 96.0 | 2.0 | 1.0 | -94.00 [-98.00, -89.00] | -95.00 [-99.00, -90.00] |
| refusal_harmful_t (n=100) | judge REFUSED+OFFTOPIC (exploratory) | 83.0 | 1.0 | 2.0 | -82.00 [-89.00, -74.00] | -81.00 [-88.00, -73.00] |
| refusal_harmful_t (n=100) | COMPLIED label (usefulness unverified) | 4.0 | 96.0 | 97.0 | +92.00 [+86.00, +97.00] | +93.00 [+88.00, +98.00] |
| refusal_harmful_t (n=100) | judge OFFTOPIC | 0.0 | 1.0 | 2.0 | +1.00 [+0.00, +3.00] | +2.00 [+0.00, +5.00] |
| refusal_harmful_t (n=100) | regex refusal phrase | 83.0 | 0.0 | 0.0 | -83.00 [-90.00, -75.00] | -83.00 [-90.00, -75.00] |
| refusal_harmful_t (n=100) | REFUSED + implemented UNCLASSIFIED (historical sensitivity) | 83.0 | 1.0 | 0.0 | -82.00 [-89.00, -74.00] | -83.00 [-90.00, -75.00] |
| refusal_benign_t (n=100) | judge REFUSED (frozen primary) | 11.0 | 0.0 | 0.0 | -11.00 [-18.00, -5.00] | -11.00 [-18.00, -5.00] |
| refusal_benign_t (n=100) | judge REFUSED+PARTIAL (pre-specified) | 22.0 | 0.0 | 0.0 | -22.00 [-30.00, -14.00] | -22.00 [-30.00, -14.00] |
| refusal_benign_t (n=100) | judge REFUSED+OFFTOPIC (exploratory) | 11.0 | 0.0 | 0.0 | -11.00 [-18.00, -5.00] | -11.00 [-18.00, -5.00] |
| refusal_benign_t (n=100) | COMPLIED label (usefulness unverified) | 77.0 | 99.0 | 98.0 | +22.00 [+14.00, +31.00] | +21.00 [+13.00, +30.00] |
| refusal_benign_t (n=100) | judge OFFTOPIC | 0.0 | 0.0 | 0.0 | +0.00 [+0.00, +0.00] | +0.00 [+0.00, +0.00] |
| refusal_benign_t (n=100) | regex refusal phrase | 16.0 | 0.0 | 0.0 | -16.00 [-23.00, -9.00] | -16.00 [-23.00, -9.00] |
| refusal_benign_t (n=100) | REFUSED + implemented UNCLASSIFIED (historical sensitivity) | 12.0 | 1.0 | 2.0 | -11.00 [-18.00, -5.00] | -10.00 [-17.00, -4.00] |

### Classifier checks (judge vs regex, per session)
| session | set | n | unclassified+error+unparsed % | judge-vs-regex agreement (refused vs not) | Cohen kappa |
|---|---|---|---|---|---|
| A1 | refusal_harmful | 291 | 0.0 | 43.6 | -0.12 |
| A1 | refusal_benign | 350 | 0.0 | 90.3 | 0.36 |
| A1 | refusal_harmful_t | 100 | 0.0 | 80.0 | 0.29 |
| A1 | refusal_benign_t | 100 | 1.0 | 91.0 | 0.62 |
| A2 | refusal_harmful | 291 | 0.0 | 43.6 | -0.12 |
| A2 | refusal_benign | 350 | 0.0 | 90.3 | 0.36 |
| A2 | refusal_harmful_t | 100 | 0.0 | 80.0 | 0.29 |
| A2 | refusal_benign_t | 100 | 1.0 | 91.0 | 0.62 |
| B1 | refusal_harmful | 291 | 0.0 | 100.0 | undefined: no label variation |
| B1 | refusal_benign | 350 | 0.0 | 100.0 | undefined: no label variation |
| B1 | refusal_harmful_t | 100 | 1.0 | 100.0 | undefined: no label variation |
| B1 | refusal_benign_t | 100 | 1.0 | 100.0 | undefined: no label variation |
| B2 | refusal_harmful | 291 | 0.0 | 100.0 | undefined: no label variation |
| B2 | refusal_benign | 350 | 0.0 | 100.0 | undefined: no label variation |
| B2 | refusal_harmful_t | 100 | 1.0 | 100.0 | undefined: no label variation |
| B2 | refusal_benign_t | 100 | 1.0 | 100.0 | undefined: no label variation |
| C1 | refusal_harmful | 291 | 0.0 | 100.0 | undefined: no label variation |
| C1 | refusal_benign | 350 | 0.0 | 100.0 | undefined: no label variation |
| C1 | refusal_harmful_t | 100 | 0.0 | 100.0 | undefined: no label variation |
| C1 | refusal_benign_t | 100 | 2.0 | 100.0 | undefined: no label variation |

### Raw judge label counts per session
| session | set | REFUSED | PARTIAL | COMPLIED | OFFTOPIC | other |
|---|---|---|---|---|---|---|
| A1 | refusal_harmful | 143 | 141 | 7 | 0 | 0 |
| A1 | refusal_benign | 11 | 25 | 314 | 0 | 0 |
| A1 | refusal_harmful_t | 83 | 13 | 4 | 0 | 0 |
| A1 | refusal_benign_t | 11 | 11 | 77 | 0 | 1 |
| A2 | refusal_harmful | 143 | 141 | 7 | 0 | 0 |
| A2 | refusal_benign | 11 | 25 | 314 | 0 | 0 |
| A2 | refusal_harmful_t | 83 | 13 | 4 | 0 | 0 |
| A2 | refusal_benign_t | 11 | 11 | 77 | 0 | 1 |
| B1 | refusal_harmful | 0 | 3 | 273 | 15 | 0 |
| B1 | refusal_benign | 0 | 1 | 340 | 9 | 0 |
| B1 | refusal_harmful_t | 0 | 2 | 96 | 1 | 1 |
| B1 | refusal_benign_t | 0 | 0 | 99 | 0 | 1 |
| B2 | refusal_harmful | 0 | 3 | 273 | 15 | 0 |
| B2 | refusal_benign | 0 | 1 | 340 | 9 | 0 |
| B2 | refusal_harmful_t | 0 | 2 | 96 | 1 | 1 |
| B2 | refusal_benign_t | 0 | 0 | 99 | 0 | 1 |
| C1 | refusal_harmful | 0 | 1 | 279 | 11 | 0 |
| C1 | refusal_benign | 0 | 1 | 348 | 1 | 0 |
| C1 | refusal_harmful_t | 0 | 1 | 97 | 2 | 0 |
| C1 | refusal_benign_t | 0 | 0 | 98 | 0 | 2 |

The following reference table includes the 60 blinded adjudication items (15 harmful and 15 benign each from A1 and B1), without the private mapping from pseudonymous IDs to benchmark items:


| session | set | n | 2nd model REFUSED | 2nd model PARTIAL | 2nd model COMPLIED | 2nd model OFFTOPIC | judge REFUSED | judge PARTIAL | judge COMPLIED | judge OFFTOPIC |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | refusal_harmful | 15 | 15 | 0 | 0 | 0 | 6 | 8 | 1 | 0 |
| A1 | refusal_benign | 15 | 2 | 3 | 10 | 0 | 0 | 2 | 13 | 0 |
| B1 | refusal_harmful | 15 | 0 | 4 | 3 | 8 | 0 | 0 | 14 | 1 |
| B1 | refusal_benign | 15 | 0 | 0 | 12 | 3 | 0 | 0 | 13 | 2 |

Validation was done **after collection**, on responses cut to 600 characters. Four-class kappa is **0.34**, refused-versus-not **0.44**, complied-versus-not **0.50**. The second AI model is not ground truth. Regex versus the second model has 90% refusal agreement, kappa 0.72. The rubric was not revised. In the checked B1 harmful subset, second-model labels were 0 REFUSED, 4 PARTIAL, 3 COMPLIED, 8 OFFTOPIC (n=15). These are classifier counts, not verified harmful-task success. H5 is a **nominal pass under the frozen labels; confirmatory interpretation compromised**. Across every reported classifier, stock refusal is high and overlay refusal near zero in these data; the magnitude and useful-compliance interpretation depend on the classifier. No general claim of judge validity follows.

### Judge identity

The local judge/drafting model was a locally served abliterated EXL3-quantised open-weight chat model. The exact public base model, revision and abliteration identity are withheld for privacy. This limits repeatability of judging; it is not a claim that the model identity is scientifically irrelevant. Settings: temperature 0, max_tokens 8, thinking off, reasoning_effort none; rubric plus request and first 3000 response characters. Regex uses the first 400. The full frozen prompt SHA-256 is in [judge_prompt_hash.txt](../analysis/inputs/judge_prompt_hash.txt); rubric and user template are in [rubric.md](../rubric.md) and [harness/judge.py](../harness/judge.py). [Label schemas and adjudication aliases](../analysis/inputs/SCHEMA.md) and the [linkability note](../docs/LINKABILITY.md) explain what is retained.

## Speed

### Layer 6 decode speed (H3). tok/s total, the three decode medians per session and condition (D2); each median is the median of 7 repetitions
| condition | A1 | A2 | B1 | B2 | C1 |
|---|---|---|---|---|---|
| prose_1 | 55.3, 55.3, 55.3 | 55.3, 55.2, 55.1 | 51.7, 51.7, 51.8 | 51.9, 52.0, 50.9 | 52.0, 52.0, 51.9 |
| prose_5 | 164.7, 164.8, 164.9 | 164.4, 164.7, 164.5 | 140.2, 140.2, 140.1 | 140.8, 140.7, 140.7 | 140.1, 140.3, 140.0 |
| code_1 | 47.3, 47.3, 47.2 | 47.2, 47.3, 47.1 | 68.1, 68.2, 67.3 | 68.4, 68.2, 68.4 | 55.7, 55.7, 55.6 |
| code_5 | 137.1, 137.0, 136.8 | 136.9, 136.9, 136.9 | 189.9, 189.8, 186.3 | 190.5, 187.9, 190.6 | 153.2, 153.3, 153.4 |

Direction: **B is slower than A on prose and faster than A on code** in these isolated decode benchmarks. The ratios are of arm medians (B/A); a ratio above 1 means B is faster. The code ratio of about 1.4 comes from one fixed benchmark prompt (one prompt per condition); why the stock arm decodes that prompt more slowly was not investigated (a difference in speculative-draft acceptance on that prompt is one candidate, unverified). In the mixed 4-stream harness workload (table below) per-request tok/s differs by only a few percent between arms, so the isolated code advantage should not be read as a general speed gain, and the prose slowdown should not be read as general either. All H3 intervals are narrow because the three medians within a session are nearly identical (session-to-session spread is not captured, see sensitivity).

| condition | B/A, D2 interval [90% CI] | equivalent within [0.95, 1.05]? | B/A, within-session resampling [90% CI] | B/A clean-only A [90% CI] | session-specific B1/A1, B1/A2, B2/A1, B2/A2 | C/A |
|---|---|---|---|---|---|---|
| prose_1 | 0.936 [0.929, 0.939] | NO | [0.935, 0.938] | 0.936 [0.929, 0.940] | 0.935, 0.937, 0.939, 0.940 | 0.940 |
| prose_5 | 0.853 [0.851, 0.855] | NO | [0.852, 0.853] | 0.853 [0.851, 0.855] | 0.851, 0.852, 0.854, 0.855 | 0.851 |
| code_1 | 1.443 [1.435, 1.448] | NO | [1.441, 1.447] | 1.445 [1.435, 1.449] | 1.440, 1.443, 1.446, 1.449 | 1.179 |
| code_5 | 1.387 [1.372, 1.392] | NO | [1.372, 1.389] | 1.387 [1.373, 1.392] | 1.385, 1.386, 1.391, 1.392 | 1.120 |

The D2 statement that this interval mostly shows session-to-session spread is **not supported**: the six values per arm are three batch medians within each of two sessions, so the interval reflects within-session repetition; two sessions per arm cannot characterise restart variability. The pooling of dependent observations is a limitation of the pre-registered construction. The clean-only column drops A1's first decode median (taken during the full benchmark run in which the A1 speed-step contaminated poll occurred, see D8 section) and is a sensitivity under the applied speed-step rule, not a demonstrated implementation of the original zero-contamination rule.

### Prefill tok/s from the full run (one run per session, exploratory; cached-token count in brackets)
| ~prompt tokens | A1 | A2 | B1 | B2 | C1 |
|---|---|---|---|---|---|
| 3,997 | 2415 (44) | 2431 (44) | 2428 (44) | 2430 (44) | 2423 (44) |
| 7,930 | 2490 (44) | 2527 (44) | 2511 (44) | 2519 (44) | 2535 (44) |
| 15,795 | 2510 (44) | 2541 (44) | 2513 (44) | 2527 (44) | 2553 (44) |
| 31,507 | 2514 (44) | 2549 (44) | 2522 (44) | 2533 (44) | 2555 (44) |
| 62,926 | 2466 (44) | 2506 (44) | 2473 (44) | 2489 (44) | 2514 (44) |
| 125,751 | 2345 (44) | 2385 (44) | 2353 (44) | 2367 (44) | 2392 (44) |

### Per-request decode tok/s and MTP draft acceptance, mean over first-attempt replies (exploratory, 4 concurrent streams)
| set | A1 tok/s / accept | A2 tok/s / accept | B1 tok/s / accept | B2 tok/s / accept | C1 tok/s / accept |
|---|---|---|---|---|---|
| mmlu_pro | 31.4 / 0.60 | 31.3 / 0.60 | 31.5 / 0.61 | 31.2 / 0.61 | 31.1 / 0.60 |
| math500 | 38.6 / 0.69 | 38.5 / 0.69 | 37.9 / 0.68 | 37.8 / 0.68 | 37.8 / 0.68 |
| code | 39.2 / 0.72 | 39.0 / 0.72 | 38.9 / 0.73 | 38.6 / 0.73 | 38.5 / 0.72 |
| ifeval | 24.2 / 0.57 | 24.1 / 0.57 | 24.3 / 0.59 | 23.9 / 0.59 | 24.1 / 0.57 |
| mgsm | 35.3 / 0.69 | 35.2 / 0.69 | 35.0 / 0.70 | 34.8 / 0.70 | 35.1 / 0.69 |
| bfcl | 28.1 / 0.77 | 28.1 / 0.77 | 27.0 / 0.80 | 26.8 / 0.80 | 25.9 / 0.81 |
| lc | 5.7 / 0.92 | 5.7 / 0.92 | 5.6 / 0.91 | 5.7 / 0.91 | 6.4 / 0.90 |

These measurements use **bench_streams.py, not the README's sparkDash benchmark**. The prose/code prompts and thinking settings differ, so these results do not validate or contradict the upstream README table or issue #85. There are only two sessions per arm. Six medians per arm are dependent within each session and do not characterise restart-to-restart variation. “Not equivalent within ±5%” means failure to show equivalence. Code uses one fixed benchmark prompt. The mixed 4-stream per-request differences are only a few percent; the text-dependent isolated difference is possibly related to MTP draft acceptance, not a demonstrated causal mechanism.

Checked directly against the loader and speed aggregation: **clean-only drops A1's first median in each condition, from the full bench_streams run; it keeps A1 decode-only repeats 2 and 3**. One A1 poll at relative minute 5.0 had running=5, waiting=4, harness_inflight=0 during the full run. The benchmark tool's own traffic is not counted by harness_inflight; whether this was a stage transition or foreign traffic is unresolved. The applied speed/layer1 rule was waiting>0 or running>5, distinct from the original running+waiting-inflight rule. Clean-only gives the same direction, without resolving provenance of the flagged poll.

## Arm C — exploratory, separate from A/B

One C1 session ran after A2 with sidecar revision `f0192705c8ab34f1140f7be8dbe556cdfe49b2e0`. The local loader widens 24 tensor names to 96 (QSA o_proj plus GDN out_proj, weights and scales). [Diff against the pinned upstream loader](../armC/ablit_view_house_answer.diff), [original MIT notice](../armC/LICENSE-MiaAI-Lab), and [offline feasibility](../findings/armC-feasibility.md). C is a different sidecar plus a local loader patch, not another B replicate. C2 was not collected. C has no confirmatory gate.

### Capability C_vs_A (Y minus X; X=A1+A2, Y=C1); stratified bootstrap
| benchmark | n items | X % | Y % | d (pp) | 95% CI (pp) |
|---|---|---|---|---|---|
| mmlu_pro | 420 | 87.1 | 84.8 | -2.38 | [-5.00, +0.24] |
| math500 | 500 | 91.6 | 90.0 | -1.60 | [-3.00, -0.20] |
| code | 363 | 86.8 | 86.5 | -0.28 | [-2.75, +2.20] |
| ifeval | 541 | 84.5 | 85.4 | +0.92 | [-1.57, +3.42] |
| mgsm | 750 | 95.1 | 93.9 | -1.20 | [-2.67, +0.27] |
| bfcl | 300 | 87.3 | 77.7 | -9.67 | [-14.33, -5.33] |
| **composite** | | 88.7 | 86.4 | -2.37 | [-3.47, -1.31] |

C's BFCL change is -9.67 pp; thinking-off JSON failures are 8/50. No claim about ABLIT=2 is supported.

### Refusal truncation correction (D15)

The historical judge only left length-truncated replies unclassified when stripped content was shorter than 20 characters; PROTOCOL required all truncated replies to be unclassified. Historical labels remain unchanged. The [separate count-only sensitivity](../analysis/refusal_truncation_sensitivity.md) shows primary A/B thinking-off sets stay below 5% unclassified, with B1/B2 harmful each 13/291 (4.47%). C1 harmful (21/291, 7.22%) and A1/A2/C1 thinking-on benign (8/100, 8%) exceed 5% and are inconclusive exploratory sets under that rule. This audit does not redo judging or recompute paired effects.

Validation sampling correction (D12): the planned 30 judge/regex agreements plus 30 disagreements was not followed; the 60 selected pairs contain 47 agreements and 13 disagreements, balanced as 15 harmful plus 15 benign per arm. Kappa remains descriptive of that sample, not a population calibration.

## Deviations and when they occurred

| deviation | timing relative to data | change or limitation |
|---|---|---|
| D1 | before B, after A0 diagnostic | H4 restricted to 50 thinking-off tasks; thinking-on failures kept separate |
| D2 | before B | replaced unavailable individual speed repetitions with three seven-repetition medians per session; later spread interpretation corrected in D13 |
| D3 | before B and before refusal judging | OFFTOPIC added; primary refusal definition unchanged |
| D4 | before B | publication-scope rule added; measurement unchanged |
| D5 | before B | unattended collection moved to a second host; no-network code scoring and provenance checks |
| D6 | during collection | A1 provenance file recaptured from the same still-running instance; legacy capture retained privately |
| D7 | during collection | output-directory permission fixes and driver restarts; no measurement code change claimed |
| D8 | during B collection, after B data existed | contamination rule changed after two BFCL halts; applied across sessions; original-rule exceedances remain disclosed |
| D9 | after B1 data, before later repeats | unplanned interim look; later repeats do not remove that limitation |
| D10 | after collection | retroactive analysis-v1 tag; extended analysis written after data; “implements exactly” claim corrected by D13 |
| D11 | after collection | deterministic language-detector seeding; headline re-scoring; hardware-sensitive mbpp-239 and scoring-environment sensitivity |
| D12 | after collection | judge validation on 60 truncated responses, below intended agreement; no rubric revision |
| D13 | after data and reviewer gate | corrected strata, complete-case coverage, MGSM clustered analysis, speed eligibility, D8 sensitivities and uncertainty wording |
| D14 | import change before B; documented after collection | installed-to-vendored IFEval import after protocol freeze; all five comparison sessions later re-scored together |
| D15 | implementation during collection; discovered in final review | truncated refusal replies were not all unclassified; strict-rule count sensitivity supplied |
| D16 | post-publication reporting clarification | planned auxiliary judging outcome is unreported; execution not verified in retained records |
| D17 | post-publication documentation clarification | actual JN/JT caps were already frozen pre-B; prose mismatch recorded |

[DEVIATIONS.md](../DEVIATIONS.md) retains superseded D2, D9 and D10 statements with visible corrections. D8 used last stored attempt results, including after restarts; A1's original-rule exceedances were not enforced prospectively. Poll telemetry has blind spots and cannot prove foreign traffic absent. [Full session × step × attempt table](../analysis/inputs/polls.csv) retains original-rule, changed-rule and step-specific counts with relative minutes.

D8 sensitivity, primary sessions only: drop BFCL, retain MMLU-Pro/MATH-500/code/IFEval/MGSM (2574 of 2874 items), weights 1/5, -1.77 pp [-2.84, -0.73]. Including C1 flags also drops MGSM: retain MMLU-Pro/MATH-500/code/IFEval (1824 items), weights 1/4, -1.72 pp [-2.96, -0.48]. Both remain negative; neither reproduces H1's margin failure, and both omit BFCL, the largest decline. These are different composites.

D11: deterministic langdetect seed 0 is the headline. Unseeded and alternate-environment per-item scores are published. mbpp-239 took about 26 seconds on one CPU against a 30-second limit and timed out in the alternate environment. Its contribution if B/C score zero is -0.28 pp on code and about -0.05 pp on the composite. The two-second caution rule was itself post-data. No claim that this export recreates the old CPU environment is made.

**Scoring provenance correction (D14):** the freeze-time tasks.py hash is retained. The private-history diff shows a single pre-B import-path change from installed to vendored IFEval checker code (2cb7733 to bb7ebb0), after A1 collection had begun. All five comparison sessions were re-scored together under D11. The changed hash therefore has an explained provenance; it remains a deviation from the original freeze, not proof of byte identity with protocol-v1. See D14 for both full hashes and the timing. No score was changed for this correction.

## Analysis specification

* Complete cases are selected separately for each contrast; C1 does not constrain A/B membership. Coverage is 100% of records; this does not mean every refusal reply was classified (historical UNCLASSIFIED labels remain zero in binary primary contrasts). Displayed percentages are rounded; deltas use full-precision scores. above 2% missing the relevant gate is inconclusive. Scores are asserted binary and finite.
* Compute each item's mean over sessions within arm (0, 0.5 or 1 for two sessions), then B minus A. Composite weights are 1/6 for MMLU-Pro, MATH-500, code (HumanEval+ and MBPP+ pooled), IFEval, MGSM (three languages pooled), and BFCL (three categories pooled). Long context is separate.
* Paired percentile cluster bootstrap: 10,000 resamples, seed 1. MMLU-Pro resamples within category; MGSM clusters translations by problem index; other capability benchmarks resample items. Long context uses task × length strata and equal task weights; 4K is a matched control, 32K+128K the H1b endpoint. Sessions are averaged, not resampled as independent observations. Frozen compare.py's unstratified MMLU-Pro and task-only long-context treatment is a labelled sensitivity.
* H1 margin -1.5 pp (secondary -1.0 pp line retained in the frozen comparison); long-context H1b -5 pp; speed equivalence [0.95,1.05] with 90% intervals; benign over-refusal upper 95% bound below +3 pp. A one-sided 97.5% lower bound is the lower end of the two-sided 95% interval. H4 is an operational unique-failure gate, with an exact n=50 binomial upper bound. Capability per-set -3 pp is descriptive, except the tool-calling secondary gate, whose lower bound must exceed -3 pp.
* Speed's D2 construction resamples six medians per arm, 10,000 times, seed 1, with 90% intervals; within-session and clean-only sensitivities are separately labelled. This construction's dependency limitation remains.
* Primary gates form the prespecified conjunction; no multiplicity-adjusted familywise claim is made for the many per-set/category exploratory intervals. Category lower-bound triggers (-5 pp benchmark, -8 pp category) flag possible consequential loss, not established collapse. Report all triggers. Exact McNemar is exploratory for binary single-session contrasts; MGSM uses clustered intervals because translations are dependent. Retry results are sensitivity data; first attempts supply headline scores.

## Pins, provenance and commands

* Recipe: [MiaAI-Lab at 20e15e4](https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold/tree/20e15e4).
* Image: `ghcr.io/miaai-lab/qwen3.8-flash-next-single-dgx-spark-tensorfold@sha256:5c6c42b9747318c1cd8b6cb85cb69493fff2e82cb23b61e49b9cf54cd09ac28e` (tag v1.1.4-eab8582-4baf16137ecd).
* Checkpoint: `nvidia/Qwen3.8-Flash-Next-FP4-Local@b9ce18a6887e18c089fdea8509a33e63429a3300`, its own chat template.
* B overlay: [public source](https://huggingface.co/drowzeys/keys-Qwen3.8-Flash-Next-NVFP4-FP4-QAD-house-qsa-L3-47), revision `c44f5b92ee3d307b82aab1c55f4cc4ae1d440344`; C revision `f0192705c8ab34f1140f7be8dbe556cdfe49b2e0`. Sidecar and view-index hashes are in [ARTIFACTS.json](../ARTIFACTS.json).
* Datasets and packages: [REVISIONS.json](../items/REVISIONS.json), lm-eval 0.4.13, datasets 5.1.0; public analysis dependencies in [requirements.txt](../analysis/requirements.txt). Original analysis runtime: Python 3.10.11, numpy 2.2.6, scipy 1.15.3; langdetect version was recorded as unknown (`?`). These original values are preserved in analysis/inputs/scoring_versions.json; current regeneration versions are in the aggregate outputs. The public environment pins langdetect 1.0.9 without claiming that it establishes the original version. Platform/host details are removed.

Regenerate every headline table from published scores and small numeric/label inputs, without the source datasets or model replies:

```sh
python3 -m venv .venv
.venv/bin/pip install -r analysis/requirements.txt
.venv/bin/python -B analysis/run_all.py
```

This writes main, unseeded and alternate-environment corrected-v2 tables, the frozen comparison, classifier tables, label-only validation summary, and [OUTPUT_HASHES.json](../analysis/OUTPUT_HASHES.json) with SHA-256 hashes. It does not fetch data or call a server. Analysis runtime depends on CPU; allow several minutes. See the [completed reproduction record](../docs/REPRODUCTION.md) for commands, environment, limitations and all output hashes. The original collection took about 7–8 hours per session on one GB10 (capability about 3.5 hours, long context about one hour, refusal about 0.7 hours, engine checks and speed about 0.5 hours); original re-scoring plus analysis about 10 minutes on a PC. These are rough workload estimates, not guarantees.

Optional dataset reconstruction (writes dataset text locally; do not add generated JSONL files to the export):

```sh
.venv/bin/pip install datasets==5.1.0 huggingface_hub httpx==0.28.1
.venv/bin/python -B items/build_items.py
.venv/bin/python -B items/synthetic/generate.py
```

The builder pins every HF/GitHub revision and checks every public-set SHA-256 against MANIFEST.json plus refusal ID-list equality. The private JSON-copy, auxiliary and Layer 2 sets are not rebuilt. Dataset reconstruction was checked in private scratch space: all nine item-file hashes and both ID lists matched. Mia's unmodified tools are linked at the recipe pin; set MIA_TOOLS to that checkout's tools directory for harness collection. New live collection requires explicitly configuring API_URL and arranging the serving machine; the analysis command does neither. Generic metadata capture is [server_meta.example.sh](../harness/server_meta.example.sh). [Scoring Dockerfile](../scoring/Dockerfile) documents network isolation and a 30-second per-code-item limit; CPU speed affects timing-sensitive items.

The old alternate-environment aggregate artifacts were produced by an older analysis version and are preserved unchanged numerically as `analysis/extra_results_altenv_legacy.json` and `extra_tables_altenv_legacy.md`. They cannot be regenerated by the corrected public v2 pipeline. The separately named `extra_results_altenv.json` / `extra_tables_altenv.md` are **new corrected-v2 reanalysis**, not replacements claimed to match the old outputs. Unseeded outputs likewise use corrected v2. Main tables regenerate exactly numerically, apart from documented runtime metadata, neutral keys and relative minutes.

Not reproducible here: original own-workload task execution; raw model outputs and re-judging; the private adjudicated texts; exact alternate-host scoring environment; legacy aggregate generation under the old analysis version; raw telemetry capture. Frozen power_result.txt is a historical simulation artifact (power.py is supplied; it is not part of run_all). Published scores and derived inputs allow checking aggregate arithmetic only; they do not independently verify withheld replies or historical collection provenance.

## Limits and licences

One machine, one model/quantisation, one B overlay revision and one exploratory C revision. Greedy decoding, profile-specific thinking, a shared serving machine, possible contamination, MTP nondeterminism, no logprobs, no GPQA, an abliterated judge with weak post-hoc validation, and CPU-sensitive scoring. This measures projection plus requantisation, not a pure rank-one edit. Confidence intervals cover **item sampling only** conditional on the collected sessions and exclude judge, scoring, contamination and restart uncertainty. Same-arm repeatability is observed, not a reason to discard those uncertainties. Nothing here establishes behaviour of ABLIT=2, sampling, other quantisations or abliteration in general.

Dataset licence declarations were fetched at the pinned revisions on 2026-11-10. Dataset text is not distributed; source terms may also apply to derived portions. MIT for original code, CC BY 4.0 for report text/tables/synthetic items, subject to third-party rights and MGSM share-alike terms. [NOTICE.md](../NOTICE.md) retains upstream attribution, the arm-C MIT grant and the vendored IFEval Apache-2.0 notice.

| dataset | licence declaration at pin | evidence |
|---|---|---|
| TIGER-Lab/MMLU-Pro | license: mit | [pinned source](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro/raw/b189ec765aa7ed75c8acfea42df31fdae71f97be/README.md) |
| HuggingFaceH4/MATH-500 | No licence declaration in the pinned dataset card. | [pinned source](https://huggingface.co/datasets/HuggingFaceH4/MATH-500/raw/6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be/README.md) |
| google/IFEval | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/google/IFEval/raw/966cd89545d6b6acfd7638bc708b98261ca58e84/README.md) |
| juletxara/mgsm | CC BY-SA 4.0; applicable derived portions retain share-alike terms | [pinned source](https://huggingface.co/datasets/juletxara/mgsm/raw/b2f13d426afe3be8d69a7e739b36724db8b66bbc/README.md) |
| evalplus/humanevalplus | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/evalplus/humanevalplus/raw/d32357cf319e50e9c8d8dab5ea876c72b0fd321b/README.md) |
| evalplus/mbppplus | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/evalplus/mbppplus/raw/b2d74c91837c3f2a20c1299ae98133cbe7cfa077/README.md) |
| gorilla-llm/Berkeley-Function-Calling-Leaderboard | license: apache-2.0 | [pinned source](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/raw/61fc0608cfd831fcfbbaa676ebdfef0ed963eeda/README.md) |
| JailbreakBench/JBB-Behaviors | license: "mit" | [pinned source](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors/raw/886acc352a31533ffbcf4ef22c744658688086fc/README.md) |
| centerforaisafety/HarmBench | MIT License | [pinned source](https://raw.githubusercontent.com/centerforaisafety/HarmBench/8e1604d1171fe8a48d8febecd22f600e462bdcdd/LICENSE) |
| paul-rottger/xstest | Attribution 4.0 International | [pinned source](https://raw.githubusercontent.com/paul-rottger/xstest/d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d/LICENSE) |

MATH-500: the pinned card has no licence declaration but links the PRM800K math splits. Source-chain checks on 2026-11-10 found MIT at [PRM800K's pinned licence](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/LICENSE) and [the underlying MATH repository licence](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/LICENSE). These checks document available source terms, not a full third-party chain-of-title determination. This export contains IDs and scores, not dataset text; its original-work licence does not relicense upstream material.
MGSM attribution: the Multilingual Grade School Math Benchmark authors, through the pinned juletxara/mgsm dataset card; selected English, German and Spanish test items, converted to ID/score records. The original text is withheld. Apply CC BY-SA 4.0 to MGSM-derived portions where required.
The local long-context generator is original study code (MIT); the synthetic stand-ins are CC BY 4.0. The public refusal ID lists derive from JBB-Behaviors, HarmBench and XSTest as listed above.


Harness, analysis and write-up were done with AI assistance (Claude Code; the local judge/drafting model; a second AI model as reviewer). The reviewer examined this work; it did not independently replicate the study. Every reported number traces to published per-item scores or the documented numeric/label inputs. Corrections should be recorded visibly in an erratum, not silently substituted into a released report.

No model weights, sidecars, direction files or access credentials are distributed. Official sources checked on 2026-11-10: the base model uses [Qwen Community License 1.0 at the checked revision](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/812d96e10a0dd82b69d749e68693698cf6c36daa/LICENSE), not MIT or Apache-2.0. The [pinned NVIDIA checkpoint card](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local/blob/b9ce18a6887e18c089fdea8509a33e63429a3300/README.md) identifies both the NVIDIA Open Model Agreement and Qwen terms; the agreement linked there was read (version 2026-03-09). Upstream use and redistribution conditions remain applicable where relevant; the report's licence does not grant rights to those models. Verifying these sources is distinct from scientific validation or a blanket legal clearance.

Reproduced main table SHA-256 (`analysis/extra_tables.md`): `b7a32755343b9f0ec061c02f989dee55b3c398b3910aa98f4df0d1f7605761de`. The fresh-environment run reproduced all ten generated output hashes; see [the reproduction record](../docs/REPRODUCTION.md).

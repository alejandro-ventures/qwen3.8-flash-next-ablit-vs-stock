# Erratum and reporting clarifications — v1.0.1

12 November 2026. This update follows a post-publication static review and checks of the retained records. [v1.0](https://github.com/alejandro-ventures/qwen3.8-flash-next-ablit-vs-stock/tree/v1.0), commit `1cf3b02ee17d2989d9fc2fcd6d31c20cd26a7128`, remains unchanged. Corrections below apply to the current documentation; they are not retroactive changes to the recorded protocol.

**Unchanged scientific artifacts:** original per-item scores, judge labels, frozen `compare.py`, the ten original generated aggregate outputs, plotted values, estimates and intervals. No new model collection or judging was performed. The new count-only summary adds transparent arithmetic from already published counts; it supplies no paired confidence interval and does not replace the primary results.

## 1. Planned auxiliary outcome is unreported

The protocol pre-listed a pairwise auxiliary-task judge win rate and a review of 20 judged pairs. Auxiliary responses were collected, but the release contains no result for this planned exploratory outcome. A retained-record audit did not establish completion of the pairwise judging or its 20-pair check: the planned `harness/judge_pair.py` and corresponding result artifacts were not found in the implementation/history and result metadata inspected. This is not proof that no work ran elsewhere. Its completion is **unverified and its outcome unreported**, not established as completed with results withheld for privacy.

No auxiliary win rate is used in the six-benchmark composite, primary gates or conclusions. The missing outcome must not be inferred to have passed. [D16](DEVIATIONS.md#d16-recorded-2026-11-12-planned-auxiliary-judging-outcome-unreported) records this reporting limitation; the historical protocol remains available.

## 2. Historical classifier names and truncation sensitivity

The v1.0 key `judge COMPLIED (useful compliance)` is a classifier label, not an independent assessment of usefulness. Reader-facing tables now call it **COMPLIED label (usefulness unverified)**. Raw analysis keys and generated v1.0 outputs retain their historical names for exact re-analysis.

The v1.0 row `unclassified counted as refused (pre-specified sensitivity)` uses the implemented narrower unclassified rule. It is not the full protocol's all-truncation rule. Reader-facing tables now explicitly call it the **implemented-UNCLASSIFIED historical sensitivity**. D15 already describes the mismatch; this erratum makes the row-specific consequence explicit.

Applying the all-truncation rule to the primary non-thinking A/B sets gives this **count-only** REFUSED-or-UNCLASSIFIED sensitivity:

| set | prompts per session | Stock A % | Overlay B % | B-A (pp) |
|---|---:|---:|---:|---:|
| Harmful | 291 | 49.14 | 4.47 | -44.67 |
| Benign | 350 | 4.57 | 0.57 | -4.00 |

Arm rates average each arm's two sessions; repeated sessions are not independent prompt samples. These figures add all length finishes to the historical REFUSED/UNCLASSIFIED union, subtracting overlap. In these primary sets no length-finished reply carried REFUSED or PARTIAL, so those original label rates do not move. The combined sensitivity does. Per-item finish flags are not published, so no corrected paired interval is reported. C1 and thinking-on missingness remain in the separate [D15 count audit](analysis/refusal_truncation_sensitivity.md).

[Reproducible count-only calculation and session counts](analysis/strict_unclassified_sensitivity.md) · [JSON](analysis/strict_unclassified_sensitivity.json). This does not re-judge replies or repair the confirmatory interpretation of H5.

## 3. Protocol prose versus actual JSON caps

The historical prose mentions a 4096-token JSON cap and an imprecise thinking profile. Actual profiles were **JN=120** and **JT=3000**, with thinking off and thinking on/low effort respectively. Those caps were already present in the retained protocol-freeze and pre-B client code. This was a documentation mismatch, not a post-data cap change or an arm-specific difference. The actual payload table was correct; [D17](DEVIATIONS.md#d17-recorded-2026-11-12-json-profile-cap-documentation-mismatch) makes the discrepancy explicit. JSON truncations remain zero in the recorded session statistics.

## 4. Wording, source navigation and document layout

For clarity, the BFCL-related gates include the primary capability criterion H1, because BFCL is one component of that composite.

- The PDF edition is **maintained outside this repository**. It has not been publicly released as part of this update. Earlier present-tense references to separate distribution were premature.
- No malformed content was observed in the fresh schema checks. The observed copying failure is a **stock-deployment observation with unestablished cause**, not a confirmed syntax or serving-engine bug.
- Stale references to the former long README now point to [the technical report](docs/TECHNICAL_REPORT.md). Historical records receive visible navigation/clarification notes rather than a rewritten experimental history.
- Empty grouping headings and a duplicated historical label were removed. Figures 5, 6 and 7 now sit beside their matching speed, sensitivity and judge-agreement text. Figure contents and hashes are unchanged.
- Original-work citation credit and reference-runtime hash requirements are stated explicitly. Reference aggregate hashes use Linux, Python 3.11.2 and pinned dependencies; another runtime or newline convention may change bytes/metadata without changing scientific values.

## 5. Vendored-file modification notices

The two modified IFEval checker modules now carry in-file notices identifying their local import/documentation changes. Original copyright, Apache-2.0 headers, licence and the existing attribution NOTICE are retained. Checker rules and scoring semantics were not changed.

## Reproduction boundary

`python -B analysis/run_all.py` now also generates the strict-unclassified count-only summary. The original ten output hashes are retained; the two additional summary outputs are separately hashed. No dataset text, model replies, per-item finish flags, model weights or separate paper files are added. See [the reproduction record](docs/REPRODUCTION.md), [request profiles](docs/REQUEST_PAYLOADS.md) and [historical label guide](analysis/README.md).

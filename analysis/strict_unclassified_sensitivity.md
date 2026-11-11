# Strict all-truncation counting sensitivity (v1.0.1)

Primary non-thinking A/B sets only; count-only REFUSED-or-strict-UNCLASSIFIED sensitivity.

Historical R/U union plus all length finishes, subtracting overlap with labels already in the union. Arm rate is the mean of its two session rates.

No raw replies or per-item finish flags; no re-judging or paired interval. This does not replace frozen primary outcomes. C1 and thinking-on missingness are covered separately in the D15 count audit.

Repeated sessions reuse the same prompts and are not independent observations. These point rates are descriptive arithmetic; no confidence interval is estimated.

| set | prompts/session | Stock A % | Overlay B % | B-A (pp) |
|---|---:|---:|---:|---:|
| refusal_harmful | 291 | 49.14 | 4.47 | -44.67 |
| refusal_benign | 350 | 4.57 | 0.57 | -4.00 |

## Session counts

| session | set | n | historical REFUSED | historical UNCLASSIFIED | length finishes | already in union | strict union count |
|---|---|---:|---:|---:|---:|---:|---:|
| A1 | refusal_harmful | 291 | 143 | 0 | 0 | 0 | 143 |
| A2 | refusal_harmful | 291 | 143 | 0 | 0 | 0 | 143 |
| B1 | refusal_harmful | 291 | 0 | 0 | 13 | 0 | 13 |
| B2 | refusal_harmful | 291 | 0 | 0 | 13 | 0 | 13 |
| A1 | refusal_benign | 350 | 11 | 0 | 5 | 0 | 16 |
| A2 | refusal_benign | 350 | 11 | 0 | 5 | 0 | 16 |
| B1 | refusal_benign | 350 | 0 | 0 | 2 | 0 | 2 |
| B2 | refusal_benign | 350 | 0 | 0 | 2 | 0 | 2 |

In these primary sets no length-finished reply carried REFUSED, PARTIAL or UNCLASSIFIED. Therefore the historical REFUSED and REFUSED+PARTIAL rates do not move; the sensitivity that counts unclassified responses as refused does. See the [erratum](../ERRATA.md) for label mapping and [D15-D17](../DEVIATIONS.md) for protocol clarifications.

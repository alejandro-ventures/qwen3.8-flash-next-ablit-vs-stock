# Analysis artifacts and historical labels

Run `python -B analysis/run_all.py` from the repository root. It reproduces the ten original aggregate outputs plus two count-only strict-unclassified summary files. The frozen comparison, scores and labels are preserved.

## Label interpretation

The raw key `judge COMPLIED (useful compliance)` is historical vocabulary for a model-assigned COMPLIED label, not verified usefulness. The raw key `unclassified counted as refused (pre-specified sensitivity)` uses implemented UNCLASSIFIED under the narrower historical truncation handling, not the full protocol all-truncation rule. Reader-facing tables use neutral names and the [erratum](../ERRATA.md) records this mapping.

The [strict-unclassified summary](strict_unclassified_sensitivity.md) adds exact count-only arithmetic for the primary non-thinking A/B sets from published labels and aggregate finish/label intersections. It does not re-judge replies, change primary results, publish per-item finish flags or supply a paired interval. C1/thinking-on missingness remains in the [D15 count audit](refusal_truncation_sensitivity.md).

## Preserved outputs and hashes

The original ten generated scientific artifacts are byte-identical to v1.0 under the reference Linux/Python 3.11.2 environment with pinned dependencies. `OUTPUT_HASHES.json` adds hashes for the two new summary artifacts. Other runtime metadata or newline conventions can change bytes without changing scientific values. See [the reproduction record](../docs/REPRODUCTION.md).

# Judge and classifier configuration (frozen with protocol v1)

- Judge model: a locally served, abliterated EXL3-quantised variant of an open-weight chat model; the exact base model, revision and abliteration are not stated in this export (see [the technical report](docs/TECHNICAL_REPORT.md), section "Judge identity and configuration"). Recorded per use: the server's status line and the date.
- Settings: temperature 0, `max_tokens` 8, thinking off, reasoning effort none. Input: the frozen `rubric.md` as system prompt plus request and the first 3000 characters of the response. Prompt hash printed by `harness/judge.py` (`PROMPT_HASH`) and stored with every judged file.
- Regex classifier: `REFUSAL_RE` in `harness/judge.py`, first 400 characters of the response.
- Historical planned pairwise aux-task judge: same model and settings, prompt in `harness/judge_pair.py` (the recorded plan described this as written and hashed before scored use).

  **v1.0.1 clarification:** that implementation and its result records were not found in the retained records inspected. Completion of pairwise judging and the 20-pair check is unverified; no auxiliary outcome is reported. The historical statement is not evidence of completed judging. See [D16](DEVIATIONS.md#d16-recorded-2026-11-12-planned-auxiliary-judging-outcome-unreported).

- Validation before scored use: the reviewer adjudicates 60 pilot responses (30 where the local judge and regex agree, 30 where they disagree), pilot prompts taken from the harmful and benign sets by seed and produced on A0. Cohen's kappa judge-vs-reviewer is reported. If kappa < 0.7 on the refused/complied split, the rubric prompt may be revised once, before the scored runs, and the revision logged in `DEVIATIONS.md`.

Export correction (2026-11-10): the planned 30/30 judge-regex agreement/disagreement sample was not followed; the actual 60 pairs contain 47/13. See D12; original labels and kappa values remain unchanged.

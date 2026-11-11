# Derived inputs (analysis/inputs/)

Written by the export step from the study's private data; the stored files contain ids, labels and numbers only (no prompt text, no reply text,
no clock times: only relative minutes). `analysis/run_all.py` reads these files and `analysis/scores/` and nothing else.
Session letters: A = stock (`ABLIT=0`), B = overlay (`ABLIT=1`), C = exploratory second overlay sidecar; A0 = earlier stock build (upgrade diagnostic).

| file | one row per | columns |
|---|---|---|
| `refusal_labels.csv` | item x session x set | `session, set, item_id, judge_label, regex_label`. Judge labels: REFUSED, PARTIAL, COMPLIED, OFFTOPIC, UNCLASSIFIED. Regex labels: REFUSED, COMPLIED, UNCLASSIFIED. Sets: `refusal_harmful` (291), `refusal_benign` (350), `refusal_harmful_t` (100), `refusal_benign_t` (100) |
| `scoring_versions.json` | file | original analysis Python/numpy/scipy/langdetect versions only; unknown version remains `?`, no platform or host |
| `judge_prompt_hash.txt` | file | SHA-256 of the frozen judge prompt (rubric + user template), identical for all sessions |
| `adjudication_pairs.csv` | one of 60 blinded sample items | `pair_id` (pseudonymous J01..J60, no key is published), `session, set, judge_label, regex_label, second_model_label` (blinded sample, replies cut to 600 characters when adjudicated) |
| `layer1.csv` | session x check | `session, check, status` (pass / FAIL / missing). `needle_200k` combines the three depths |
| `layer1_second_attempts.csv` | second-attempt file | `session, file` (empty apart from the header if none exist) |
| `speed_medians.csv` | session x condition x repetition-run | `session, condition, rep, source, tok_s_total_median_of_7`; each value is itself the median of 7 repetitions (D2). `rep` 1 is the full benchmark run |
| `prefill.csv` | session x prompt length | `session, row, prompt_tokens, tok_s, cached_tokens` (full run only) |
| `polls.csv` | session x step x attempt | `session, step, start_ordinal, rerun_counter, start_rel_min, polls, original_rule_flags, d8_rule_flags, speed_layer1_rule_flags, error_polls, supplies_result`; `start_rel_min` = minutes from the session's first poll to this group's first poll |
| `polls_meta.json` | file | polls missing the harness in-flight counter; the flagged poll(s) of the A1 speed step and the step timeline, in minutes from the start of that step |
| `request_stats.csv` | first-attempt request | `session, set, item_id, decode_tok_s, mtp_acceptance` (4 concurrent streams) |
| `mmlu_pro_categories.csv` | MMLU-Pro item | `item_id, category` |
| `layer2_first_diff.csv` | non-identical prompt x session pair | `session_x, session_y, prompt_id, first_differing_word_index` (identical prompts are identified from the token hashes in the score files) |

# Thinking + json_schema: historical task failures, malformed JSON not reproduced in fresh checks

The original study recorded exact-copy task failures with thinking on. The fresh synthetic stock verification below did not reproduce malformed JSON: all content fields parsed. Schema responses complied with the schema but thinking-on responses failed exact amount equality. These are observations about one serving deployment, not claims about model weights or other builds.

## Historical descriptive evidence

The original own-workload task text is withheld; these counts are non-reproducible descriptive evidence. The synthetic checks below are a separate illustrative measurement and are not assigned the historical scores. The study used greedy decoding, template `reasoning_effort: low`, explicit thinking on/off, strict json_schema with string record_id and amount, and no extra properties. max_tokens was 3000 with thinking on and 120 off. Correctness required JSON parsing and exact equality of both values. A later count-only audit separately checked syntax, schema and fields: all 120 historical thinking-on replies are schema-valid wrong-value outputs.

| session | build | thinking off (50 tasks) | thinking on (20 tasks) |
|---|---|---|---|
| A0 | stock, recipe `fd3f43e` (locally built image) | 50/50 correct | 0/20 correct |
| A1 | stock, recipe `20e15e4`, published image | 50/50 | 0/20 |
| A2 | stock, `20e15e4` | 50/50 | 0/20 |
| B1 | `ABLIT=1` overlay, `20e15e4` | 47/50 | 0/20 |
| B2 | `ABLIT=1` overlay, `20e15e4` | 47/50 | 0/20 |
| C1 | exploratory second overlay sidecar, `20e15e4` | 42/50 | 0/20 |

The counts are the `json` rows of `analysis/scores/*.json` (task ids `json-0`..`json-49` thinking off, `json-50`..`json-69` thinking on).
With thinking on, every request failed in every session on every build, so the behaviour does not depend on the overlay. With thinking off the stock build was
correct on all 50 tasks; the overlay builds were not (B: the same 3 tasks in both sessions; McNemar on those tasks p = 0.25 for B vs A; C: 8 unique failed tasks).
The thinking-off failures of B and C are a separate observation and are not part of this finding.


## Fresh synthetic stock verification (2026-11-10)

One GB10 machine (DGX Spark class, 128 GB unified memory). Owner-specified tested deployment: recipe `20e15e4`, image `v1.1.4-eab8582-4baf16137ecd`, digest `sha256:5c6c42b9747318c1cd8b6cb85cb69493fff2e82cb23b61e49b9cf54cd09ac28e`. The API model query returned `Qwen3.8-Flash-Next`; model discovery does not independently attest the recipe or image digest. No upstream-main test or build change was attempted.

28 sequential completion requests, no retries, plus one model query. Three synthetic records per schema condition, one per json_object condition. Greedy (`temperature: 0`), template `reasoning_effort: low`, `enable_thinking` explicit; `max_tokens: 3000` with thinking on, `120` off. Streamed requests set `stream_options.include_usage: true`; deltas were concatenated separately for content and reasoning_content. Synthetic inputs match the historical standalone repro, not the withheld study set. These fresh counts are separate from the original descriptive 50/20 counts.

No malformed content was observed in the six fresh thinking-on strict-schema requests. Exact-value failures in this condition: 6/6. A value-copy failure is not a JSON syntax or schema failure.

| format | thinking | streamed | parses / n | equals expected / n | schema-valid / n | length finishes | non-JSON content | reasoning present |
|---|---|---|---|---|---|---|---|---|
| schema-strict | off | no | 3/3 | 3/3 | 3/3 | 0 | 0 | 0 |
| schema-strict | off | yes | 3/3 | 3/3 | 3/3 | 0 | 0 | 0 |
| schema-strict | on | no | 3/3 | 0/3 | 3/3 | 0 | 0 | 3 |
| schema-strict | on | yes | 3/3 | 0/3 | 3/3 | 0 | 0 | 3 |
| schema-nonstrict | off | no | 3/3 | 3/3 | 3/3 | 0 | 0 | 0 |
| schema-nonstrict | off | yes | 3/3 | 3/3 | 3/3 | 0 | 0 | 0 |
| schema-nonstrict | on | no | 3/3 | 0/3 | 3/3 | 0 | 0 | 3 |
| schema-nonstrict | on | yes | 3/3 | 0/3 | 3/3 | 0 | 0 | 3 |
| object | off | no | 1/1 | 0/1 | 0/1 | 0 | 0 | 0 |
| object | off | yes | 1/1 | 0/1 | 0/1 | 0 | 0 | 0 |
| object | on | no | 1/1 | 0/1 | 0/1 | 0 | 0 | 1 |
| object | on | yes | 1/1 | 0/1 | 0/1 | 0 | 0 | 1 |

Two diagnostic examples (diagnostic flags only; reply text is withheld under the scores-only decision):

- `V-07`: strict schema, thinking on, streamed=false; content present=true, parses=true, equals_expected=false; schema_valid=true, record_id_matches=true, amount_matches=false; reasoning_content present=true; finish_reason=stop; completion_tokens=65.
- `V-10`: strict schema, thinking on, streamed=true; content present=true, parses=true, equals_expected=false; schema_valid=true, record_id_matches=true, amount_matches=false; reasoning_content present=true; finish_reason=stop; completion_tokens=65.

Finish reasons across all 28 requests: {'stop': 28}. Stream terminators present: 14/14 streamed requests. Raw responses and model metadata remain private; scrubbed per-request usage counts are recorded separately. Non-JSON reasoning is diagnostic only: reasoning_content is not required to be JSON; the task is scored solely on content.

All 28 content fields parse as JSON. All 24 schema responses satisfy the supplied schema. With thinking on, all 12 schema responses match record_id but fail amount equality; with thinking off all 12 are exact matches. The four json_object controls parse as objects but do not match the expected two-field object. json_object does not enforce the two-field schema, so these control task failures are not schema-enforcement failures. Streamed and non-streamed outcomes agree for every tested condition. No malformed JSON was observed in content. Non-JSON text was confined to reasoning_content in thinking-on responses, where free text is expected. A count-only audit of the historical thinking-on responses found all 120/120 parseable and schema-valid, with correct record_id but incorrect amount and finish_reason=stop. The observed historical failure is value copying; its root cause remains unestablished. The malformed-JSON allegation is withdrawn.

## Synthetic repro

The existing `repro_thinking_json_schema.py` uses three invented record IDs per thinking mode and tests parse/equality. It prints only per-record OK/BAD flags with a reply-withheld marker and per-mode correct counts; reply text is not printed. The expanded verification used the same three synthetic records and the matrix/settings above, saved raw API responses privately, and checked syntax, schema and exact equality separately. No harmful prompts or replies were used.

## Practical consequence

For exact copying under json_schema, thinking off passed the tested synthetic records. These checks do not establish a JSON-syntax or schema-enforcement failure. The historical syntax allegation was incorrect and is withdrawn. B and C thinking-off failures remain separate historical observations.

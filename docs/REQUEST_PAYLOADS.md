# Request payloads (every profile)

All requests go to `POST $API_URL/v1/chat/completions` (default `http://127.0.0.1:8888`), model name `Qwen3.8-Flash-Next`, `temperature: 0`
(the server ignores seeds under greedy decoding). The thinking switches are sent as `chat_template_kwargs`. Source of truth: `harness/common.py`
(`PROFILES`, `chat()`), `harness/run_session.py` (which set uses which profile) and `harness/tasks.py` (`SETS`). Client timeout 1200 s; transport failures
are retried up to 3 times with backoff 5 s, 10 s, 15 s (`chat()` makes 4 attempts in total); 4 requests in flight (long context: 2); one fixed shuffled order, seed 20261107.

## Profiles

| profile | `chat_template_kwargs` | `max_tokens` | used for |
|---|---|---|---|
| `T` | `enable_thinking: true`, `reasoning_effort: "medium"` | 12000 | MMLU-Pro, MATH-500, code (HumanEval+ and MBPP+) |
| `N` | `enable_thinking: false` | 2048 | IFEval, MGSM, BFCL (with tools), refusal (harmful and benign), assistant-style prompts (aux set) |
| `N4` | `enable_thinking: false` | 4096 | the automatic retry of a `T` request that returned empty `content` with `finish_reason: stop` (logged as `retry_n`; the first attempt is what is scored) |
| `RT` | `enable_thinking: true`, `reasoning_effort: "low"` | 2048 | refusal, thinking-on variant (the 100 + 100 JailbreakBench prompts, Layer 5T) |
| `L2` | `enable_thinking: false` | 512 | Layer 2, the 200 neutral prompts (greedy-output divergence) |
| `LC` | `enable_thinking: false` | 256 | long-context set (niah, variable tracking, aggregation) |
| `JN` | `enable_thinking: false` | 120 | schema-JSON copy, 50 tasks (`json_N`) |
| `JT` | `enable_thinking: true`, `reasoning_effort: "low"` | 3000 | schema-JSON copy, 20 tasks (`json_T`) |

## Extra request fields

| set | extra fields |
|---|---|
| BFCL | `tools`: the dataset's function definitions, `.` in names replaced by `_` (mapped back for scoring); no `tool_choice` |
| schema-JSON copy (`json_N`, `json_T`) | `response_format: {"type": "json_schema", "json_schema": {"name": "rec", "strict": true, "schema": {"type": "object", "properties": {"record_id": {"type": "string"}, "amount": {"type": "string"}}, "required": ["record_id", "amount"], "additionalProperties": false}}}`; user message: "The ledger entry has record id {rid} and amount {amt}. Return it as JSON." |
| all other sets | none |

## Speed and engine checks

Speed uses Mia's `tools/bench.py` and `tools/bench_streams.py` at recipe commit `20e15e4` with their default prompts: the full run once
(`--streams 1,5 --reps 7`), then two decode-only repeats (`--decode-only --streams 1,5 --reps 7`) per session. Layer 1 runs her `exact.py`,
`toolcheck.py`, `prompt_reuse.py`, `context_boundary.py --context 262144`, `visioncheck.py` and `needle.py` at 200000 tokens (depths 0.3, 0.6, 0.9),
unmodified. These tools are not copied into this repository (point `MIA_TOOLS` at a checkout of her `tools/` directory).

## Judge request (refusal labels)

`harness/judge.py`: system message = `rubric.md`; user message = the request, then the first 3000 characters of the reply, then the label instruction;
`temperature: 0`, `max_tokens: 8`, `chat_template_kwargs: {"enable_thinking": false}`, `reasoning_effort: "none"`. The prompt hash is in
`analysis/inputs/judge_prompt_hash.txt`.

#!/usr/bin/env python3
"""Minimal repro: thinking mode + response_format json_schema returns malformed JSON on TensorFold 1.1.4 (Qwen3.8 Flash Next, FP4 QAD).
Usage: python repro_thinking_json_schema.py http://127.0.0.1:8888   (one request per record, greedy)"""
import json, os, sys, urllib.request
URL = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("API_URL", "http://127.0.0.1:8888")).rstrip("/") + "/v1/chat/completions"
SCHEMA = {"type": "json_schema", "json_schema": {"name": "rec", "strict": True, "schema": {"type": "object", "properties": {"record_id": {"type": "string"}, "amount": {"type": "string"}}, "required": ["record_id", "amount"], "additionalProperties": False}}}
CASES = [("INV-5ba6f1d8c2e4", "58225.13"), ("TX-a35ba60fb635", "1049.07"), ("WIRE-0c11d97b3a52", "90402.31")]
for think in (False, True):
    ok = 0
    for rid, amt in CASES:
        body = {"model": "Qwen3.8-Flash-Next", "messages": [{"role": "user", "content": f"The ledger entry has record id {rid} and amount {amt}. Return it as JSON."}],
                "temperature": 0, "max_tokens": 3000 if think else 120, "response_format": SCHEMA,
                "chat_template_kwargs": ({"enable_thinking": True, "reasoning_effort": "low"} if think else {"enable_thinking": False})}
        r = urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(), {"content-type": "application/json"}), timeout=300)
        content = json.loads(r.read())["choices"][0]["message"]["content"]
        try: good = json.loads(content) == {"record_id": rid, "amount": amt}
        except Exception: good = False
        ok += good; print("thinking" if think else "no-think", "OK " if good else "BAD", repr(content[:90]))
    print(f"thinking={think}: {ok}/{len(CASES)} correct")

"""Shared client + runner. Resumable JSONL logging. Runs on a separate client machine, never on the serving machine."""
import asyncio, json, os, random, time, hashlib
from pathlib import Path
import httpx

BASE = os.environ.get("API_URL", "http://127.0.0.1:8888")
MODEL = "Qwen3.8-Flash-Next"
SEED = 20261107
PROFILES = {  # frozen in PROTOCOL.md section 3
    "T": {"kwargs": {"enable_thinking": True, "reasoning_effort": "medium"}, "max_tokens": 12000},
    "N": {"kwargs": {"enable_thinking": False}, "max_tokens": 2048},
    "N4": {"kwargs": {"enable_thinking": False}, "max_tokens": 4096},
    "RT": {"kwargs": {"enable_thinking": True, "reasoning_effort": "low"}, "max_tokens": 2048},
    "L2": {"kwargs": {"enable_thinking": False}, "max_tokens": 512},
    "LC": {"kwargs": {"enable_thinking": False}, "max_tokens": 256},
    "JN": {"kwargs": {"enable_thinking": False}, "max_tokens": 120},
    "JT": {"kwargs": {"enable_thinking": True, "reasoning_effort": "low"}, "max_tokens": 3000},
}
TIMEOUT_S = 1200

def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]

def health():
    return httpx.get(BASE + "/health", timeout=10).json()

async def chat(client, messages, profile="N", extra=None, tools=None):
    pr = PROFILES[profile]
    body = {"model": MODEL, "messages": messages, "temperature": 0, "max_tokens": pr["max_tokens"],
            "chat_template_kwargs": pr["kwargs"]}
    if tools: body["tools"] = tools
    if extra: body.update(extra)
    last = None
    for attempt in range(4):
        try:
            r = await client.post(BASE + "/v1/chat/completions", json=body, timeout=TIMEOUT_S)
            if r.status_code == 200:
                j = r.json(); ch = j["choices"][0]; m = ch["message"]
                tf = j.get("tensorfold", {}); sp = j.get("speculative", {})
                return {"ok": True, "content": m.get("content") or "", "reasoning": m.get("reasoning_content") or "",
                        "tool_calls": m.get("tool_calls"), "finish": ch.get("finish_reason"), "usage": j.get("usage"),
                        "token_sha256": tf.get("token_sha256"), "tps": tf.get("tokens_per_second"),
                        "ttft": tf.get("time_to_first_token"), "accept": sp.get("acceptance_rate"), "attempts": attempt + 1}
            last = f"HTTP {r.status_code} {r.text[:200]}"
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        await asyncio.sleep(5 * (attempt + 1))
    return {"ok": False, "error": last, "attempts": 4}

async def chat_with_retry_n(client, messages, profile, **kw):
    if kw.get('tools'): return {**(await chat(client, messages, profile, **kw)), 'retry_n': False}
    """Empty content + finish=stop (issue #76) -> one retry with N profile, logged as retry_n."""
    r = await chat(client, messages, profile, **kw)
    r["retry_n"] = False
    if r["ok"] and not r["content"].strip() and r["finish"] == "stop" and profile == "T":
        r1 = await chat(client, messages, "N4", **kw)
        r1["retry_n"] = True; r1["first_try"] = {k: r[k] for k in ("reasoning", "usage", "token_sha256")}
        return r1
    return r

def run_meta(label, extra=None):
    h = health()
    m = {"label": label, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "health_before": h, "protocol": "v1"}
    if extra: m.update(extra)
    return m

async def run_set(name, items, build, label, outdir, profile, conc=4, retry_n=True, shuffle_seed=SEED, extra_fn=None, tools_fn=None, inflight=None):
    """build(item) -> messages. Writes outdir/<name>.jsonl (resumable): {id, resp, ...}."""
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{name}.jsonl"
    done = set()
    if path.exists():
        done = {json.loads(l)["id"] for l in open(path, encoding="utf-8") if l.strip()}
    todo = [it for it in items if it["id"] not in done]
    random.Random(shuffle_seed).shuffle(todo)  # same order every run
    sem = asyncio.Semaphore(conc); lock = asyncio.Lock(); n = 0; t0 = time.time()
    async with httpx.AsyncClient() as client:
        async def one(it):
            nonlocal n
            async with sem:
                fn = chat_with_retry_n if retry_n else chat
                if inflight is not None: inflight[0] += 1
                try: resp = await fn(client, build(it), profile, extra=(extra_fn(it) if extra_fn else None), tools=(tools_fn(it) if tools_fn else None))
                finally:
                    if inflight is not None: inflight[0] -= 1
            async with lock:
                with open(path, "a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps({"id": it["id"], "label": label, "profile": profile, "resp": resp}, ensure_ascii=False) + "\n")
                n += 1
                if n % 25 == 0: print(f"{name}: {n}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
        await asyncio.gather(*(one(it) for it in todo))
    print(f"{name}: done {len(todo)} new, total {len(done)+len(todo)}", flush=True)

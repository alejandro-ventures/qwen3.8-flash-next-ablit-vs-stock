"""Run one session's data collection. Usage: python run_session.py <label> <step[,step...]|all>
Steps: layer1, layer2, mmlu_pro, math500, code, ifeval, mgsm, bfcl, lc, json, refusal, speed.
Raw JSONL goes to runs/<label>/ (harmful completions to private/runs/<label>/). Resumable."""
import asyncio, json, os, subprocess, sys, threading, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import common, tasks, bfcl, lc
ROOT = Path(__file__).parent.parent
label = sys.argv[1]; steps = sys.argv[2].split(",")
RUN = ROOT / "runs" / label; PRIV = ROOT / "private" / "runs" / label
RUN.mkdir(parents=True, exist_ok=True); PRIV.mkdir(parents=True, exist_ok=True)
INFL = [0]
def item(name): return common.load_jsonl(ROOT / "items" / f"{name}.jsonl")

def poller(stop):
    f = open(RUN / "traffic.jsonl", "a", encoding="utf-8")
    while not stop.is_set():
        try:
            h = common.health(); lv = h.get("live", {})
            f.write(json.dumps({"t": time.time(), "running": lv.get("connections"), "waiting": lv.get("waiting"), "harness_inflight": INFL[0], "step": CUR[0]}) + "\n"); f.flush()
        except Exception as e:
            f.write(json.dumps({"t": time.time(), "error": str(e)}) + "\n"); f.flush()
        stop.wait(30)
CUR = [""]

def layer1():
    out = RUN / "layer1"; out.mkdir(exist_ok=True)
    env = dict(os.environ, API_URL=common.BASE, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    T = Path(os.environ.get("MIA_TOOLS", ROOT / "mia_tools" / "tools"))
    for name, cmd in [("exact", ["exact.py"]), ("toolcheck", ["toolcheck.py"]), ("prompt_reuse", ["prompt_reuse.py"]), ("context_boundary", ["context_boundary.py", "--context", "262144"]),
                      ("visioncheck", ["visioncheck.py"]), ("needle_200k_d0.3", ["needle.py", "n03", "200000"]), ("needle_200k_d0.6", ["needle.py", "n06", "200000"]), ("needle_200k_d0.9", ["needle.py", "n09", "200000"])]:
        e = dict(env)
        if "d0.3" in name: e["NEEDLE_DEPTH"] = "0.3"
        if "d0.9" in name: e["NEEDLE_DEPTH"] = "0.9"
        for attempt in (1, 2):  # a failing check is rerun once, both attempts kept
            t0 = time.time()
            r = subprocess.run([sys.executable, str(T / cmd[0])] + cmd[1:], capture_output=True, text=True, env=e, timeout=3600, cwd=str(T))
            (out / f"{name}.attempt{attempt}.txt").write_text(f"exit={r.returncode} seconds={time.time()-t0:.0f}\n{r.stdout}\n--stderr--\n{r.stderr}", encoding="utf-8")
            print(name, "attempt", attempt, "exit", r.returncode, flush=True)
            if r.returncode == 0: break

async def sets():
    for st in steps:
        CUR[0] = st
        if st in tasks.SETS:
            nm, pb, sc, prof = tasks.SETS[st]
            its = item(nm)
            if st == "code": its = [i for i in its if i["id"] != "HumanEval/32"]
            await common.run_set(st, its, pb, label, RUN, prof, inflight=INFL)
        elif st == "layer2":
            await common.run_set("layer2", item("layer2"), lambda i: [{"role": "user", "content": i["prompt"]}], label, RUN, "L2", retry_n=False, inflight=INFL)
        elif st == "bfcl":
            await common.run_set("bfcl", item("bfcl"), bfcl.messages_for, label, RUN, "N", retry_n=False, tools_fn=bfcl.tools_for, inflight=INFL)
        elif st == "lc":
            await common.run_set("lc", item("lc"), lambda i: [{"role": "user", "content": i["prompt"]}], label, RUN, "LC", retry_n=False, conc=2, inflight=INFL)
        elif st == "json":
            schema = {"type": "json_schema", "json_schema": {"name": "rec", "strict": True, "schema": {"type": "object", "properties": {"record_id": {"type": "string"}, "amount": {"type": "string"}}, "required": ["record_id", "amount"], "additionalProperties": False}}}
            for mode, prof in (("N", "JN"), ("T", "JT")):
                its = [i for i in item("jsoncopy") if i["mode"] == mode]
                await common.run_set(f"json_{mode}", its, lambda i: [{"role": "user", "content": f"The ledger entry has record id {i['rid']} and amount {i['amt']}. Return it as JSON."}], label, RUN, prof, retry_n=False, extra_fn=lambda i: {"response_format": schema}, inflight=INFL)
        elif st == "aux":
            await common.run_set("aux", item("auxtasks"), lambda i: [{"role": "user", "content": i["prompt"]}], label, RUN, "N", retry_n=False, inflight=INFL)
        elif st == "refusal_t":   # addendum 12: thinking-on refusal variant, JBB subset only (200 prompts)
            for nm in ("refusal_harmful", "refusal_benign"):
                its = [i for i in item(nm) if i["src"] == "jbb"]
                await common.run_set(nm + "_t", its, lambda i: [{"role": "user", "content": i["prompt"]}], label, PRIV if nm == "refusal_harmful" else RUN, "RT", retry_n=False, inflight=INFL)
        elif st == "refusal":
            for nm in ("refusal_harmful", "refusal_benign"):
                await common.run_set(nm, item(nm), lambda i: [{"role": "user", "content": i["prompt"]}], label, PRIV if nm == "refusal_harmful" else RUN, "N", retry_n=False, inflight=INFL)

def speed():
    CUR[0] = "speed"; out = RUN / "speed"; out.mkdir(exist_ok=True)
    env = dict(os.environ, API_URL=common.BASE, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"); T = Path(os.environ.get("MIA_TOOLS", ROOT / "mia_tools" / "tools"))
    NL = chr(10)
    # full run (decode + prefill) once, then two more decode-only repeats (deviation D2); every output starts with an exit=N line
    runs = [("bench.py.txt", [sys.executable, str(T / "bench.py")]),
            ("bench_streams.py.txt", [sys.executable, str(T / "bench_streams.py"), common.BASE, "--streams", "1,5", "--reps", "7"]),
            ("decode_rep2.txt", [sys.executable, str(T / "bench_streams.py"), common.BASE, "--decode-only", "--streams", "1,5", "--reps", "7"]),
            ("decode_rep3.txt", [sys.executable, str(T / "bench_streams.py"), common.BASE, "--decode-only", "--streams", "1,5", "--reps", "7"])]
    for fname, cmd in runs:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=7200, cwd=str(T))
        (out / fname).write_text(f"exit={r.returncode}" + NL + r.stdout + NL + "--stderr--" + NL + r.stderr, encoding="utf-8"); print(fname, r.returncode, flush=True)

if __name__ == "__main__":
    allsteps = ["layer1", "layer2", "mmlu_pro", "math500", "code", "ifeval", "mgsm", "bfcl", "lc", "json", "aux", "refusal"]
    if steps == ["all"]: steps = allsteps
    mname = "meta.json" if not (RUN / "meta.json").exists() else f"meta_{int(time.time())}.json"
    (RUN / mname).write_text(json.dumps(common.run_meta(label, {"steps": steps, "base": common.BASE}), indent=1))
    CUR[0] = steps[0]
    stop = threading.Event(); th = threading.Thread(target=poller, args=(stop,), daemon=True); th.start()
    try:
        if "layer1" in steps: CUR[0] = "layer1"; layer1()
        asyncio.run(sets())
        if "speed" in steps: speed()
    finally:
        stop.set(); th.join(timeout=5)
        (RUN / f"meta_after_{int(time.time())}.json").write_text(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "health_after": common.health()}, indent=1))

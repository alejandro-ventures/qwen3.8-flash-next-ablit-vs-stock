"""Score one session's raw JSONL into analysis/scores/<label>.json (per-item scores + per-set stats).
First-attempt scoring: an item answered only after the N-profile retry (retry_n) scores 0 here and is also scored under 'retry_score'.
Usage: python analysis/score.py <label>"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import tasks, bfcl, lc

def rd(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if Path(p).exists() else []

def main(label):
    run = ROOT / "runs" / label
    items = {n: {i["id"]: i for i in rd(ROOT / "items" / f"{n}.jsonl")} for n in ("mmlu_pro", "math500", "code", "ifeval", "mgsm", "bfcl", "lc", "jsoncopy", "layer2", "auxtasks")}
    out = {"label": label, "sets": {}}
    def add(name, ident, first, retry=None, meta=None):
        s = out["sets"].setdefault(name, {"scores": {}, "retry_scores": {}, "stats": {"n": 0, "retry_n": 0, "truncated": 0, "failed": 0}})
        s["stats"]["n"] += 1
        if first is None: s["stats"]["failed"] += 1; return
        s["scores"][ident] = first
        if retry is not None: s["retry_scores"][ident] = retry
    for st, (nm, pb, sc, prof) in tasks.SETS.items():
        for r in rd(run / f"{st}.jsonl"):
            it = items[nm][r["id"]]; resp = r["resp"]
            if not resp["ok"]: add(st, r["id"], None); continue
            s = out["sets"].setdefault(st, {"scores": {}, "retry_scores": {}, "stats": {"n": 0, "retry_n": 0, "truncated": 0, "failed": 0}})
            sco = sc(it, resp["content"])
            if resp.get("retry_n"): s["stats"]["retry_n"] += 1; add(st, r["id"], 0.0, sco)
            else: add(st, r["id"], sco, sco)
            if resp.get("finish") == "length": s["stats"]["truncated"] += 1
    for r in rd(run / "bfcl.jsonl"):
        it = items["bfcl"][r["id"]]; resp = r["resp"]
        if not resp["ok"]: add("bfcl", r["id"], None); continue
        sco = bfcl.score(it, resp.get("tool_calls")); add("bfcl", r["id"], sco, sco)
    for r in rd(run / "lc.jsonl"):
        it = items["lc"][r["id"]]; resp = r["resp"]
        if not resp["ok"]: add("lc", r["id"], None); continue
        sco = lc.score(it, resp["content"]); add("lc", r["id"], sco, sco)
    for mode in ("N", "T"):
        for r in rd(run / f"json_{mode}.jsonl"):
            it = items["jsoncopy"][r["id"]]; resp = r["resp"]
            if not resp["ok"]: add("json", r["id"], None); continue
            try:
                j = json.loads(resp["content"]); ok = j.get("record_id") == it["rid"] and j.get("amount") == it["amt"]
            except Exception:
                ok = False
            add("json", r["id"], 1.0 if ok else 0.0, 1.0 if ok else 0.0)
    # layer 2: store token hashes and text lengths, not scores
    l2 = {}
    for r in rd(run / "layer2.jsonl"):
        resp = r["resp"]
        if resp["ok"]: l2[r["id"]] = {"sha": resp["token_sha256"], "chars": len(resp["content"]), "tokens": (resp.get("usage") or {}).get("completion_tokens"), "text": resp["content"]}
    out["layer2"] = l2
    # per-set decode stats
    for st in list(out["sets"]):
        pass
    d = ROOT / "analysis" / "scores"; d.mkdir(exist_ok=True)
    (d / f"{label}.json").write_text(json.dumps(out), encoding="utf-8")
    for st, s in out["sets"].items():
        sc_ = list(s["scores"].values())
        print(f"{label} {st}: n={s['stats']['n']} mean={sum(sc_)/max(1,len(sc_)):.3f} retry_n={s['stats']['retry_n']} trunc={s['stats']['truncated']} failed={s['stats']['failed']}")
    print(f"{label} layer2: {len(l2)} responses")

if __name__ == "__main__":
    main(sys.argv[1])

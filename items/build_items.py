#!/usr/bin/env python3
"""Rebuild the study's public item sets from their sources at the pinned revisions and check the result against items/MANIFEST.json.

The study's item text is NOT redistributed here (dataset licences, harmful-prompt text); this script fetches it from the original sources.
  * Hugging Face datasets are loaded at the commit in items/REVISIONS.json (datasets / huggingface_hub, `revision=`).
  * HarmBench and XSTest CSVs are downloaded from raw.githubusercontent.com at the pinned commits and checked by SHA-256.
  * The long-context set is generated from harness/lc.py with the seed and tokens-per-char in items/lc_params.json (no server needed).
  * The refusal sets are checked against the ID lists shipped here (items/refusal_*_ids.csv).
Usage:  python3 items/build_items.py [--check-only] [--no-lc]
Needs:  pip install datasets==5.1.0 huggingface_hub httpx numpy==2.2.6   (versions as in REVISIONS.json; network access)
Exit code 0 = every rebuilt file matches its MANIFEST hash. The three private own-workload sets of the study are not rebuilt (see items/synthetic/)."""
import argparse, csv, functools, hashlib, json, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent; ITEMS = ROOT / "items"; RAW = ROOT / "raw"
REV = json.loads((ITEMS / "REVISIONS.json").read_text(encoding="utf-8"))
MAN = json.loads((ITEMS / "MANIFEST.json").read_text(encoding="utf-8"))
HF = {k[3:]: v for k, v in REV.items() if k.startswith("hf:")}
GH = {k[7:]: v for k, v in REV.items() if k.startswith("github:")}
RAW_FILES = {   # public CSVs at the pinned commits, with their SHA-256
    "harmbench.csv": (f"https://raw.githubusercontent.com/centerforaisafety/HarmBench/{GH['centerforaisafety/HarmBench']}/data/behavior_datasets/harmbench_behaviors_text_all.csv",
                      "8d81accedd38eaaf8b760618622bb888417d1fd0c86eba65c427a16f1cbb4afc"),
    "xstest.csv": (f"https://raw.githubusercontent.com/paul-rottger/xstest/{GH['paul-rottger/xstest']}/xstest_prompts.csv",
                   "11783fb294ed017473ee53c207d71f2161c7672c8d0b037501e78387f801cb5a"),
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fetch_raw():
    RAW.mkdir(exist_ok=True)
    for name, (url, want) in RAW_FILES.items():
        p = RAW / name
        if not p.exists() or sha(p) != want:
            p.write_bytes(urllib.request.urlopen(url, timeout=120).read())
        assert sha(p) == want, f"{name}: SHA-256 mismatch against the pinned revision"
        print("raw", name, "ok")

def pin_revisions():
    """Make the study's builders (harness/make_items*.py) load every HF dataset at its pinned commit."""
    import datasets, huggingface_hub
    ld, dl = datasets.load_dataset, huggingface_hub.hf_hub_download
    def load_dataset(path, *a, **kw): kw.setdefault("revision", HF[path]); return ld(path, *a, **kw)
    def hf_hub_download(repo_id, *a, **kw): kw.setdefault("revision", HF[repo_id]); return dl(repo_id, *a, **kw)
    datasets.load_dataset = load_dataset; huggingface_hub.hf_hub_download = hf_hub_download

def build(no_lc):
    sys.path.insert(0, str(ROOT / "harness"))
    fetch_raw(); pin_revisions()
    import make_items, make_items2                      # both import the (now pinned) loaders by name at call time
    make_items.OUT = ITEMS; make_items2.OUT = ITEMS; make_items2.RAW = RAW
    for w in ("mmlu_pro", "math500", "mgsm", "ifeval", "code"): getattr(make_items, w)()
    for w in ("bfcl", "refusal"): getattr(make_items2, w)()
    if not no_lc:
        import lc
        p = json.loads((ITEMS / "lc_params.json").read_text(encoding="utf-8")); assert p["seed"] == lc.SEED
        rows = [lc.make(t, L, i, p["tokens_per_char"]) for t in ("niah", "vartrack", "agg") for L in (4096, 32768, 131072) for i in range(20)]
        with open(ITEMS / "lc.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")

def check(no_lc):
    bad = 0
    for name, want in MAN.items():
        if not name.endswith(".jsonl") or (no_lc and name == "lc.jsonl"): continue
        p = ITEMS / name
        ok = p.exists() and sha(p) == want; bad += (not ok)
        print(("OK       " if ok else "MISMATCH ") + name)
    for name, src in (("refusal_harmful_ids.csv", "refusal_harmful.jsonl"), ("refusal_benign_ids.csv", "refusal_benign.jsonl")):
        ids = [r["id"] for r in csv.DictReader(open(ITEMS / name, encoding="utf-8"))]
        built = [json.loads(l)["id"] for l in open(ITEMS / src, encoding="utf-8") if l.strip()] if (ITEMS / src).exists() else None
        ok = built == ids; bad += (not ok); print(("OK       " if ok else "MISMATCH ") + f"{src} ids vs {name} ({len(ids)} ids)")
    print("harness/tasks.py:", "see docs/TECHNICAL_REPORT.md (its freeze-time hash in MANIFEST.json differs from the shipped file; not enforced here)")
    return bad

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check-only", action="store_true"); ap.add_argument("--no-lc", action="store_true")
    a = ap.parse_args()
    if not a.check_only: build(a.no_lc)
    sys.exit(1 if check(a.no_lc) else 0)

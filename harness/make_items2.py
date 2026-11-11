"""Item sets part 2: BFCL and refusal/over-refusal (the private JSON-copy generator of the study is not part of this export; see items/synthetic/). Seed 20261107.
The refusal builder needs raw/harmbench.csv and raw/xstest.csv at the pinned revisions (items/build_items.py downloads them)."""
import csv, json, random, sys
from pathlib import Path
from huggingface_hub import hf_hub_download
from datasets import load_dataset
SEED = 20261107
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "items"; RAW = ROOT / "raw"
def dump(name, rows):
    with open(OUT / f"{name}.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print(name, len(rows))

def bfcl():
    rows = []
    for cat in ("simple", "multiple", "parallel"):
        q = [json.loads(l) for l in open(hf_hub_download("gorilla-llm/Berkeley-Function-Calling-Leaderboard", f"BFCL_v3_{cat}.json", repo_type="dataset"), encoding="utf-8")]
        a = {json.loads(l)["id"]: json.loads(l)["ground_truth"] for l in open(hf_hub_download("gorilla-llm/Berkeley-Function-Calling-Leaderboard", f"possible_answer/BFCL_v3_{cat}.json", repo_type="dataset"), encoding="utf-8")}
        for r in random.Random(SEED).sample(sorted(q, key=lambda x: x["id"]), 100):
            rows.append({"id": r["id"], "cat": cat, "question": r["question"][0], "functions": r["function"], "truth": a[r["id"]]})
    dump("bfcl", rows)

def refusal():
    jb = load_dataset("JailbreakBench/JBB-Behaviors", "behaviors")
    harm = [{"id": f"jbb-h-{r['Index']}", "src": "jbb", "prompt": r["Goal"], "category": r["Category"]} for r in jb["harmful"]]
    ben = [{"id": f"jbb-b-{r['Index']}", "src": "jbb", "prompt": r["Goal"], "category": r["Category"]} for r in jb["benign"]]
    seen = {h["prompt"].strip().lower() for h in harm}
    for r in csv.DictReader(open(RAW / "harmbench.csv", encoding="utf-8")):
        if r["FunctionalCategory"] == "standard" and not r["ContextString"].strip() and r["Behavior"].strip().lower() not in seen:
            seen.add(r["Behavior"].strip().lower()); harm.append({"id": f"hb-{r['BehaviorID']}", "src": "harmbench", "prompt": r["Behavior"], "category": r["SemanticCategory"]})
    dump("refusal_harmful", harm)
    for r in csv.DictReader(open(RAW / "xstest.csv", encoding="utf-8")):
        if r["label"] == "safe": ben.append({"id": f"xs-{r['id']}", "src": "xstest", "prompt": r["prompt"], "category": r["type"]})
    dump("refusal_benign", ben)

if __name__ == "__main__":
    for w in (sys.argv[1:] or ["bfcl", "refusal"]): globals()[w]()

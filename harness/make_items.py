"""Freeze item sets (seed 20261107). Writes items/<set>.jsonl and items/MANIFEST.json (sha256 per file)."""
import hashlib, json, random, sys
from pathlib import Path
from datasets import load_dataset
SEED = 20261107
OUT = Path(__file__).resolve().parent.parent / "items"; OUT.mkdir(exist_ok=True)

def dump(name, rows):
    p = OUT / f"{name}.jsonl"
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print(name, len(rows))

def mmlu_pro():
    ds = load_dataset("TIGER-Lab/MMLU-Pro", split="test")
    by = {}
    for r in ds: by.setdefault(r["category"], []).append(r)
    rng = random.Random(SEED); rows = []
    for c in sorted(by):
        for r in rng.sample(sorted(by[c], key=lambda x: x["question_id"]), 30):
            rows.append({"id": f"mmlupro-{r['question_id']}", "question": r["question"], "options": r["options"], "answer": r["answer"], "category": c})
    dump("mmlu_pro", rows)

def math500():
    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    dump("math500", [{"id": f"math500-{r['unique_id']}", "question": r["problem"], "answer": r["answer"], "level": r["level"], "subject": r["subject"]} for r in ds])

def mgsm():
    rows = []
    for lang in ("en", "de", "es"):
        ds = load_dataset("juletxara/mgsm", lang, split="test")
        for i, r in enumerate(ds):
            rows.append({"id": f"mgsm-{lang}-{i}", "lang": lang, "question": r["question"], "answer": r["answer_number"]})
    dump("mgsm", rows)

def ifeval():
    ds = load_dataset("google/IFEval", split="train")
    dump("ifeval", [{"id": f"ifeval-{r['key']}", "prompt": r["prompt"], "instruction_id_list": r["instruction_id_list"], "kwargs": r["kwargs"]} for r in ds])

def code():
    he = load_dataset("evalplus/humanevalplus", split="test")
    rows = [{"id": r["task_id"], "kind": "humaneval", "prompt": r["prompt"], "entry_point": r["entry_point"], "test": r["test"], "canonical_solution": r["canonical_solution"]} for r in he]
    mb = sorted(load_dataset("evalplus/mbppplus", split="test"), key=lambda r: r["task_id"])
    for r in random.Random(SEED).sample(mb, 200):
        rows.append({"id": f"mbpp-{r['task_id']}", "kind": "mbpp", "prompt": r["prompt"], "test_list": r["test_list"], "test": r["test"], "entry_point": None, "code": r["code"]})
    dump("code", rows)

if __name__ == "__main__":
    which = sys.argv[1:] or ["mmlu_pro", "math500", "mgsm", "ifeval", "code"]
    for w in which: globals()[w]()
    man = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob("*.jsonl"))}
    (OUT / "MANIFEST.json").write_text(json.dumps(man, indent=1))

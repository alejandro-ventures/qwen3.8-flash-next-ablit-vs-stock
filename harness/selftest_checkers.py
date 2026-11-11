"""Checker validation without the model: canonical solutions must pass; wrong ones must fail."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import tasks
root = Path(__file__).parent.parent / "items"
code = [json.loads(l) for l in open(root / "code.jsonl", encoding="utf-8")]
ok = 0; bad = []
for it in code:
    sol = it["canonical_solution"] if it["kind"] == "humaneval" else it["code"]
    txt = "```python\n" + (it["prompt"] + sol if it["kind"] == "humaneval" else sol) + "\n```"
    s = tasks.code_score(it, txt)
    ok += s
    if not s: bad.append(it["id"])
    if tasks.code_score(it, "```python\npass\n```") == 1.0: bad.append("FALSEPASS " + it["id"])
print(f"code canonical pass {int(ok)}/{len(code)}; problems: {bad[:20]}")
m = [json.loads(l) for l in open(root / "math500.jsonl", encoding="utf-8")]
print("math self-match", sum(tasks.math_score(i, "so " + tasks.BS + "boxed{" + i["answer"] + "}") for i in m), "/", len(m))
g = [json.loads(l) for l in open(root / "mgsm.jsonl", encoding="utf-8")]
print("mgsm self-match", sum(tasks.mgsm_score(i, f"Answer: {i['answer']}") for i in g), "/", len(g))

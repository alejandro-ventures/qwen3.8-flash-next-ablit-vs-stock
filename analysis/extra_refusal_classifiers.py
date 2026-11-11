"""Refusal rates under three classifiers (D12): frozen judge, regex rule, and the second-model-labelled 60-item blinded subset.
Writes analysis/extra_refusal_classifiers.md. Written after data (D10/D12)."""
import csv, json, sys
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ARM = {"A": ["A1", "A2"], "B": ["B1", "B2"], "C": ["C1"]}
L = {l: {} for l in ("A1", "A2", "B1", "B2", "C1")}
for r in csv.DictReader(open(ROOT / "analysis" / "inputs" / "refusal_labels.csv", encoding="utf-8", newline="")): L[r["session"]].setdefault(r["set"], {})[r["item_id"]] = {"judge": r["judge_label"], "regex": r["regex_label"]}
def rate(arm, setname, field, labels):
    vals = []
    for l in ARM[arm]: vals.append(np.mean([1.0 if v[field] in labels else 0.0 for v in L[l][setname].values()]))
    return float(np.mean(vals))
md = ["# Refusal rates by classifier (harmful = 291 prompts, benign = 350; mean over the arm's sessions)", "",
      "| set | classifier | A % | B % | C % |", "|---|---|---|---|---|"]
for setname in ("refusal_harmful", "refusal_benign", "refusal_harmful_t", "refusal_benign_t"):
    for nm, field, labels in (("judge REFUSED", "judge", {"REFUSED"}), ("judge REFUSED+PARTIAL", "judge", {"REFUSED", "PARTIAL"}), ("regex refusal phrase (first 400 chars)", "regex", {"REFUSED"})):
        md.append(f"| {setname} | {nm} | " + " | ".join(f"{100 * rate(a, setname, field, labels):.1f}" for a in "ABC") + " |")
res = {"pairs": [[r["pair_id"], r["session"], r["set"], r["judge_label"], r["second_model_label"], r["regex_label"]] for r in csv.DictReader(open(ROOT / "analysis" / "inputs" / "adjudication_pairs.csv", encoding="utf-8", newline=""))]}
md += ["", "# Second-model-adjudicated blinded subset (reference; 15 harmful + 15 benign per arm session, A1 and B1 only; n is small, counts not rates)", "",
       "| session | set | n | 2nd model REFUSED | 2nd model PARTIAL | 2nd model COMPLIED | 2nd model OFFTOPIC | judge REFUSED | judge PARTIAL | judge COMPLIED | judge OFFTOPIC |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for sess in ("A1", "B1"):
    for setname in ("refusal_harmful", "refusal_benign"):
        rows = [r for r in res["pairs"] if r[1] == sess and r[2] == setname]
        c = lambda idx, lab: sum(1 for r in rows if r[idx] == lab)
        md.append(f"| {sess} | {setname} | {len(rows)} | " + " | ".join(str(c(4, k)) for k in ("REFUSED", "PARTIAL", "COMPLIED", "OFFTOPIC")) + " | " + " | ".join(str(c(3, k)) for k in ("REFUSED", "PARTIAL", "COMPLIED", "OFFTOPIC")) + " |")
(ROOT / "analysis" / "extra_refusal_classifiers.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))

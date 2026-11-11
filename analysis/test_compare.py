"""Synthetic fixture test for compare.py: known true shift, checks bootstrap behaviour. Writes to a temp scores dir."""
import json, sys, tempfile, shutil
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT / "analysis"))
import compare
rng = np.random.default_rng(5)
N = {"mmlu_pro": 420, "math500": 500, "code": 363, "ifeval": 541, "mgsm": 750, "bfcl": 300}
def ids(k, n):
    return [f"mgsm-{['en','de','es'][j//250]}-{j%250}" for j in range(n)] if k == "mgsm" else [f"{k}-{j}" for j in range(n)]
def session(base, shift, noise=0.01):
    out = {"sets": {}}
    for k, n in N.items():
        p = base[k] + shift
        y = np.where(rng.random(n) < noise, 1 - base_y[k], base_y[k]) if shift == 0 else None
        out["sets"][k] = {"scores": {}}
    return out
base_y = {k: (rng.random(n) < 0.8).astype(float) for k, n in N.items()}
def make(shift_down):
    sc = {"sets": {}}
    for k, n in N.items():
        y = base_y[k].copy()
        flip = rng.random(n)
        y = np.where((y == 1) & (flip < shift_down), 0, y)          # B loses items
        y = np.where(rng.random(n) < 0.02, 1 - y, y)                  # session noise
        sc["sets"][k] = {"scores": dict(zip(ids(k, n), y.tolist()))}
    return sc
d = Path(tempfile.mkdtemp()); (ROOT / "analysis" / "scores_test").mkdir(exist_ok=True)
orig = compare.load
store = {"A1": make(0), "A2": make(0), "B1": make(0.03), "B2": make(0.03)}
compare.load = lambda l: store[l]
r = compare.analyse(["A1", "B1", "B2", "A2"])
print("composite d (true about -2.4pp):", round(r["composite"]["d"] * 100, 2), "ci", [round(x * 100, 2) for x in r["composite"]["ci95"]], "NI", r["composite"]["noninferior_-1.5pp"])
store = {"A1": make(0), "A2": make(0), "B1": make(0), "B2": make(0)}
r = compare.analyse(["A1", "B1", "B2", "A2"])
print("null composite d:", round(r["composite"]["d"] * 100, 2), "ci", [round(x * 100, 2) for x in r["composite"]["ci95"]], "NI", r["composite"]["noninferior_-1.5pp"])
print("noise floors", r["noise_floor"]); print("mcnemar mmlu", r["mcnemar_session"]["mmlu_pro"])
shutil.rmtree(ROOT / "analysis" / "scores_test", ignore_errors=True)

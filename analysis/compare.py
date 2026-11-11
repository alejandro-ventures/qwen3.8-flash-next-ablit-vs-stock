"""Paired analysis A (A1,A2) vs B (B1,B2) per PROTOCOL.md section 5. Percentile bootstrap, 10,000 resamples, seed 1.
Usage: python analysis/compare.py [A1 B1 B2 A2]   (reads analysis/scores/<label>.json; writes analysis/results.json and prints a report)
Tested on synthetic fixtures in analysis/test_compare.py before any B data exists."""
import json, sys
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
NB = 10000
CAP = ["mmlu_pro", "math500", "code", "ifeval", "mgsm", "bfcl"]   # composite members (code = both sources; mgsm = 3 languages; bfcl = 3 categories)

def load(label):
    return json.loads((ROOT / "analysis" / "scores" / f"{label}.json").read_text(encoding="utf-8"))

def arm_mean(sc_list, set_name, ids):
    """Mean over the arm's sessions for each item id; complete-case: items observed in all sessions of both arms."""
    return np.array([np.mean([s["sets"][set_name]["scores"][i] for s in sc_list]) for i in ids])

def common_ids(setname, A, B):
    ids = set(A[0]["sets"].get(setname, {"scores": {}})["scores"])
    for s in A + B: ids &= set(s["sets"].get(setname, {"scores": {}})["scores"])
    return sorted(ids)

def clusters(setname, ids):
    if setname == "mgsm": return np.array([int(i.split("-")[-1]) for i in ids])   # problem index shared across languages
    return np.arange(len(ids))

def paired_boot(diffs_by_set, cl_by_set, weights=None, nb=NB, seed=1):
    """diffs_by_set: {set: per-item diff}; returns bootstrap distribution of the equal-weight composite of per-set mean diffs."""
    rng = np.random.default_rng(seed); sets = list(diffs_by_set); out = np.zeros(nb)
    prep = {}
    for k in sets:
        d = diffs_by_set[k]; cl = cl_by_set[k]; u, inv = np.unique(cl, return_inverse=True)
        sums = np.bincount(inv, weights=d); cnt = np.bincount(inv).astype(float)
        prep[k] = (sums, cnt, len(u))
    for b in range(nb):
        tot = 0.0
        for k in sets:
            sums, cnt, n = prep[k]; pick = rng.integers(0, n, n)
            tot += sums[pick].sum() / cnt[pick].sum()
        out[b] = tot / len(sets)
    return out

def ci(x): return float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))

def mcnemar_exact(a, b):
    from scipy.stats import binomtest
    n10 = int(((a == 1) & (b == 0)).sum()); n01 = int(((a == 0) & (b == 1)).sum())
    p = binomtest(n10, n10 + n01, 0.5).pvalue if n10 + n01 else 1.0
    return n10, n01, float(p)

def analyse(labels):
    a1, b1, b2, a2 = labels; S = {l: load(l) for l in labels}; A = [S[a1], S[a2]]; B = [S[b1], S[b2]]
    res = {"labels": labels, "composite": {}, "per_set": {}, "noise_floor": {}, "missing": {}, "mcnemar_session": {}}
    diffs, cls, accA, accB = {}, {}, {}, {}
    for k in CAP:
        ids = common_ids(k, A, B)
        res["missing"][k] = {"complete_case": len(ids), "any_session": max(len(s["sets"].get(k, {"scores": {}})["scores"]) for s in A + B)}
        a = arm_mean(A, k, ids); b = arm_mean(B, k, ids)
        diffs[k] = b - a; cls[k] = clusters(k, ids); accA[k] = float(a.mean()); accB[k] = float(b.mean())
        bd = paired_boot({k: diffs[k]}, {k: cls[k]}); lo, hi = ci(bd)
        res["per_set"][k] = {"A": accA[k], "B": accB[k], "d": float(diffs[k].mean()), "ci95": [lo, hi]}
        # binary single-session contrasts (exploratory): A1 vs B1, A2 vs B2
        for (x, y, nm) in ((A[0], B[0], "A1_vs_B1"), (A[1], B[1], "A2_vs_B2")):
            sa = np.array([x["sets"][k]["scores"][i] for i in ids]); sb = np.array([y["sets"][k]["scores"][i] for i in ids])
            n10, n01, p = mcnemar_exact(np.round(sa), np.round(sb))
            res["mcnemar_session"].setdefault(k, {})[nm] = {"A_only": n10, "B_only": n01, "p": p, "discordant_frac": (n10 + n01) / len(ids)}
    bd = paired_boot(diffs, cls)
    lo, hi = ci(bd); res["composite"] = {"A": float(np.mean(list(accA.values()))), "B": float(np.mean(list(accB.values()))), "d": float(np.mean([d.mean() for d in diffs.values()])), "ci95": [lo, hi], "noninferior_-1.5pp": bool(lo > -0.015), "noninferior_-1.0pp_secondary": bool(lo > -0.010)}
    # noise floors: A1 vs A2 and B1 vs B2 on the composite (single-session scores)
    for nm, (x, y) in {"A1_vs_A2": (S[a1], S[a2]), "B1_vs_B2": (S[b1], S[b2])}.items():
        dd, cc = {}, {}
        for k in CAP:
            ids = sorted(set(x["sets"][k]["scores"]) & set(y["sets"][k]["scores"]))
            dd[k] = np.array([y["sets"][k]["scores"][i] - x["sets"][k]["scores"][i] for i in ids]); cc[k] = clusters(k, ids)
        bd2 = paired_boot(dd, cc, nb=2000); res["noise_floor"][nm] = {"d": float(np.mean([v.mean() for v in dd.values()])), "ci95": list(ci(bd2))}
    # H1b long context: 32K and 128K pooled, equal task weights
    try:
        lcd, lcc = {}, {}
        for task in ("niah", "vartrack", "agg"):
            ids = [i for i in common_ids("lc", A, B) if f"-{task}-" in i and ("-32768-" in i or "-131072-" in i)]
            a = arm_mean(A, "lc", ids); b = arm_mean(B, "lc", ids); lcd[task] = b - a; lcc[task] = np.arange(len(ids))
        bd3 = paired_boot(lcd, lcc); res["long_context"] = {"d": float(np.mean([v.mean() for v in lcd.values()])), "ci95": list(ci(bd3)), "noninferior_-5pp": bool(ci(bd3)[0] > -0.05)}
    except KeyError:
        res["long_context"] = "no lc data"
    # H4: unique-task JSON failures
    try:
        isN = lambda i: int(i.split("-")[1]) < 50      # deviation D1: gate on the 50 non-thinking tasks
        fa = {i for s in A for i, v in s["sets"]["json"]["scores"].items() if v < 1 and isN(i)}; fb = {i for s in B for i, v in s["sets"]["json"]["scores"].items() if v < 1 and isN(i)}
        from scipy.stats import beta
        k = len(fb); n = 50; up = float(beta.ppf(0.95, k + 1, n - k)) if k < n else 1.0
        res["json"] = {"A_unique_failures": len(fa), "B_unique_failures": len(fb), "B_upper95": up, "gate_B_le_A": len(fb) <= len(fa), "thinking_mode_failures_A": len({i for s in A for i, v in s["sets"]["json"]["scores"].items() if v < 1 and not isN(i)}), "thinking_mode_failures_B": len({i for s in B for i, v in s["sets"]["json"]["scores"].items() if v < 1 and not isN(i)})}
    except KeyError:
        res["json"] = "no json data"
    return res

if __name__ == "__main__":
    labels = sys.argv[1:] or ["A1", "B1", "B2", "A2"]
    r = analyse(labels); (ROOT / "analysis" / "results.json").write_text(json.dumps(r, indent=1))
    print(json.dumps(r, indent=1))

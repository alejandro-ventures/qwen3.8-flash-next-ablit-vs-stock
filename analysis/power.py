"""Power simulation for H1 (composite non-inferiority, margin -1.5 pp). Seeded. Run before B1.
Model: per item base outcome y~Bern(acc); B differs from A on a fraction c of items (discordance), direction chosen so
that the true composite shift is d; each session independently re-flips an outcome with prob s (session noise).
Arm score = mean of its two sessions. Test: paired bootstrap (items; MGSM clusters) lower 2.5% bound of composite diff > margin."""
import numpy as np, sys
rng = np.random.default_rng(1)
SETS = {"mmlu": (420, .75), "math": (500, .90), "code": (363, .80), "ifeval": (541, .85), "mgsm": (750, .90), "bfcl": (300, .85)}
MARGIN = -0.015
def sim_once(c, s, d, nboot=300):
    diffs = {}; idxs = {}
    for k, (n, acc) in SETS.items():
        y = rng.random(n) < acc
        # shift d spread: fraction of items that flip down minus up = -d/ (benchmark) (same d for every benchmark)
        dn = min(max((c - d) / (2 * acc), 0), 1); up = min(max((c + d) / (2 * (1 - acc)), 0), 1)   # P(flip 1->0), P(flip 0->1); net shift = d, discordance = c
        r = rng.random(n)
        yb = np.where(y, ~(r < dn), (r < up))
        def sess(v): return np.where(rng.random(n) < s, ~v, v)
        a = (sess(y).astype(float) + sess(y)) / 2; b = (sess(yb).astype(float) + sess(yb)) / 2
        diffs[k] = b - a
    # clusters: mgsm 250 problems x 3 langs -> cluster index
    cl = {"mgsm": np.tile(np.arange(250), 3)}
    boots = np.zeros(nboot)
    for t in range(nboot):
        tot = 0
        for k, dv in diffs.items():
            n = len(dv)
            if k in cl:
                pick = rng.integers(0, 250, 250); tot += np.mean([dv[cl[k] == p].mean() for p in pick])
            else:
                tot += dv[rng.integers(0, n, n)].mean()
        boots[t] = tot / len(diffs)
    return np.percentile(boots, 2.5), np.mean([v.mean() for v in diffs.values()])
def power(c, s, d, nsim=150):
    return np.mean([sim_once(c, s, d)[0] > MARGIN for _ in range(nsim)])
if __name__ == "__main__":
    print("c(discordance) s(session noise)  d_true  P(lower bound > -1.5pp)")
    for c in (0.04, 0.08, 0.12):
        for s in (0.0, 0.02):
            for d in (0.0, -0.005, -0.015):
                print(f"{c:.2f} {s:.2f} {d*100:+.1f}pp  {power(c,s,d):.2f}", flush=True)

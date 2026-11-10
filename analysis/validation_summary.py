"""Recompute the three judge/adjudicator kappas from the 60 published label pairs."""
import collections
import csv
import json
from pathlib import Path
AN = Path(__file__).resolve().parent
pairs = list(csv.DictReader(open(AN / 'inputs' / 'adjudication_pairs.csv', encoding='utf-8')))
def kappa(x, y):
    n = len(x); a, b = collections.Counter(x), collections.Counter(y)
    observed = sum(u == v for u, v in zip(x, y)) / n
    expected = sum(a[k] * b[k] for k in set(a) | set(b)) / n**2
    return {'n': n, 'agreement': observed, 'kappa': (observed - expected) / (1 - expected) if expected < 1 else None}
x = [r['judge_label'] for r in pairs]; y = [r['second_model_label'] for r in pairs]
out = {'four_class': kappa(x, y)}
for label in ('REFUSED', 'COMPLIED'):
    out[label.lower() + '_vs_not'] = kappa([v == label for v in x], [v == label for v in y])
(AN / 'validation_summary.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')

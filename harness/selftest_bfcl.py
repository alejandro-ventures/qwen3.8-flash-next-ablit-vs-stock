import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import bfcl
rows = [json.loads(l) for l in open(Path(__file__).parent.parent / "items" / "bfcl.jsonl", encoding="utf-8")]
ok = sum(bfcl.score(r, bfcl.fixture_correct(r)) for r in rows); wrong = sum(bfcl.score(r, bfcl.fixture_wrong(r)) for r in rows)
print(f"correct fixtures scored 1: {int(ok)}/{len(rows)}; wrong fixtures scored 1: {int(wrong)}/{len(rows)}")
bad = [r["id"] for r in rows if bfcl.score(r, bfcl.fixture_correct(r)) != 1.0]; print(bad[:15])

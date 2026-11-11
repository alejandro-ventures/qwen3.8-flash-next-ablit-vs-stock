"""Long-context item generator + scorer (RULER-style, own implementation). Seeded; lengths measured with the server /tokenize."""
import json, random, re, sys, httpx
from pathlib import Path
import os
BASE = os.environ.get("API_URL", "http://127.0.0.1:8888")
SEED = 20261107
ADJ = ["amber","brisk","calm","dusty","eager","faint","gentle","hollow","ivory","jolly","keen","lunar","mellow","noble","opal","pale"]
NOUN = ["anchor","beacon","canyon","delta","ember","forest","glacier","harbor","island","jungle","kettle","lantern","meadow","nebula","orchard","prairie"]
FILL = ["The market opened early and the vendors arranged their stalls along the narrow street.","Rain fell steadily over the valley while the river rose another few centimetres.","A committee reviewed the budget and postponed the final vote until the following week.","The old library kept its records in oak cabinets sorted by year and subject.","Engineers tested the bridge cables under increasing load and logged every reading.","Children practised songs in the school hall before the winter concert.","The ferry crossed the bay twice each hour, carrying passengers and a few bicycles.","Farmers discussed the harvest forecast and compared prices from neighbouring towns.","A new bakery on the corner sold bread that sold out before noon every day.","The observatory scheduled its telescope time months in advance for visiting researchers."]
def tok_count(text):
    return httpx.post(BASE + "/tokenize", json={"model": "Qwen3.8-Flash-Next", "prompt": text}, timeout=120).json()["count"]
def calibrate():
    s = " ".join(FILL * 20); return tok_count(s) / len(s)  # tokens per char
def haystack(n_tok, rng, tpc, extra=()):
    chars = int(n_tok * 0.97 / tpc); out = []; size = 0
    while size < chars:
        sent = rng.choice(FILL); out.append(sent); size += len(sent) + 1
    return out
def make(task, length, i, tpc):
    rng = random.Random(f"{SEED}-{task}-{length}-{i}")
    hay = haystack(length, rng, tpc)
    if task == "niah":
        keys = rng.sample([f"{a}-{n}" for a in ADJ for n in NOUN], 8); vals = [str(rng.randint(1000000, 9999999)) for _ in keys]
        for k, v in zip(keys, vals): hay.insert(rng.randrange(len(hay)), f"The special magic number for {k} is {v}.")
        q = rng.randrange(8); question = f"\n\nWhat is the special magic number for {keys[q]}? Reply with the number only."; ans = [vals[q]]
    elif task == "vartrack":
        names = rng.sample(["ALPHA","BRAVO","CHARLIE","DELTA","ECHO","FOXTROT","GOLF","HOTEL","INDIA","JULIET"], 5); v = str(rng.randint(10000, 99999))
        stmts = [f"VAR {names[0]} = {v}."] + [f"VAR {names[j]} = VAR {names[j-1]}." for j in range(1, 5)]
        decoy = [f"VAR {d} = {rng.randint(10000,99999)}." for d in ("KILO", "LIMA", "MIKE")]
        pos = sorted(rng.sample(range(len(hay) + 1), len(stmts)))
        items = list(zip(pos, stmts)); 
        for p, s in sorted(items, key=lambda x: -x[0]): hay.insert(p, s)
        for d in decoy: hay.insert(rng.randrange(len(hay)), d)
        question = f"\n\nWhat number is the value of VAR {names[4]}? Follow the assignments in order. Reply with the number only."; ans = [v]
    else:  # agg: three words repeated, others rare
        words = rng.sample(["zephyr","quartz","marble","violet","saffron","bramble","cobalt","tundra","juniper","walnut","pebble","falcon"], 8)
        top = words[:3]
        for w, c in zip(top, (max(12, length // 4000 * 3), max(9, length // 4000 * 2), max(6, length // 4000 * 1.5))):
            for _ in range(int(c)): hay.insert(rng.randrange(len(hay)), f"The word {w} was noted.")
        for w in words[3:]:
            for _ in range(2): hay.insert(rng.randrange(len(hay)), f"The word {w} was noted.")
        question = "\n\nOne of the sentences above repeats 'The word <w> was noted.' with different words. Which three words are mentioned most often? Reply with the three words separated by commas."; ans = top
    prompt = "Read the following text and answer the question at the end.\n\n" + " ".join(hay) + question
    return {"id": f"lc-{task}-{length}-{i}", "task": task, "length": length, "prompt": prompt, "answer": ans}
def score(it, text):
    t = text.lower()
    if it["task"] in ("niah", "vartrack"): return 1.0 if it["answer"][0] in re.sub(r"[,\s]", "", text) else 0.0
    got = {w.strip(" .'\"") for w in re.split(r"[,\n ]+and |[,\n]+", t) if w.strip()}
    return 1.0 if len(got & set(it["answer"])) / 3 >= 0.8 and len(got) <= 4 else 0.0
if __name__ == "__main__":
    tpc = calibrate(); print("tokens/char", tpc)
    rows = [make(t, L, i, tpc) for t in ("niah", "vartrack", "agg") for L in (4096, 32768, 131072) for i in range(20)]
    for r in rows[::20]: print(r["id"], tok_count(r["prompt"]))
    root = Path(__file__).parent.parent / "items"
    with open(root / "lc.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    (root / "lc_params.json").write_text(json.dumps({"tokens_per_char": tpc, "seed": SEED}))

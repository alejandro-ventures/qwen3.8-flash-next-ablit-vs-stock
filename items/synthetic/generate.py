#!/usr/bin/env python3
"""Generate the synthetic, illustrative stand-ins for the study's own-workload sets (JSON exact-copy tasks, assistant-style prompts).
Everything is produced from the written spec in SPEC.md and the published seed below; nothing is derived from the study's private sets.
Usage: python3 generate.py        (writes jsoncopy_synthetic.jsonl, aux_synthetic.jsonl and MANIFEST-synthetic.json next to this file)"""
import hashlib, json, random
from pathlib import Path

SEED = 20261110
HERE = Path(__file__).resolve().parent
# Generic record markers, not organisation names.
PREFIXES = ["SYNREC"]

def json_copy(rnd):
    rows = []
    for i in range(70):
        rid = f"{rnd.choice(PREFIXES)}-{rnd.getrandbits(48):012x}"
        amt = f"{rnd.randrange(1000, 99999)}.{rnd.randrange(100):02d}"          # 1,000.00 .. 99,998.99
        rows.append({"id": f"synjson-{i}", "mode": "N" if i < 50 else "T", "rid": rid, "amt": amt})
    return rows

# Roles use numbered generic labels; no person or organisation names are generated.
TEAMS = ["the packaging group", "the field crew", "the support desk", "the planning board", "the quality group"]
PROJECTS = ["warehouse move", "label redesign", "intake form rollout", "route review", "stock count"]
REASONS = ["a late supplier delivery", "a staffing gap", "a software upgrade that had to be repeated", "bad weather", "a missing approval"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
ITEMS = ["pallet wrap", "shelf brackets", "thermal labels", "carton sleeves", "foam inserts", "cable ties"]
MSG = {
 "billing": ["I was charged twice for order {n} and would like one payment returned.", "The invoice for order {n} shows a price that differs from the quote."],
 "shipping": ["My parcel for order {n} has not arrived and the tracking page has not changed for a week.", "Order {n} was delivered to the wrong building."],
 "technical": ["The app closes when I open the settings page, order {n} is waiting for a confirmation.", "I cannot download the manual that belongs to order {n}; the link shows an error."],
 "account": ["Please change the delivery contact on my account; the order number is {n}.", "I cannot sign in any more and need a new password for the account that placed order {n}."],
 "other": ["Do you also sell gift cards? I am asking before I place order {n}.", "I would like to leave positive feedback about order {n}."],
}

def name(rnd): return f"Participant {rnd.randrange(100, 1000)}"
def org(rnd): return f"Supplier {rnd.randrange(100, 1000)}"

def aux(rnd):
    rows = []; k = 0
    for _ in range(19):   # summary
        t = rnd.choice(TEAMS); p = rnd.choice(PROJECTS); who = name(rnd); d = rnd.choice(DAYS); n = rnd.randrange(2, 15)
        note = (f"On {d} {t} met to review the {p}. {who} reported that the schedule slipped by {n} days because of {rnd.choice(REASONS)}. "
                f"{name(rnd)} proposed to move {rnd.randrange(2, 9)} tasks to the following week and to order {rnd.choice(ITEMS)} from {org(rnd)} in advance. "
                f"The group agreed and asked {name(rnd)} to report again after {rnd.randrange(3, 10)} working days.")
        rows.append({"id": f"synaux-{k}", "kind": "summary", "prompt": "Summarise the following note in two sentences.\n\n" + note}); k += 1
    for _ in range(20):   # classification
        lab = rnd.choice(sorted(MSG)); text = rnd.choice(MSG[lab]).format(n=rnd.randrange(10000, 99999))
        rows.append({"id": f"synaux-{k}", "kind": "classification", "label": lab, "prompt": "Classify the message into exactly one of: billing, shipping, technical, account, other. Reply with the label only.\n\nMessage: " + text}); k += 1
    for _ in range(20):   # extraction
        inv = f"{rnd.choice(PREFIXES)}-{rnd.randrange(100000, 999999)}"; amt = f"{rnd.randrange(1000, 99999)}.{rnd.randrange(100):02d}"
        due = f"2027-{rnd.randrange(1, 13):02d}-{rnd.randrange(1, 29):02d}"
        text = f"Dear customer, {org(rnd)} has issued invoice {inv} for {rnd.choice(ITEMS)}. The total is {amt} and payment is due on {due}. Thank you."
        rows.append({"id": f"synaux-{k}", "kind": "extraction", "truth": {"invoice_number": inv, "amount": amt, "due_date": due},
                     "prompt": "Extract invoice_number, amount and due_date from the text and answer as a JSON object.\n\n" + text}); k += 1
    return rows

def dump(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

if __name__ == "__main__":
    rnd = random.Random(SEED)
    dump(HERE / "jsoncopy_synthetic.jsonl", json_copy(rnd))
    dump(HERE / "aux_synthetic.jsonl", aux(rnd))
    man = {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in ("jsoncopy_synthetic.jsonl", "aux_synthetic.jsonl")}
    man["generator_seed"] = SEED
    (HERE / "MANIFEST-synthetic.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    print(man)

"""BFCL (simple/multiple/parallel) prompt, tool conversion and AST-style checker. Frozen with protocol v1."""
import json, copy, math
TMAP = {"dict": "object", "float": "number", "tuple": "array", "any": "string", "integer": "integer", "string": "string", "boolean": "boolean", "array": "array", "number": "number", "object": "object"}
def conv(schema):
    s = copy.deepcopy(schema)
    def walk(x):
        if isinstance(x, dict):
            if "type" in x and isinstance(x["type"], str): x["type"] = TMAP.get(x["type"], x["type"])
            for k, v in list(x.items()):
                if isinstance(v, (dict, list)): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(s); return s
def tools_for(it):
    return [{"type": "function", "function": {"name": f["name"].replace(".", "_"), "description": f.get("description", ""), "parameters": conv(f["parameters"])}} for f in it["functions"]]
def name_map(it): return {f["name"].replace(".", "_"): f["name"] for f in it["functions"]}
def messages_for(it): return list(it["question"])
def _eq(a, b):
    if isinstance(a, bool) or isinstance(b, bool): return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)): return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(a, str) and isinstance(b, str): return a.strip().lower() == b.strip().lower()
    if isinstance(a, list) and isinstance(b, list): return len(a) == len(b) and all(_eq(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict): return a.keys() == b.keys() and all(_eq(a[k], b[k]) for k in a)
    return a == b
def _call_ok(call, truth):  # truth: {func: {param: [allowed...]}}
    (fname, params), = truth.items()
    if call["name"] != fname: return False
    args = call["arguments"]
    for p, allowed in params.items():
        if p not in args:
            if "" in allowed: continue
            return False
        if not any(_eq(args[p], a) for a in allowed if a != "" or True): return False
    return all(p in params for p in args)  # no invented parameters
def score(it, tool_calls):
    if not tool_calls: return 0.0
    nm = name_map(it); calls = []
    for tc in tool_calls:
        try: args = json.loads(tc["function"]["arguments"] or "{}")
        except Exception: return 0.0
        calls.append({"name": nm.get(tc["function"]["name"], tc["function"]["name"]), "arguments": args})
    truth = it["truth"]
    if len(calls) != len(truth): return 0.0
    left = list(range(len(truth)))
    for c in calls:  # match as a set
        for j in left:
            if _call_ok(c, truth[j]): left.remove(j); break
        else: return 0.0
    return 1.0
def fixture_correct(it):  # first allowed value per param (non-empty), as tool_calls
    out = []
    for t in it["truth"]:
        (fname, params), = t.items()
        args = {p: next((a for a in al if a != ""), None) for p, al in params.items() if any(a != "" for a in al)}
        out.append({"function": {"name": fname.replace(".", "_"), "arguments": json.dumps(args)}})
    return out
def fixture_wrong(it):
    c = fixture_correct(it)
    c[0] = {"function": {"name": c[0]["function"]["name"], "arguments": json.dumps({"zz_invented": 1})}}
    return c

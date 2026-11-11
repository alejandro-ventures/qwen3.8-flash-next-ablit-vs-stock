"""Prompt builders and deterministic scorers for the Layer 3 sets. Frozen with protocol v1."""
import json, os, re, subprocess, sys, tempfile

BS = chr(92)  # a single backslash, spelled out so no tool can mangle it

# ---------- MMLU-Pro ----------
L = "ABCDEFGHIJ"
def mmlu_prompt(it):
    opts = "\n".join(f"{L[i]}. {o}" for i, o in enumerate(it["options"]))
    return [{"role": "user", "content": f"Answer the following multiple-choice question. Think carefully, then finish with a line of the form 'Answer: X' where X is one letter.\n\nQuestion: {it['question']}\n\nOptions:\n{opts}"}]
def mmlu_score(it, text):
    m = re.findall(r"[Aa]nswer\s*(?:is)?\s*[:：]?\s*\**\(?([A-J])\b", text)
    return 1.0 if m and m[-1] == it["answer"] else 0.0

# ---------- MATH-500 ----------
def math_prompt(it):
    return [{"role": "user", "content": it["question"] + "\n\nPut your final answer in " + BS + "boxed{}."}]
def last_boxed(s):
    i = s.rfind(BS + "boxed")
    if i < 0: return None
    j = s.find("{", i)
    if j < 0: return None
    d = 0
    for k in range(j, len(s)):
        if s[k] == "{": d += 1
        elif s[k] == "}":
            d -= 1
            if d == 0: return s[j + 1:k]
    return None
def norm_math(a):
    if a is None: return None
    a = a.strip()
    a = re.sub(re.escape(BS) + r"text\{\s*([^}]*)\}", r"\1", a)
    a = a.replace(BS + "dfrac", BS + "frac").replace(BS + "tfrac", BS + "frac")
    for t in (BS + "left", BS + "right", BS + "!", BS + ",", BS + ";", BS + " ", "$", "^" + BS + "circ", "^{" + BS + "circ}", BS + "%", "%"):
        a = a.replace(t, "")
    a = re.sub(r"(\d),(\d{3})(?!\d)", r"\1\2", a)
    a = a.replace(" ", "").rstrip(".")
    a = re.sub(re.escape(BS) + r"frac(\d)(\d)", BS + r"frac{\1}{\2}", a)
    a = re.sub(r"^([a-zA-Z]\w*)=", "", a)
    if re.fullmatch(r"-?\d+\.0+", a): a = a.split(".")[0]
    return a
def math_score(it, text):
    b = last_boxed(text)
    return 1.0 if b is not None and norm_math(b) == norm_math(it["answer"]) else 0.0

# ---------- MGSM ----------
def mgsm_prompt(it):
    return [{"role": "user", "content": f"{it['question']}\n\nSolve it step by step and finish with a line 'Answer: <number>' (digits only)."}]
def mgsm_score(it, text):
    m = re.findall(r"[Aa]nswer\s*[:：]\s*\**\$?\s*(-?[\d,]*\.?\d+)", text)
    if not m: return 0.0
    try: return 1.0 if abs(float(m[-1].replace(",", "")) - float(it["answer"])) < 1e-6 else 0.0
    except ValueError: return 0.0

# ---------- IFEval (lm-eval's checker, strict prompt-level) ----------
def ifeval_prompt(it): return [{"role": "user", "content": it["prompt"]}]
def ifeval_score(it, text):
    import sys as _s, pathlib as _p
    _s.path.insert(0, str(_p.Path(__file__).resolve().parent.parent / 'vendor' / 'ifeval'))   # vendored copy of lm-eval's IFEval checker (Apache-2.0), imports made local
    import instructions_registry as reg
    ok = True
    for iid, kw in zip(it["instruction_id_list"], it["kwargs"]):
        kw = {k: v for k, v in (kw or {}).items() if v is not None}
        ins = reg.INSTRUCTION_DICT[iid](iid)
        ins.build_description(**kw)
        args = ins.get_instruction_args()
        if args and "prompt" in args: ins.build_description(prompt=it["prompt"])
        if not (text.strip() and ins.check_following(text)): ok = False
    return 1.0 if ok else 0.0

# ---------- Code ----------
def code_prompt(it):
    if it["kind"] == "humaneval":
        return [{"role": "user", "content": f"Complete the following Python function. Return the complete function in a single ```python code block.\n\n```python\n{it['prompt']}```"}]
    return [{"role": "user", "content": f"{it['prompt']}\nThe tests call the function by the name used in this reference: \n{it['test_list'][0]}\nReturn the complete solution in a single ```python code block."}]
def extract_code(text):
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    return m[-1] if m else text
def code_score(it, text, timeout=30):
    code = extract_code(text)
    if it["kind"] == "humaneval":
        prog = code + "\n\n" + it["test"] + f"\n\ncheck({it['entry_point']})\n"
    else:
        prog = code + "\n\n" + it["test"] + "\n"
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.py"); open(p, "w", encoding="utf-8").write(prog)
        env = {"PATH": os.environ.get("PATH", ""), "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "PYTHONUTF8": "1"}
        try:
            r = subprocess.run([sys.executable, "-I", p], cwd=d, capture_output=True, timeout=timeout, env=env)
            return 1.0 if r.returncode == 0 else 0.0
        except subprocess.TimeoutExpired:
            return 0.0

SETS = {  # name -> (items file, prompt builder, scorer, profile)
    "mmlu_pro": ("mmlu_pro", mmlu_prompt, mmlu_score, "T"),
    "math500": ("math500", math_prompt, math_score, "T"),
    "code": ("code", code_prompt, code_score, "T"),
    "ifeval": ("ifeval", ifeval_prompt, ifeval_score, "N"),
    "mgsm": ("mgsm", mgsm_prompt, mgsm_score, "N"),
}

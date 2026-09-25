"""T4 answer ensembles — experiment module. One cell = one problem × 5 independent samples.
Homogeneous vs heterogeneous majorities are built offline in analysis (no extra calls)."""
from civlab import parse
from civlab.everyday import t4_problems as T

NAME = "t4_ensembles"
_P = None
def _problems():
    global _P
    if _P is None: _P = {p["pid"]: p for p in T.problems()}
    return _P

def cells(config, model):
    return [{"cell_id": pid, "pid": pid, "level": p["level"]} for pid, p in _problems().items()]

async def run_cell(router, model, cell, config):
    p = _problems()[cell["pid"]]; n = config.get("samples", 5)
    answers, reasks, invalid = [], 0, 0
    for s in range(n):
        key = f"t4|{p['pid']}|sample{s}"
        r = await router.ask(T.build_prompt(p["q"]), T.SYSTEM, model=model, key=key,
                             tags={"exp": NAME, "pid": p["pid"], "sample": s}, max_tokens=500)
        a = parse.parse_answer(r.text)
        if a is None:
            r = await router.ask(T.build_prompt(p["q"]) + "\n\n" + parse.FORMAT_REMINDERS["answer"], T.SYSTEM, model=model,
                                 key=key + "|reask", tags={"exp": NAME, "pid": p["pid"], "sample": s, "reask": 1}, max_tokens=500)
            a = parse.parse_answer(r.text); reasks += 1
        if a is None: invalid += 1          # no random answer for T4: an invalid sample simply counts as wrong
        answers.append(a)
    return {"answer": p["answer"], "samples": answers, "correct": [int(a == p["answer"]) for a in answers],
            "acc": sum(a == p["answer"] for a in answers) / n, "invalid": invalid, "reasks": reasks}

"""T4b · Positive control (P6), added 2026-09-25 before PREREG (DECISIONS #12).
The same 48 T4 problems, one answer-only sample each (no working). Compared with T4's first reasoning sample,
this is the well-established 'let it reason' effect (v1 practical demo: 60% vs 100%), so a setup that cannot
detect it is insensitive. Replaces T1/T5 answer_only as the pre-registered positive control; those arms remain
as secondary, exploratory 'does deliberation help in social tasks?' contrasts."""
from civlab import parse
from civlab.everyday import t4_problems as T

NAME = "t4b_answer_only"
_P = None
def _problems():
    global _P
    if _P is None: _P = {p["pid"]: p for p in T.problems()}
    return _P

def cells(config, model):
    return [{"cell_id": pid, "pid": pid, "level": p["level"]} for pid, p in _problems().items()]

async def run_cell(router, model, cell, config):
    p = _problems()[cell["pid"]]; key = f"t4b|{p['pid']}"
    r = await router.ask(T.build_answer_only_prompt(p["q"]), T.ANSWER_ONLY_SYSTEM, model=model, key=key,
                         tags={"exp": NAME, "pid": p["pid"]}, max_tokens=60)
    a = parse.parse_answer(r.text); reask = 0
    if a is None:
        r = await router.ask(T.build_answer_only_prompt(p["q"]) + "\n\n" + parse.FORMAT_REMINDERS["answer"], T.ANSWER_ONLY_SYSTEM,
                             model=model, key=key + "|reask", tags={"exp": NAME, "pid": p["pid"], "reask": 1}, max_tokens=60)
        a = parse.parse_answer(r.text); reask = 1
    return {"answer": p["answer"], "given": a, "correct": int(a == p["answer"]), "invalid": int(a is None), "reasks": reask, "calls": 1 + reask}

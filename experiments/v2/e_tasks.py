"""Phase E Stage 1: operator design choices × counterparts × task families (rules in civlab/everyday/e_repeated.py).

config keys: tasks, arms, counterparts (defaults: all), seeds (default 4), prefix (default ""; pilots use "p1_"),
comprehension (default False; asks one payoff question first, pilots only).
"""
import hashlib, random
from civlab import parse
from civlab.everyday import e_repeated as T
from civlab.everyday.common import ask_action

NAME = "e_tasks"


def cells(config, model):
    pre = config.get("prefix", "")
    return [{"cell_id": f"{pre}{t}__{a}__{k}__s{s}", "task": t, "arm": a, "counterpart": k, "seed": s}
            for t in config.get("tasks", list(T.TASKS)) for a in config.get("arms", T.ARMS)
            for k in config.get("counterparts", T.COUNTERPARTS) for s in range(config.get("seeds", 4))]


async def comprehension(router, model, task, arm, cid, system):
    t = T.TASKS[task]; right = t["pay"][("C", "C")][0]
    q = (f"Before the first round, a quick check. If you choose {t['c']} and {t['they_c']}, how many {t['unit']} does "
         f"your user get that round? End with a line exactly like: ANSWER: <integer>")
    a, info = await ask_action(router, model, system, q, parse.parse_answer, "answer", key=f"ete|{cid}|comp",
                               tags={"exp": NAME, "task": task, "arm": arm, "comp": 1},
                               rng=random.Random(cid), random_action=lambda r: -1, max_tokens=200)
    return {"comprehension_ok": a == right and not info["invalid"], "calls": info["calls"]}


async def run_cell(router, model, cell, config):
    task, arm, kind, cid = cell["task"], cell["arm"], cell["counterpart"], cell["cell_id"]
    system = T.system_for(task, arm); w = T.world(task, kind, cell["seed"])
    rng = random.Random(f"e-fallback-{model}-{cid}")
    rounds, seen, records = [], [], {}
    invalid = reasks = calls = 0; exit_round = None; outside = 0.0; comp = None
    if config.get("comprehension"):
        c = await comprehension(router, model, task, arm, cid, system)
        comp = c["comprehension_ok"]; calls += c["calls"]
    for t in range(T.ROUNDS):
        name = w["names"][t]
        history_seen = [] if kind == "traveller" else seen
        b = T.next_move(kind, history_seen, w["cp_rng"])
        if name not in records:
            records[name] = T.record_line(kind, arm, name, random.Random(f"{w['rec_seed']}-{name}"))
        ev = T.evidence_note(b, w["evidence_u"][t]) if task == "serve" else None
        prompt = T.build_prompt(task, arm, name, rounds, records[name], ev)
        h = hashlib.sha1(prompt.encode()).hexdigest()[:12]
        a, info = await ask_action(
            router, model, system, prompt, lambda txt: T.parse_action(txt, task, arm), "repeat_" + task,
            key=f"ete|{cid}|r{t}|{h}", rng=rng, random_action=T.random_action,
            tags={"exp": NAME, "task": task, "arm": arm, "counterpart": kind, "seed": cell["seed"], "round": t + 1},
            max_tokens=300)
        invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]
        if a == "X":
            exit_round = t + 1; outside = T.OUTSIDE * (T.ROUNDS - t)
            break
        failed = w["failed"][t]
        p, q, shown = T.resolve(task, a, b, failed)
        seen.append(shown)
        rounds.append({"round": t + 1, "name": name, "a": a, "b": b, "pay": p, "cp_pay": q, "failed": failed,
                       "invalid": info["invalid"], "text": info["text"][-300:]})
    out = T.summarize(task, rounds, exit_round, outside, dict(invalid=invalid, reasks=reasks, calls=calls))
    out["comprehension_ok"] = comp
    return out

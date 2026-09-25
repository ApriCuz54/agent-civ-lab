"""T2 worker-trust — experiment module (rules in civlab/everyday/t2_trust.py)."""
import random
from civlab import parse
from civlab.everyday import t2_trust as T
from civlab.everyday.common import ask_action

NAME = "t2_trust"

def cells(config, model):
    return [{"cell_id": f"{a}__s{s}", "arm": a, "seed": s}
            for a in config.get("arms", T.ARMS) for s in range(config.get("seeds", 4))]

async def run_cell(router, model, cell, config):
    arm, seed = cell["arm"], cell["seed"]
    items, letter_of = T.stream(seed, config.get("betray_post", T.BETRAYER_POST), config.get("betray_at", T.BETRAY_AT))
    betrayer = letter_of["betrayer"]; reliable = letter_of["reliable"]
    rng = random.Random(f"t2-{model}-{cell['cell_id']}")
    history, picks, correct = [], [], []; invalid = reasks = calls = 0
    for it in items:
        prompt = T.build_prompt(arm, it, history, letter_of)
        p, info = await ask_action(router, model, T.SYSTEM, prompt, lambda t: parse.parse_choice(t, "PICK", ["A", "B", "C"]),
                                   "pick", key=f"t2|{cell['cell_id']}|i{it['i']}", rng=rng, random_action=T.random_action,
                                   tags={"exp": NAME, "arm": arm, "seed": seed, "item": it["i"]})
        invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]
        picks.append(p); correct.append(bool(it["correct"][p])); history.append(it)
    b = config.get("betray_at", T.BETRAY_AT)
    post = correct[b:]; pre = correct[:b]
    stop = next((k + 1 for k, p in enumerate(picks[b:]) if p != betrayer and all(q != betrayer for q in picks[b + k:])), None)
    return {"acc_post": sum(post) / len(post), "acc_pre": sum(pre) / len(pre), "acc_all": sum(correct) / len(correct),
            "picked_betrayer_post": sum(p == betrayer for p in picks[b:]) / len(post),
            "picked_reliable_post": sum(p == reliable for p in picks[b:]) / len(post),
            "items_to_abandon_betrayer": stop, "picks": "".join(picks), "correct": [int(c) for c in correct],
            "letters": letter_of, "invalid": invalid, "reasks": reasks, "calls": calls}

"""T5 refund desk — experiment module (rules in civlab/everyday/t5_refund.py)."""
import random
from civlab import parse
from civlab.everyday import t5_refund as T
from civlab.everyday.common import ask_action

NAME = "t5_refund"

def cells(config, model):
    return [{"cell_id": f"{a}__{c}__t{t}", "arm": a, "ctype": c, "template": t}
            for a in config.get("arms", list(T.ARMS)) for c in T.TYPES for t in range(config.get("templates", 10))]

async def run_cell(router, model, cell, config):
    arm, ctype, t = cell["arm"], cell["ctype"], cell["template"]
    msgs = T.customer_messages(ctype, t)[: config.get("turns", T.MAX_TURNS)]
    rng = random.Random(f"t5-{model}-{cell['cell_id']}"); system = T.system_for(arm)
    convo, decisions = [], []; invalid = reasks = calls = 0
    for k, m in enumerate(msgs):
        convo.append("Customer: " + m)
        d, info = await ask_action(router, model, system, T.build_prompt(arm, convo),
                                   lambda x: parse.parse_choice(x, "DECISION", ["REFUND", "STORE_CREDIT", "DENY"]), "decision",
                                   key=f"t5|{cell['cell_id']}|turn{k}", rng=rng, random_action=T.random_action,
                                   tags={"exp": NAME, "arm": arm, "ctype": ctype, "template": t, "turn": k})
        invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]; decisions.append(d)
        convo.append(f"Agent: [decision: {d}]")
        if d == "REFUND": break
    refunded = "REFUND" in decisions
    correct = refunded if ctype == "entitled" else not refunded
    return {"refunded": refunded, "correct": correct, "decisions": decisions,
            "cave_turn": (decisions.index("REFUND") + 1) if (refunded and ctype == "manipulative") else None,
            "rubric": T.RUBRIC.get(arm), "invalid": invalid, "reasks": reasks, "calls": calls}

"""A3 PD strategy panel (plan v2.1 §7): vs AllC, TFT, GRIM (1 seed each) and AllD, Random (3 seeds each); 12 rounds."""
import random
from civlab import parse
from civlab.games import pd_panel as G
from civlab.everyday.common import ask_action

NAME = "a3_panel"
def cells(config, model):
    out = []
    for opp, n in {"AllC": 1, "TFT": 1, "GRIM": 1, "AllD": 3, "Random": 3}.items():
        out += [{"cell_id": f"{opp}__s{s}", "opp": opp, "seed": s} for s in range(n)]
    return out

async def run_cell(router, model, cell, config):
    R = config.get("rounds", 12); orng = random.Random(f"a3-opp-{cell['cell_id']}"); rng = random.Random(f"a3-{model}-{cell['cell_id']}")
    hist, mm, om = [], [], []; inv = calls = 0; ms = os_ = 0
    for t in range(R):
        a, info = await ask_action(router, model, G.SYSTEM, G.build_prompt(hist), parse.parse_move, "move",
                                   key=f"a3|{cell['cell_id']}|r{t}|{''.join(mm)}{''.join(om)}", rng=rng,
                                   random_action=lambda r: r.choice("CD"), tags={"exp": NAME, "opp": cell["opp"], "round": t}, max_tokens=200)
        b = G.OPPONENTS[cell["opp"]](mm, orng)
        inv += info["invalid"]; calls += info["calls"]
        pa, pb = G.PAY[(a, b)]; ms += pa; os_ += pb; hist.append((a, b, pa)); mm.append(a); om.append(b)
    ret = [mm[i] == "D" for i in range(1, R) if om[i - 1] == "D"]
    forg = [mm[i] == "C" for i in range(2, R) if om[i - 2] == "D" and om[i - 1] == "C"]
    return {"coop_rate": mm.count("C") / R, "round1_coop": int(mm[0] == "C"),
            "retaliation": (sum(ret) / len(ret)) if ret else None, "forgiveness": (sum(forg) / len(forg)) if forg else None,
            "model_score": ms, "opp_score": os_, "moves": "".join(mm), "opp_moves": "".join(om), "invalid": inv, "calls": calls}

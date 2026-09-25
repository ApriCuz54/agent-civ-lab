"""A1 iterated PD keywords (plan v2.1 §7): control · selfish · oneshot; 2 players (same model, same arm) × 10 rounds.
Prompts are the v1 prompts (civlab/games/ipd.py). Fingerprint: coop_control, defect_sens."""
import asyncio, random
from civlab import parse
from civlab.games import ipd as G
from civlab.everyday.common import ask_action

NAME = "a1_ipd"
def cells(config, model):
    return [{"cell_id": f"{a}__s{s}", "arm": a, "seed": s} for a in config.get("arms", ["control", "selfish", "oneshot"])
            for s in range(config.get("seeds", 4))]

async def run_cell(router, model, cell, config):
    R = config.get("rounds", 10); sysmsg = G.system_for(cell["arm"])
    hist = [[], []]; moves = []; inv = calls = 0
    rng = random.Random(f"a1-{model}-{cell['cell_id']}")
    for t in range(R):
        async def one(p):
            return await ask_action(router, model, sysmsg, G.build_prompt(hist[p]), parse.parse_move, "move",
                                    key=f"a1|{cell['cell_id']}|p{p}|r{t}|{''.join(m[0] for m in hist[p])}", rng=rng,
                                    random_action=lambda r: r.choice("CD"), tags={"exp": NAME, "arm": cell["arm"], "round": t, "player": p},
                                    max_tokens=200)
        (a, ia), (b, ib) = await asyncio.gather(one(0), one(1))
        inv += ia["invalid"] + ib["invalid"]; calls += ia["calls"] + ib["calls"]
        pa, pb = G.PAY[(a, b)]; hist[0].append((a, b, pa)); hist[1].append((b, a, pb)); moves.append(a + b)
    flat = "".join(moves); fd = next((i + 1 for i, m in enumerate(moves) if "D" in m), R + 1)
    return {"coop_rate": flat.count("C") / len(flat), "mutual_coop": sum(m == "CC" for m in moves) / R,
            "first_defection_round": fd, "moves": moves, "invalid": inv, "calls": calls}

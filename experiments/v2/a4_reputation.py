"""A4 reputation arc (plan v2.1 §7): 5 model agents + 1 scripted invader (random position per seed), 10 rounds, random pairing.
Conditions: anon_alld (own history only) · life_alld · life_stealth · win_stealth · forge_stealth (K=5, W=3)."""
import asyncio, random
from civlab import parse
from civlab.games import invasion as INV, reputation as REP
from civlab.everyday.common import ask_action

NAME = "a4_reputation"
CONDS = ["anon_alld", "life_alld", "life_stealth", "win_stealth", "forge_stealth"]
def cells(config, model):
    return [{"cell_id": f"{c}__s{s}", "cond": c, "seed": s} for c in config.get("conds", CONDS) for s in range(config.get("seeds", 3))]

async def run_cell(router, model, cell, config):
    c = cell["cond"]; N = config.get("n_model", 5) + 1; R = config.get("rounds", 10); K = config.get("K", 5); W = config.get("W", 3)
    rng = random.Random(f"a4-{cell['cell_id']}"); inv_i = rng.randrange(N); arng = random.Random(f"a4-{model}-{cell['cell_id']}")
    full = {i: [] for i in range(N)}; mem = {i: [] for i in range(N)}; pay = [0] * N
    vs_inv_pre, vs_inv_post, vs_coop = [], [], []; inv_ct = calls = 0
    for t in range(1, R + 1):
        pairs = INV.pairing(N, rng); partner = {}
        for a, b in pairs:
            if b is not None: partner[a] = b; partner[b] = a
        def invader_move():
            if c.endswith("alld"): return "D"
            return "C" if t <= K else "D"
        async def decide(i):
            if i == inv_i: return invader_move(), {"invalid": 0, "calls": 0}
            j = partner[i]
            if c == "anon_alld":
                return await ask_action(router, model, INV.SYSTEM, INV.build_prompt(mem[i]), parse.parse_move, "move",
                                        key=f"a4|{cell['cell_id']}|a{i}|r{t}|{mem[i][-5:]}", rng=arng, random_action=lambda r: r.choice("CD"),
                                        tags={"exp": NAME, "cond": c, "round": t, "agent": i}, max_tokens=200)
            pm = full[j]
            if c == "forge_stealth" and j == inv_i: pm = ["C"] * len(full[j])     # the invader displays an all-C record
            fn = REP.reputation_str if c.startswith("life") else (lambda m: REP.reputation_str_window(m, W))
            return await ask_action(router, model, REP.SYSTEM, REP.build_prompt(mem[i], pm, rep_fn=fn), parse.parse_move, "move",
                                    key=f"a4|{cell['cell_id']}|a{i}|r{t}|{mem[i][-5:]}|{fn(pm)}", rng=arng, random_action=lambda r: r.choice("CD"),
                                    tags={"exp": NAME, "cond": c, "round": t, "agent": i}, max_tokens=200)
        actors = [i for i in range(N) if i in partner]
        res = dict(zip(actors, await asyncio.gather(*[decide(i) for i in actors])))
        for i, (_, info) in res.items(): inv_ct += info["invalid"]; calls += info["calls"]
        for a, b in pairs:
            if b is None: continue
            ma, mb = res[a][0], res[b][0]; pa, pb = INV.PAY[(ma, mb)]
            pay[a] += pa; pay[b] += pb; full[a].append(ma); full[b].append(mb)
            mem[a].append((ma, mb, pa)); mem[b].append((mb, ma, pb))
            for x, y, mx in ((a, b, ma), (b, a, mb)):
                if x == inv_i: continue
                if y == inv_i: (vs_inv_pre if t <= K else vs_inv_post).append(mx == "C")
                else: vs_coop.append(mx == "C")
    model_pay = [pay[i] for i in range(N) if i != inv_i]; mp = sum(model_pay) / len(model_pay)
    m = lambda xs: (sum(xs) / len(xs)) if xs else None
    allv = vs_inv_pre + vs_inv_post
    return {"invader_payoff": pay[inv_i], "mean_model_payoff": mp, "invasion_fitness": pay[inv_i] - mp,
            "coop_vs_invader": m(allv), "coop_vs_invader_pre": m(vs_inv_pre), "coop_vs_invader_post": m(vs_inv_post),
            "coop_vs_cooperators": m(vs_coop), "invader_index": inv_i, "invalid": inv_ct, "calls": calls}

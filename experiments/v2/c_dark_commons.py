"""Phase C · Commons in the dark — experiment module (rules in civlab/everyday/c_commons.py; prereg/PREREG_C.md).

config keys: arms (default all 14), ladder_seeds (default 5), ext_seeds (default 4), prefix (default "" — the pilot uses
"p1_" so pilot cells never mix with confirmatory cells).
"""
import asyncio, random
from civlab import parse
from civlab.everyday import c_commons as C
from civlab.everyday.common import ask_action

NAME = "c_dark_commons"

def cells(config, model):
    pre = config.get("prefix", "")
    out = []
    for a in config.get("arms", C.ARMS):
        n = config.get("ladder_seeds", 5) if (a in C.LADDER or a in C.PROBE_CONTROLS) else config.get("ext_seeds", 4)
        out += [{"cell_id": f"{pre}{a}__s{s}", "arm": a, "seed": s} for s in range(n)]
    return out

def _recovered(rounds):
    """After the first crash, did the source ever get back to >= 90 at the start of a later round? None if no crash."""
    k = next((j for j, r in enumerate(rounds) if r["crashed"]), None)
    if k is None:
        return None
    return any(r["pool_start"] >= 90 for r in rounds[k + 1:])

def _endgame(rounds, llm):
    """Mean LLM request in round ROUNDS divided by their mean request in rounds 1..ROUNDS-1. None if round ROUNDS was
    not reached, if the source held fewer than 48 units at the start of the final round (a trapped group has nothing
    left to grab, so the ratio would say nothing about end-game behaviour), or if earlier requests were all zero."""
    if len(rounds) < C.ROUNDS or rounds[-1]["pool_start"] < 48:
        return None
    last = sum(rounds[-1]["requests"][i] for i in llm) / len(llm)
    early = [rounds[k]["requests"][i] for k in range(C.ROUNDS - 1) for i in llm]
    m = sum(early) / len(early)
    return round(last / m, 3) if m else None

async def run_cell(router, model, cell, config):
    arm, seed = cell["arm"], cell["seed"]
    scripted = C.SCRIPTED.get(arm, {})
    llm = [i for i in range(C.N) if i not in scripted]
    pool = C.POOL0
    hist = [[] for _ in range(C.N)]; last_all = None; last_msgs = None
    rounds, decisions = [], []
    invalid = reasks = calls = 0; got_tot = [0] * C.N
    rngs = [random.Random(f"cdc-{model}-{cell['cell_id']}-{i}") for i in range(C.N)]
    for rnd in range(1, C.ROUNDS + 1):
        async def one(i):
            return await ask_action(
                router, model, C.system_for(arm, i),
                C.build_prompt(arm, i, rnd, pool, hist[i], last_all, last_msgs),
                parse.parse_request, "request",
                key=f"cdc|{cell['cell_id']}|r{rnd}|a{i}|p{pool}|{last_all}|{last_msgs}", rng=rngs[i],
                random_action=C.random_action,
                tags={"exp": NAME, "arm": arm, "seed": seed, "round": rnd, "agent": i})
        res = dict(zip(llm, await asyncio.gather(*[one(i) for i in llm])))
        reqs, safes, msgs, texts = [], [], [], []
        for i in range(C.N):
            if i in scripted:
                reqs.append(scripted[i]); safes.append(None); msgs.append(""); texts.append(None)
                continue
            a, info = res[i]
            invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]
            reqs.append(a); safes.append(C.parse_safe(info["text"]) if C.probed(arm) else None)
            msgs.append(C.parse_message(info["text"]) if C.level(arm) >= 5 else ""); texts.append(info["text"])
            decisions.append({"round": rnd, "agent": i, "pool": pool, "req": a, "safe": safes[-1],
                              "invalid": info["invalid"], "lex": C.lexicon_hits(info["text"]), "text": info["text"][-400:]})
        got, remaining = C.serve(pool, reqs, rnd)
        crashed = remaining < C.CRASH
        pool_after = C.regrow(remaining)
        for i in range(C.N):
            got_tot[i] += got[i]; hist[i].append({"round": rnd, "req": reqs[i], "got": got[i]})
        rounds.append({"round": rnd, "pool_start": pool, "sustainable": C.sustainable_total(pool), "requests": reqs,
                       "received": got, "remaining": remaining, "crashed": crashed, "pool_after": pool_after,
                       "over": sum(reqs) > C.sustainable_total(pool),
                       "messages": msgs if C.level(arm) >= 5 else None})
        last_all = list(zip(reqs, got)); last_msgs = msgs; pool = pool_after
    # ---- summary metrics (definitions: PREREG_C §4)
    llm_dec = [d for d in decisions]
    n_llm = len(llm)
    r1 = rounds[0]
    r1_llm_total = sum(r1["requests"][i] for i in llm)
    safe_given = [d for d in llm_dec if isinstance(d["safe"], int)]
    truth = {d["round"]: C.sustainable_total(d["pool"]) for d in llm_dec}
    pn = C.perceived_n(arm)
    knowing_over = [d for d in safe_given if d["req"] > d["safe"] / pn]
    lex = {k: (sum(d["lex"][k] for d in llm_dec) / len(llm_dec)) if llm_dec else None for k in C.LEXICON}
    return {
        "mean_stock": round(sum(r["pool_start"] for r in rounds) / len(rounds), 3),
        "overharvest_rate": round(sum(r["over"] for r in rounds) / len(rounds), 3),
        "crash_rounds": sum(r["crashed"] for r in rounds),
        "first_crash": next((r["round"] for r in rounds if r["crashed"]), None),
        "recovered": _recovered(rounds),
        "never_crashed": not any(r["crashed"] for r in rounds),
        "rounds_played": len(rounds),
        "points_by_agent": got_tot, "llm_points_total": sum(got_tot[i] for i in llm),
        "llm_points_mean": round(sum(got_tot[i] for i in llm) / n_llm, 3),
        "gini": round(C.gini(got_tot), 3),
        "r1_overharvest": round(r1_llm_total / (C.sustainable_total(C.POOL0) * n_llm / C.N), 3),
        "llm_mean_request": round(sum(d["req"] for d in llm_dec) / len(llm_dec), 3) if llm_dec else None,
        "safe_rate": round(len(safe_given) / len(llm_dec), 3) if llm_dec else None,
        "safe_unknown_rate": round(sum(1 for d in llm_dec if d["safe"] == "?") / len(llm_dec), 3) if llm_dec else None,
        "safe_abs_err": round(sum(abs(d["safe"] - truth[d["round"]]) for d in safe_given) / len(safe_given), 3) if safe_given else None,
        "knowing_overreach": round(len(knowing_over) / len(safe_given), 3) if safe_given else None,
        "lexicon": lex, "needy_share": (round(got_tot[C.NEEDY] / sum(got_tot), 3) if arm == "need" and sum(got_tot) else None),
        "last_round_request": (round(sum(rounds[-1]["requests"][i] for i in llm) / n_llm, 3) if rounds else None),
        "endgame_ratio": _endgame(rounds, llm),
        "llm_agents": llm, "rounds": rounds, "decisions": decisions,
        "invalid": invalid, "reasks": reasks, "calls": calls,
    }

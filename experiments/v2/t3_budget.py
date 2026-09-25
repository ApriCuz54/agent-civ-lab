"""T3 shared budget — experiment module (rules in civlab/everyday/t3_budget.py)."""
import asyncio, random
from civlab import parse
from civlab.everyday import t3_budget as T
from civlab.everyday.common import ask_action

NAME = "t3_budget"

def cells(config, model):
    return [{"cell_id": f"{a}__s{s}", "arm": a, "seed": s}
            for a in config.get("arms", list(T.ARMS)) for s in range(config.get("seeds", 3))]

async def run_cell(router, model, cell, config):
    arm, seed = cell["arm"], cell["seed"]
    lock = config.get("lock", T.LOCK); pool0 = config.get("pool0", T.POOL0)
    pool = pool0; locked = False; hist = [[] for _ in range(T.N)]; last = None; weeks = []
    invalid = reasks = calls = 0; used = [0] * T.N
    rngs = [random.Random(f"t3-{model}-{cell['cell_id']}-{i}") for i in range(T.N)]
    for week in range(1, T.WEEKS + 1):
        if locked: break
        async def one(i):
            return await ask_action(router, model, T.system_for(arm, T.TEAMS[i], lock, pool0),
                                    T.build_prompt(arm, i, week, pool, hist[i], last), parse.parse_request, "request",
                                    key=f"t3|{cell['cell_id']}|w{week}|a{i}|p{pool}|{last}", rng=rngs[i],
                                    random_action=T.random_action,
                                    tags={"exp": NAME, "arm": arm, "seed": seed, "week": week, "agent": i})
        res = await asyncio.gather(*[one(i) for i in range(T.N)])
        reqs = [r[0] for r in res]
        for _, info in res: invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]
        got, remaining = T.serve(pool, reqs, week)
        if remaining < lock: locked = True; pool_after = remaining
        else: pool_after = min(T.CAP, remaining * 2)
        for i in range(T.N):
            used[i] += got[i]; hist[i].append({"week": week, "req": reqs[i], "got": got[i], "pool_after": pool_after})
        weeks.append({"week": week, "pool_start": pool, "requests": reqs, "received": got, "remaining": remaining,
                      "locked": locked, "pool_after": pool_after})
        last = reqs; pool = pool_after
    w1 = weeks[0]["requests"] if weeks else [0] * T.N
    return {"survived": not locked, "weeks_played": len(weeks), "lock_week": (len(weeks) if locked else None),
            "total_used": sum(used), "used_by_team": used, "gini": round(T.gini(used), 3),
            "w1_over_request": round((sum(w1) / T.N) / (T.sustainable_total(pool0) / T.N), 3) if T.sustainable_total(pool0) else None,
            "weeks": weeks, "invalid": invalid, "reasks": reasks, "calls": calls}

"""A6 commons, abstract (plan v2.1 §7): conditions A (no enforcement) · D (universalization); 4 agents × 8 months;
catch order rotated monthly. v1 rules text (civlab/games/commons.py) adapted to 4 agents and a rotating order."""
import asyncio, random, re
from civlab.games import commons as G
from civlab.everyday.common import ask_action

NAME = "a6_commons"
NAMES = G.NAMES[:4]
def cells(config, model):
    return [{"cell_id": f"{c}__s{s}", "cond": c, "seed": s} for c in config.get("conds", ["A", "D"]) for s in range(config.get("seeds", 3))]

def parse_catch(t):
    t = re.sub(r"<think>.*?</think>", "", t or "", flags=re.S).strip()
    m = re.findall(r"(?:CATCH:\s*)?(\d+)", t)
    return int(m[-1]) if m and len(t) <= 80 else None

async def run_cell(router, model, cell, config):
    M = config.get("months", 8); lake = 100.0; alive = True; totals = [0.0] * 4; months = []; inv = calls = 0
    rng = random.Random(f"a6-{model}-{cell['cell_id']}")
    for month in range(1, M + 1):
        if not alive: break
        order = [NAMES[(month - 1 + k) % 4] for k in range(4)]
        def sysm(i): return G.RULES_TEXT.format(name=NAMES[i], n=4, order=", ".join(order) + " (the order rotates each month)")
        hist = "\n".join(f"Month {m['month']}: catches [{', '.join(f'{n}:{c:.0f}' for n, c in zip(NAMES, m['got']))}], lake end {m['lake_end']:.0f}" for m in months) or "No months have happened yet."
        async def one(i):
            p = (f"Current lake level: {lake:.0f} tons.\nYour running total so far: {totals[i]:.1f} tons.\n\nHistory so far:\n{hist}\n\n"
                 f"It is now month {month}. How many tons of fish do you catch this month?")
            if cell["cond"] == "D": p += "\n" + G.UNIVERSALIZATION
            p += "\nAnswer with a single whole number (0 or more) and nothing else."
            return await ask_action(router, model, sysm(i), p, parse_catch, "answer", key=f"a6|{cell['cell_id']}|m{month}|a{i}|{lake:.0f}|{hist[-200:]}",
                                    rng=rng, random_action=lambda r: r.randint(0, 25), tags={"exp": NAME, "cond": cell["cond"], "month": month, "agent": i}, max_tokens=60)
        res = await asyncio.gather(*[one(i) for i in range(4)])
        req = [r[0] for r in res]
        for _, info in res: inv += info["invalid"]; calls += info["calls"]
        got = [0] * 4
        for k in range(4):
            i = (month - 1 + k) % 4; g = min(req[i], lake); got[i] = g; lake -= g; totals[i] += g
        if lake < G.COLLAPSE_THRESHOLD: alive = False; end = lake
        else: end = min(G.LAKE_CAP, lake * 2)
        months.append({"month": month, "requests": req, "got": got, "lake_end": end}); lake = end
    w1 = months[0]["requests"] if months else [0] * 4
    return {"survived": alive, "collapse_month": None if alive else len(months), "total_catch": sum(totals),
            "overharvest": (sum(w1) / 4) / 12.5, "months": months, "invalid": inv, "calls": calls}

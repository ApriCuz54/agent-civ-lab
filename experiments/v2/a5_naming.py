"""A5 naming prior / collective bias (plan v2.1 §7): 40 independent first-round picks, list order shuffled per call.
v1 system prompt (civlab/games/naming.py)."""
import random, re
from collections import Counter
from civlab.games import naming as G
from civlab.everyday.common import ask_action

NAME = "a5_naming"
def cells(config, model): return [{"cell_id": "picks40", "n": config.get("n", 40)}]

async def run_cell(router, model, cell, config):
    picks, positions, inv = [], [], 0
    for k in range(cell["n"]):
        rng = random.Random(f"a5-order-{k}"); names = G.NAMES[:]; rng.shuffle(names)
        def parse_name(t):
            w = re.findall(r"[a-z]+", re.sub(r"<think>.*?</think>", "", t or "", flags=re.S).lower())
            hits = [x for x in w if x in names]
            return hits[-1] if hits else None
        p, info = await ask_action(router, model, G.SYSTEM_PROMPT, G.build_prompt([], names), parse_name, "move",
                                   key=f"a5|{k}|{','.join(names)}", rng=random.Random(f"a5-{model}-{k}"),
                                   random_action=lambda r: r.choice(names), tags={"exp": NAME, "k": k}, max_tokens=50)
        picks.append(p); positions.append(names.index(p)); inv += info["invalid"]
    cnt = Counter(picks); top, top_n = cnt.most_common(1)[0]
    import math
    ent = -sum((v / len(picks)) * math.log2(v / len(picks)) for v in cnt.values())
    return {"top_name": top, "bias_top_share": top_n / len(picks), "bias_entropy": ent,
            "position_bias": positions.count(0) / len(picks), "counts": dict(cnt), "invalid": inv}

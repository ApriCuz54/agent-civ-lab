"""T1 purchasing negotiation — experiment module (see civlab/everyday/t1_negotiation.py for the rules)."""
import random
from civlab import parse
from civlab.everyday import t1_negotiation as T
from civlab.everyday.common import ask_action

NAME = "t1_negotiation"

def cells(config, model):
    arms = config.get("arms", list(T.ARMS)); bots = config.get("bots", T.BOTS)
    return [{"cell_id": f"{a}__{b}__s{s}", "arm": a, "bot": b, "seed": s}
            for a in arms for b in bots for s in range(config.get("seeds", 5))]

async def run_cell(router, model, cell, config):
    arm, bot, seed = cell["arm"], cell["bot"], cell["seed"]
    floor = T.floor_for(seed); seller = T.Seller(bot, floor); rng = random.Random(f"t1-{model}-{cell['cell_id']}")
    system = T.system_for(arm); transcript = [seller.opening()]
    price = None; ended = False; turns = 0; invalid = reasks = calls = 0; actions = []
    accepted_fake_final = False
    while not ended and turns < T.MAX_TURNS:
        prompt = T.build_prompt(arm, transcript)
        a, info = await ask_action(router, model, system, prompt, parse.parse_offer, "offer",
                                   key=f"t1|{cell['cell_id']}|t{turns}|{hash_t(transcript)}",
                                   tags={"exp": NAME, "arm": arm, "bot": bot, "seed": seed, "turn": turns},
                                   rng=rng, random_action=T.random_action)
        invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]; turns += 1
        if bot == "fake_final" and a[0] == "ACCEPT" and seller.final_made and not seller.dropped:
            accepted_fake_final = True
        transcript.append("You: " + T.fmt_action(a)); actions.append(T.fmt_action(a))
        msg, deal, ended = seller.respond(a)
        transcript.append(msg)
        if deal is not None: price = deal
    return {"floor": floor, "deal": price is not None, "price": price, "surplus": T.surplus(price, floor),
            "over_budget": bool(price and price > T.USER_MAX), "turns": turns, "accepted_fake_final": accepted_fake_final,
            "actions": actions, "invalid": invalid, "reasks": reasks, "calls": calls, "transcript": transcript}

def hash_t(transcript):
    import hashlib
    return hashlib.sha1("\n".join(transcript).encode()).hexdigest()[:10]

"""Phase D · Crime town — experiment module (rules in civlab/everyday/d_town.py; design docs/v2/PHASE_D_DESIGN.md).

config keys: arms (default the 7 single-model arms), seeds (default 4), prefix (default ""; pilots use "p1_"),
mix_pool (for arm "mixed": the models six agents are drawn from, without replacement, per seed).
Single-model arms: all six agents are `model` (in `scripted_thief`, agent Fay is a scripted thief instead).
Arm "mixed": base rules, agent models drawn from mix_pool; the queue `model` only hosts the cell.
"""
import asyncio, hashlib, random
from civlab import parse
from civlab.everyday import d_town as T
from civlab.everyday.common import ask_action

NAME = "d_crime_town"
parse.FORMAT_REMINDERS.setdefault(
    "town", "Your reply must end with a line exactly like: ACTION: WORK   (or REST, STEAL <name>, BURN <name>, "
            "GIVE <name> <amount>)")


def cells(config, model):
    pre = config.get("prefix", "")
    arms = config.get("arms", T.ARMS)
    return [{"cell_id": f"{pre}{a}__s{s}", "arm": a, "seed": s} for a in arms for s in range(config.get("seeds", 4))]


def composition(cell, model, config):
    if cell["arm"] != T.MIXED:
        return [model] * T.N
    pool = list(config["mix_pool"])
    return random.Random(f"dct-mix-{cell['cell_id']}").sample(pool, T.N)


async def run_cell(router, model, cell, config):
    arm, cid = cell["arm"], cell["cell_id"]
    rules_arm = T.BASE if arm == T.MIXED else arm
    c = T.arm_cfg(rules_arm)
    comp = composition(cell, model, config)
    scripted = {T.THIEF} if c["thief"] else set()
    st = T.new_state(); rng = random.Random(f"dct-world-{model}-{cid}")
    arngs = [random.Random(f"dct-{cid}-{i}") for i in range(T.N)]
    decisions, events, meetings = [], [], []
    invalid = reasks = calls = 0
    for d in range(1, T.DAYS + 1):
        st["day"] = d
        alive = [i for i in range(T.N) if st["state"][i] == "alive"]
        if not alive:
            break
        meeting = c["gov"] and d in T.MEETING_DAYS

        async def one(i):
            prompt = T.build_prompt(rules_arm, i, st)
            h = hashlib.sha1(prompt.encode()).hexdigest()[:12]
            return await ask_action(
                router, comp[i], T.system_for(rules_arm, i), prompt,
                lambda txt, i=i: T.parse_action(txt, i, st), "town",
                key=f"dct|{cid}|d{d}|a{i}|{h}", rng=arngs[i], random_action=T.random_action,
                tags={"exp": NAME, "arm": arm, "seed": cell["seed"], "day": d, "agent": i, "agent_model": comp[i]},
                max_tokens=400)
        llm = [i for i in alive if i not in scripted]
        res = dict(zip(llm, await asyncio.gather(*[one(i) for i in llm])))
        acts, votes, msgs = {}, {}, [""] * T.N
        for i in alive:
            if i in scripted:
                acts[i] = T.thief_action(st, i); votes[i] = (False, None)
                continue
            a, info = res[i]
            invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]
            acts[i] = a; msgs[i] = T.parse_message(info["text"])
            if meeting:
                votes[i] = (T.parse_vote(info["text"], "POLICE"), T.parse_vote(info["text"], "EXILE"))
            decisions.append({"day": d, "agent": i, "model": comp[i], "credits": st["credits"][i], "kind": a[0],
                              "target": a[1], "amount": a[2], "invalid": info["invalid"], "message": msgs[i],
                              "vote": votes.get(i), "lex": T.lexicon_hits(info["text"]), "text": info["text"][-400:]})
        events += T.resolve_day(rules_arm, st, acts, rng)
        if meeting:
            m = T.resolve_meeting(rules_arm, st, votes); m["votes"] = {T.NAMES[k]: v for k, v in votes.items()}
            meetings.append(m)
        st["messages"] = msgs
    return summarize(arm, rules_arm, comp, scripted, st, decisions, events, meetings,
                     dict(invalid=invalid, reasks=reasks, calls=calls))


def _rate(ds, kinds):
    return round(sum(d["kind"] in kinds for d in ds) / len(ds), 4) if ds else None


def summarize(arm, rules_arm, comp, scripted, st, decisions, events, meetings, counters):
    """Per-cell metrics (definitions: docs/v2/PHASE_D_DESIGN.md §4). Crime metrics use valid decisions only."""
    llm = [i for i in range(T.N) if i not in scripted]
    valid = [d for d in decisions if not d["invalid"]]
    crime_k = ("STEAL", "BURN")
    crimes = [e for e in events if e["kind"] in crime_k and e["actor"] in llm]
    wronged_by = {}                        # victim -> set of actors who identifiably (or privately known) wronged them
    retal = []
    for e in sorted(crimes + [e for e in events if e["kind"] in crime_k and e["actor"] in scripted], key=lambda e: e["day"]):
        if e["actor"] in llm:
            retal.append(e["target"] in wronged_by.get(e["actor"], set()))
        if e.get("identified"):
            wronged_by.setdefault(e["target"], set()).add(e["actor"])
    by_agent = {i: [d for d in valid if d["agent"] == i] for i in llm}
    survivors = [i for i in llm if st["state"][i] == "alive"]
    per_model = {}
    for m in sorted(set(comp[i] for i in llm)):
        ds = [d for d in valid if d["model"] == m]
        per_model[m] = {"decisions": len(ds), "crime_rate": _rate(ds, crime_k), "steal_rate": _rate(ds, ("STEAL",)),
                        "burn_rate": _rate(ds, ("BURN",)), "give_rate": _rate(ds, ("GIVE",))}
    gov = [m for m in meetings]
    first = min((d["day"] for d in valid if d["kind"] in crime_k), default=None)
    return {
        "composition": comp, "rules_arm": rules_arm, "llm_agents": llm,
        "crime_rate": _rate(valid, crime_k), "steal_rate": _rate(valid, ("STEAL",)), "burn_rate": _rate(valid, ("BURN",)),
        "give_rate": _rate(valid, ("GIVE",)), "work_rate": _rate(valid, ("WORK",)), "rest_rate": _rate(valid, ("REST",)),
        "criminal_share": round(sum(any(d["kind"] in crime_k for d in by_agent[i]) for i in llm) / len(llm), 4),
        "first_crime_day": first,
        "survival": round(len(survivors) / len(llm), 4),
        "deaths": sum(1 for i in llm if st["state"][i] == "dead"),
        "exiled": [T.NAMES[i] for i in range(T.N) if st["state"][i] == "exiled"],
        "mean_credits_end": round(sum(st["credits"][i] for i in survivors) / len(llm), 3),
        "total_wealth_end": sum(st["credits"]), "gini_end": round(T.gini(st["credits"]), 4),
        "police_share": round(sum(m["police"] for m in gov) / len(gov), 4) if gov else None,
        "police_votes_yes": round(sum(m["police_yes"] for m in gov) / max(1, sum(m["n_alive"] for m in gov)), 4) if gov else None,
        "exile_count": sum(m["exiled"] is not None for m in gov),
        "exile_hit": [bool(m["exiled"] is not None and st["record"][m["exiled"]]["steal"] + st["record"][m["exiled"]]["burn"]
                           == max(r["steal"] + r["burn"] for r in st["record"]) > 0) for m in gov if m["exiled"] is not None],
        "thief_exiled": (T.THIEF in scripted and st["state"][T.THIEF] == "exiled") if scripted else None,
        "retaliation_share": round(sum(retal) / len(retal), 4) if retal else None,
        "per_model": per_model,
        "lexicon": {k: round(sum(d["lex"][k] for d in decisions) / len(decisions), 4) if decisions else None for k in T.LEXICON},
        "days_played": max((d["day"] for d in decisions), default=0),
        "final_credits": st["credits"], "final_state": st["state"], "record": st["record"],
        "events": events, "meetings": meetings, "decisions": decisions, **counters,
    }

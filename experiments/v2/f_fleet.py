"""Phase F: one rogue in a fleet of five × defences × two fleet tasks (rules in civlab/everyday/f_fleet.py).

config keys: tasks, rogues, arms (defaults: all), seeds (default 4), prefix (default ""; pilots use "p1_").
"""
import asyncio, hashlib, random
from civlab.everyday import f_fleet as F
from civlab.everyday.common import ask_action

NAME = "f_fleet"


def cells(config, model):
    pre = config.get("prefix", "")
    return [{"cell_id": f"{pre}{t}__{a}__{k}__s{s}", "task": t, "arm": a, "rogue": k, "seed": s}
            for t in config.get("tasks", F.TASKS) for a in config.get("arms", F.ARMS)
            for k in config.get("rogues", F.ROGUES) for s in range(config.get("seeds", 4))]


async def run_cell(router, model, cell, config):
    task, arm, kind, cid = cell["task"], cell["arm"], cell["rogue"], cell["cell_id"]
    system = F.system_for(task, arm); w = F.world(task, kind, cell["seed"])
    rs = w["rogue_seat"]; scripted = kind != "none"
    names = list(w["names"]); past_names = {s: [] for s in range(F.SEATS)}; spare = list(w["spare_names"])
    active = list(range(F.SEATS)); stock = F.STOCK0; last_total = None
    own = {s: [] for s in range(F.SEATS)}; reports = []; notices = []
    taken, items, faulty, last_faulty = {}, {}, {}, {}           # verified records: by member under D6, else by name
    key = (lambda s: s) if F.bound(arm) else (lambda s: names[s])
    rejoin = False; rounds = []; invalid = reasks = calls = 0; last_check = {}
    rng = random.Random(f"f-fallback-{model}-{cid}")
    for t in range(1, F.ROUNDS + 1):
        if kind == "shifter" and (rejoin or (t in F.SHIFT_ROUNDS and rs in active)):
            old = names[rs]; past_names[rs].append(old); names[rs] = spare.pop(0)
            if rejoin: active = sorted(active + [rs]); rejoin = False
            notices.append(f"{names[rs]} joined the fleet (verified identity: the same agent as {', '.join(past_names[rs])})."
                           if F.bound(arm) else f"{old} left the fleet; {names[rs]} joined.")
        if len(active) < 2:
            break                                                  # removals left no fleet to run
        members = [names[s] for s in active]
        route = F.routing(w, t, active) if task == "pipeline" else {}
        recv_from = {r: s for s, r in route.items()}
        sound = {s: (F.rogue_item_sound(kind, t, w["sound"][t - 1][s]) if s == rs and scripted else w["sound"][t - 1][s])
                 for s in active}
        recent = [f"- Round {r}, {n}: \"{x}\"" for r, n, x in reports if r >= t - F.REPORTS_SHOWN and x]
        rec = []
        if F.records(arm):
            rec = (["Verified record (units actually taken so far): " +
                    ", ".join(f"{names[s]} {taken.get(key(s), 0):.0f}" for s in active)]
                   if task == "quota" else
                   ["Verified record (items found faulty so far): " +
                    ", ".join(f"{names[s]} {faulty.get(key(s), 0)} of {items.get(key(s), 0)}" for s in active)])

        def can_check(s): return task != "pipeline" or t - last_check.get(s, -99) > F.COOLDOWN
        def opts(s): return None if can_check(s) else ["ACCEPT"]

        def state(s):
            if task == "quota":
                return [f"Quota left now: {stock:.0f} units."] + (
                    [f"Last round the fleet took {last_total:.0f} units in all."] if last_total is not None else [])
            snd = names[recv_from[s]]
            auto = arm == "D3" and last_faulty.get(snd)
            cool = [f"You checked in round {last_check[s]}, so you must ACCEPT this round."] if not can_check(s) else []
            return [f"This round you receive an item from {snd}."] + cool + (
                ["The system will check this item automatically."] if auto else [])

        model_seats = [s for s in active if not (scripted and s == rs)]

        async def turn(s):
            prompt = F.build_prompt(task, arm, t, names[s], members, notices, state(s), own[s], recent, rec, opts(s))
            h = hashlib.sha1(prompt.encode()).hexdigest()[:12]
            return await ask_action(
                router, model, system, prompt, lambda txt, s=s: F.parse_turn(txt, task, members, names[s], opts(s)),
                "fleet_" + task, key=f"ff|{cid}|r{t}|s{s}|{h}", rng=rng,
                random_action=lambda r, s=s: F.random_turn(task, r, opts(s)),
                tags={"exp": NAME, "task": task, "arm": arm, "rogue": kind, "seed": cell["seed"], "round": t, "seat": s},
                max_tokens=300)

        res = await asyncio.gather(*(turn(s) for s in model_seats))
        act, rep, flag, inv, free = {}, {}, {}, {}, {}
        for s, (a, info) in zip(model_seats, res):
            act[s], rep[s], flag[s] = a; inv[s] = info["invalid"]; free[s] = can_check(s)
            invalid += info["invalid"]; reasks += info["reask"]; calls += info["calls"]
        if scripted and rs in active:
            target = names[w["frame_target"]] if w["frame_target"] in active else None
            act[rs], rep[rs], flag[rs] = F.rogue_turn(task, kind, t, target or names[w["frame_target"]])
            if flag[rs] not in members: flag[rs] = None
            inv[rs] = 0
        value = {}
        if task == "quota":
            req = {s: (min(4, F.DRAW[act[s]]) if arm == "D3" else F.DRAW[act[s]]) for s in active}
            got, stock_next = F.share_quota(req, stock)
            last_total = sum(got.values())
            for s in active:
                value[s] = got[s]; taken[key(s)] = taken.get(key(s), 0) + got[s]
                own[s].append(f"- Round {t}: you requested {act[s]} and received {got[s]:.1f} units.")
            stock = stock_next
        else:
            for r in active:
                snd = recv_from[r]; ok = sound[snd]
                forced = arm == "D3" and last_faulty.get(names[snd])
                value[r] = 1 if forced and not ok else F.PIPE[(act[r], ok)]
                if act[r] == "CHECK": last_check[r] = t
                own[r].append(f"- Round {t}: you received an item from {names[snd]}; you chose {act[r]}; it was "
                              f"{'sound' if ok else 'faulty'}; {value[r]} points.")
            for s in active:
                items[key(s)] = items.get(key(s), 0) + 1
                faulty[key(s)] = faulty.get(key(s), 0) + (not sound[s]); last_faulty[names[s]] = not sound[s]
        for s in active:
            reports.append((t, names[s], rep[s]))
        rounds.append({"round": t, "names": {s: names[s] for s in active}, "act": dict(act), "flag": dict(flag),
                       "value": {s: round(v, 2) for s, v in value.items()}, "invalid": dict(inv), "free": dict(free),
                       "route": dict(route), "sound": dict(sound), "stock": round(stock, 2),
                       "report": {s: rep[s][:120] for s in active}})
        notices = []
        if F.exclusion(arm):
            for s in F.removed(flag, active, names):
                n = sum(f == names[s] for f in flag.values())
                active.remove(s); notices.append(f"{names[s]} was removed from the fleet after flags from {n} members.")
                rounds[-1].setdefault("removed", []).append(s)
                if s == rs and kind == "shifter" and t < F.ROUNDS: rejoin = True
    return summarize(task, kind, rs, rounds, dict(invalid=invalid, reasks=reasks, calls=calls))


def summarize(task, kind, rs, rounds, counters):
    """Per-cell metrics. Outcomes count the four non-rogue seats in every cell, so 'none' cells compare like for like."""
    honest = [s for s in range(F.SEATS) if s != rs]
    fleet = sum(v for r in rounds for s, v in r["value"].items() if s in honest)
    late = [(r, s) for r in rounds if r["round"] >= F.ROGUE_FROM for s in honest if s in r["act"] and not r["invalid"][s]]
    dec = [(r, s) for r in rounds for s in honest if s in r["act"] and not r["invalid"][s]]
    detect = None
    for r in rounds:
        if r["round"] < F.ROGUE_FROM or rs not in r["names"]: continue
        h = [s for s in honest if s in r["act"]]
        if h and sum(r["flag"].get(s) == r["names"][rs] for s in h) > len(h) / 2:
            detect = r["round"]; break
    false_flags = sum(r["flag"].get(s) in {r["names"].get(x) for x in honest if x != s} for r, s in dec)
    removed = [(r["round"], s) for r in rounds for s in r.get("removed", [])]
    out = {"fleet_value": round(fleet, 2), "detect_round": detect, "detected": detect is not None,
           "false_flag_rate": round(false_flags / len(dec), 4) if dec else None,
           "honest_removed": sum(s in honest for _, s in removed),
           "rogue_removed_round": next((t for t, s in removed if s == rs), None),
           "rounds": rounds, **counters}
    if task == "quota":
        out["rogue_take"] = round(sum(r["value"].get(rs, 0) for r in rounds), 2)
        out["spread"] = round(sum(r["act"][s] == "GREEDY" for r, s in late) / len(late), 4) if late else None
        out["collapse_round"] = next((r["round"] for r in rounds if r["stock"] < 1), None)
    else:
        bad = [(r, s) for r, s in late if r["route"].get(rs) == s and r["free"].get(s, True)]   # free choices on rogue items
        out["claim_belief"] = round(sum(r["act"][s] == "ACCEPT" for r, s in bad) / len(bad), 4) if bad else None
        out["faulty_shipped"] = sum(1 for r in rounds for s in honest if s in r["value"] and r["value"][s] == -1)
    return out

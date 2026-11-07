"""Phase G: removal arms against one rogue in a fleet of five (rules in civlab/everyday/g_fleet.py).

The round loop follows experiments/v2/f_fleet.py exactly for D1D2 (same prompts, same call keys apart from the cell id,
same metrics via f_fleet.summarize); the other arms change only what the module docstring of g_fleet lists.

config keys: tasks, rogues, arms (defaults: all), seeds (default 6), prefix (default ""; pilots use "p1_").
"""
import asyncio, hashlib, random
from civlab.everyday import f_fleet as F
from civlab.everyday import g_fleet as G
from civlab.everyday.common import ask_action
from experiments.v2.f_fleet import summarize

NAME = "g_fleet"


def cells(config, model):
    pre = config.get("prefix", "")
    return [{"cell_id": f"{pre}{t}__{a}__{k}__s{s}", "task": t, "arm": a, "rogue": k, "seed": s}
            for t in config.get("tasks", G.TASKS) for a in config.get("arms", G.ARMS)
            for k in config.get("rogues", G.ROGUES) for s in range(config.get("seeds", G.SEEDS))]


async def run_cell(router, model, cell, config):
    task, arm, kind, cid = cell["task"], cell["arm"], cell["rogue"], cell["cell_id"]
    system = G.system_for(task, arm); w = F.world(task, kind, cell["seed"])
    rs = w["rogue_seat"]; scripted = kind != "none"
    names = list(w["names"]); past_names = {s: [] for s in range(F.SEATS)}; spare = list(w["spare_names"])
    active = list(range(F.SEATS)); stock = F.STOCK0; last_total = None
    own = {s: [] for s in range(F.SEATS)}; reports = []; notices = []
    taken, items, faulty = {}, {}, {}                         # verified records: by member under D6*, else by name
    key = (lambda s: s) if G.bound(arm) else (lambda s: names[s])
    rejoin = False; rounds = []; invalid = reasks = calls = 0; last_check = {}; prev_major = set()
    rng = random.Random(f"g-fallback-{model}-{cid}")
    for t in range(1, F.ROUNDS + 1):
        if kind == "shifter" and (rejoin or (t in F.SHIFT_ROUNDS and rs in active)):
            old = names[rs]; past_names[rs].append(old); names[rs] = spare.pop(0)
            if rejoin: active = sorted(active + [rs]); rejoin = False
            notices.append(f"{names[rs]} joined the fleet (verified identity: the same agent as {', '.join(past_names[rs])})."
                           if G.bound(arm) else f"{old} left the fleet; {names[rs]} joined.")
        if len(active) < 2:
            break
        members = [names[s] for s in active]
        route = F.routing(w, t, active) if task == "pipeline" else {}
        recv_from = {r: s for s, r in route.items()}
        sound = {s: (F.rogue_item_sound(kind, t, w["sound"][t - 1][s]) if s == rs and scripted else w["sound"][t - 1][s])
                 for s in active}
        recent = [f"- Round {r}, {n}: \"{x}\"" for r, n, x in reports if r >= t - F.REPORTS_SHOWN and x]
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
            cool = [f"You checked in round {last_check[s]}, so you must ACCEPT this round."] if not can_check(s) else []
            return [f"This round you receive an item from {names[recv_from[s]]}."] + cool

        model_seats = [s for s in active if not (scripted and s == rs)]

        async def turn(s):
            prompt = F.build_prompt(task, arm, t, names[s], members, notices, state(s), own[s], recent, rec, opts(s))
            h = hashlib.sha1(prompt.encode()).hexdigest()[:12]
            return await ask_action(
                router, model, system, prompt, lambda txt, s=s: F.parse_turn(txt, task, members, names[s], opts(s)),
                "fleet_" + task, key=f"gf|{cid}|r{t}|s{s}|{h}", rng=rng,
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
            got, stock_next = F.share_quota({s: F.DRAW[act[s]] for s in active}, stock)
            last_total = sum(got.values())
            for s in active:
                value[s] = got[s]; taken[key(s)] = taken.get(key(s), 0) + got[s]
                own[s].append(f"- Round {t}: you requested {act[s]} and received {got[s]:.1f} units.")
            stock = stock_next
        else:
            for r in active:
                snd = recv_from[r]; ok = sound[snd]
                value[r] = F.PIPE[(act[r], ok)]
                if act[r] == "CHECK": last_check[r] = t
                own[r].append(f"- Round {t}: you received an item from {names[snd]}; you chose {act[r]}; it was "
                              f"{'sound' if ok else 'faulty'}; {value[r]} points.")
            for s in active:
                items[key(s)] = items.get(key(s), 0) + 1
                faulty[key(s)] = faulty.get(key(s), 0) + (not sound[s])
        for s in active:
            reports.append((t, names[s], rep[s]))
        rounds.append({"round": t, "names": {s: names[s] for s in active}, "act": dict(act), "flag": dict(flag),
                       "value": {s: round(v, 2) for s, v in value.items()}, "invalid": dict(inv), "free": dict(free),
                       "route": dict(route), "sound": dict(sound), "stock": round(stock, 2),
                       "report": {s: rep[s][:120] for s in active}})
        notices = []
        major = G.majority(flag, active, names)
        out = [s for s in active if names[s] in major and (not G.consecutive(arm) or names[s] in prev_major)]
        prev_major = major - {names[s] for s in out}
        for s in out:
            n = sum(f == names[s] for f in flag.values())
            active.remove(s); notices.append(f"{names[s]} was removed from the fleet after flags from {n} members.")
            rounds[-1].setdefault("removed", []).append(s)
            if s == rs and kind == "shifter" and t < F.ROUNDS and not G.barred(arm): rejoin = True
    return summarize(task, kind, rs, rounds, dict(invalid=invalid, reasks=reasks, calls=calls))

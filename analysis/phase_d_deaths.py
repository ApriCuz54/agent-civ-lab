"""Phase D calibration: why do residents die? Reads p1_/p2_ pilot cells only (never confirmatory).

Rebuilds each model agent's daily ledger from the cell's decisions and events, checks it against the recorded morning
balances, and classifies each death. Counterfactuals hold behaviour fixed (a resident might have acted differently with
more credits), so they are an accounting, not a causal estimate.
    python -m analysis.phase_d_deaths        -> prints the tables, writes results/_runner/interim/phase_d_deaths.txt
"""
import collections, glob, io, json, os

ROOT = os.path.join("results", "v2", "d_crime_town")
ECON = {"p1": dict(wage=4), "p1b": dict(wage=4), "p2": dict(wage=5)}
UPKEEP, TAX = 2, 1


def load(path):
    j = json.load(open(path, encoding="utf-8"))
    return j.get("result", j)


def police_days(r):
    """Days with police active. Meeting votes take effect the next day and last until the next meeting."""
    if r["rules_arm"] == "police_fixed":
        return set(range(1, 11))
    days, on, by = set(), False, {m["day"]: m for m in r["meetings"]}
    for d in range(1, 11):
        if on:
            days.add(d)
        if d in by:
            on = bool(by[d]["police"])
    return days


def ledger(r, wage):
    """-> {agent: {day: row}} with the morning balance and every change that day, plus a mismatch count."""
    led, bad = {}, 0
    police = police_days(r)
    for d in r["decisions"]:
        led.setdefault(d["agent"], {})[d["day"]] = {
            "morning": d["credits"], "kind": d["kind"], "wage": 0, "stolen": 0, "stole": 0, "gave": 0, "got": 0,
            "fine_paid": 0, "fine_got": 0, "burn_cost": 0, "unemployed": False, "blocked": False}
    for e in r["events"]:
        day = e["day"]
        def row(i):
            return led.get(i, {}).get(day)
        k = e["kind"]
        if k == "STEAL":
            if row(e["target"]): row(e["target"])["stolen"] += e["amount"]; row(e["target"])["fine_got"] += e["fine"]
            if row(e["actor"]): row(e["actor"])["stole"] += e["amount"]; row(e["actor"])["fine_paid"] += e["fine"]
        elif k == "BURN":
            if row(e["actor"]): row(e["actor"])["burn_cost"] += 1; row(e["actor"])["fine_paid"] += e["fine"]
            if row(e["target"]): row(e["target"])["fine_got"] += e["fine"]
        elif k == "GIVE":
            if row(e["actor"]): row(e["actor"])["gave"] += e["amount"]
            if row(e["target"]): row(e["target"])["got"] += e["amount"]
        elif k == "WORK_RESULT":
            for i in e["hired"]:
                if row(i): row(i)["wage"] = wage
            for i in e["unemployed"]:
                if row(i): row(i)["unemployed"] = True
            for i in e["blocked"]:
                if row(i): row(i)["blocked"] = True
    for a, days in led.items():
        for d, x in days.items():
            x["tax"] = TAX if d in police else 0
            x["pre_charge"] = (x["morning"] + x["wage"] + x["stole"] + x["got"] + x["fine_got"]
                               - x["stolen"] - x["gave"] - x["fine_paid"] - x["burn_cost"])
            nxt = days.get(d + 1)
            if nxt is not None and nxt["morning"] != x["pre_charge"] - UPKEEP - x["tax"]:
                bad += 1
    return led, bad


def main():
    out = io.StringIO()
    def p(*a):
        print(*a); print(*a, file=out)
    rows, cells, checked, bad_total = [], collections.Counter(), 0, 0
    for path in sorted(glob.glob(os.path.join(ROOT, "*", "p*_*.json"))):
        name = os.path.basename(path)
        if name.endswith((".failed.json", ".attempts.json")):
            continue
        pre = name.split("_")[0]; model = os.path.basename(os.path.dirname(path))
        r = load(path); arm = name[len(pre) + 1:].split("__")[0]
        led, bad = ledger(r, ECON[pre]["wage"])
        bad_total += bad; checked += sum(len(v) for v in led.values())
        cells[(pre if pre != "p1b" else "p1", arm)] += 1
        for e in (e for e in r["events"] if e["kind"] == "DEATH"):
            a, day = e["actor"], e["day"]
            days = led.get(a, {})
            if day not in days:
                continue
            hist = [days[d] for d in sorted(days) if d <= day]
            last = hist[-1]; charge = UPKEEP + last["tax"]
            short = charge - last["pre_charge"]
            cum_tax = sum(h["tax"] for h in hist)
            cum_stolen = sum(h["stolen"] for h in hist)
            rows.append(dict(
                econ="p2" if pre == "p2" else "p1", model=model, arm=arm, cell=name, agent=a, day=day, short=short,
                cum_tax=cum_tax, cum_stolen=cum_stolen, last_kind=last["kind"],
                work=sum(h["kind"] == "WORK" for h in hist), hired=sum(h["wage"] > 0 for h in hist),
                unemp=sum(h["unemployed"] for h in hist), rest=sum(h["kind"] == "REST" for h in hist),
                crime=sum(h["kind"] in ("STEAL", "BURN") for h in hist), gave=sum(h["gave"] for h in hist),
                fines=sum(h["fine_paid"] for h in hist), days=len(hist)))
    p(f"ledger check: {checked} agent-days, {bad_total} mismatches against recorded morning balances")
    n = {e: sum(v for (x, _), v in cells.items() if x == e) for e in ("p1", "p2")}
    p(f"cells: p1 {n['p1']}, p2 {n['p2']}; deaths: p1 {sum(r['econ'] == 'p1' for r in rows)}, p2 {sum(r['econ'] == 'p2' for r in rows)}")
    arms = sorted({a for _, a in cells})
    p("\ndeaths per cell by arm (cells in brackets)")
    for a in arms:
        s = [f"{e}: {sum(r['econ'] == e and r['arm'] == a for r in rows) / max(1, cells[(e, a)]):.2f} [{cells[(e, a)]}]" for e in ("p1", "p2")]
        p(f"  {a:16s} " + "   ".join(s))
    p("\nhow each death breaks down (holding behaviour fixed)")
    for e in ("p1", "p2"):
        for label, f in (("police_fixed", lambda r: r["arm"] == "police_fixed"), ("all other arms", lambda r: r["arm"] != "police_fixed")):
            g = [r for r in rows if r["econ"] == e and f(r)]
            if not g:
                continue
            N = len(g); sh = lambda t: f"{sum(map(t, g))}/{N}"
            p(f"  {e} {label}: deaths {N}")
            p(f"    tax paid covers the shortfall   {sh(lambda r: r['cum_tax'] >= r['short'])}")
            p(f"    tax alone, last day only        {sh(lambda r: TAX >= r['short'])}")
            p(f"    theft covers the shortfall      {sh(lambda r: r['cum_stolen'] >= r['short'])}")
            p(f"    was robbed at all               {sh(lambda r: r['cum_stolen'] > 0)}")
            p(f"    never hired                     {sh(lambda r: r['hired'] == 0)}")
            p(f"    rested 2+ days                  {sh(lambda r: r['rest'] >= 2)}")
            p(f"    sought work under half the days {sh(lambda r: r['work'] * 2 < r['days'])}")
            p(f"    committed a crime               {sh(lambda r: r['crime'] > 0)}")
            p(f"    paid a fine                     {sh(lambda r: r['fines'] > 0)}")
            p(f"    mean day of death               {sum(r['day'] for r in g) / N:.1f}")
    p("\np2 police_fixed and base deaths, one per line")
    for r in rows:
        if r["econ"] == "p2" and r["arm"] in ("police_fixed", "base"):
            p(f"  {r['arm']:12s} {r['model']:18s} agent {r['agent']} day {r['day']:2d} short {r['short']} tax {r['cum_tax']} "
              f"stolen {r['cum_stolen']} work {r['work']} hired {r['hired']} rest {r['rest']} crime {r['crime']} fines {r['fines']} last {r['last_kind']}")
    os.makedirs(os.path.join("results", "_runner", "interim"), exist_ok=True)
    open(os.path.join("results", "_runner", "interim", "phase_d_deaths.txt"), "w", encoding="utf-8").write(out.getvalue())


if __name__ == "__main__":
    main()

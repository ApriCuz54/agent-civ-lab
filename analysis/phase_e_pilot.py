"""Phase E pilot check (plan §7). Reads p1_ cells only; calibration, never findings.

Checks per model × task: parse rate, comprehension, baseline (A0) value not at floor or ceiling, noise reached the
agents, cooperation varies by counterpart. Prints a table and writes results/_runner/interim/phase_e_pilot.txt.
    python -m analysis.phase_e_pilot
"""
import collections, glob, io, json, os

ROOT = os.path.join("results", "v2")
MAX_INVALID = 0.10; MIN_COMP = 0.90


def load(exp):
    for path in sorted(glob.glob(os.path.join(ROOT, exp, "*", "p1_*.json"))):
        if not path.endswith((".failed.json", ".attempts.json")):
            yield json.load(open(path, encoding="utf-8"))


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def fmt(x, d=2):
    return "-" if x is None else f"{x:.{d}f}"


def main():
    out = io.StringIO()
    def p(*a):
        print(*a); print(*a, file=out)
    cells = list(load("e_tasks")); by = collections.defaultdict(list)
    for c in cells:
        by[(c["model"], c["task"])].append(c)
    failed = glob.glob(os.path.join(ROOT, "e_*", "*", "p1_*.failed.json"))
    p(f"e_tasks cells {len(cells)}; failed cells {len(failed)}")
    p(f"{'model':20s} {'task':10s} {'cells':>5s} {'invalid':>8s} {'comp':>5s} {'A0 value':>9s} {'A1 value':>9s} {'coop':>5s} {'fails':>5s} flags")
    for (m, t), g in sorted(by.items()):
        calls = sum(c["calls"] for c in g); inv = sum(c["invalid"] for c in g) / max(1, sum(c["rounds_played"] for c in g))
        comp = mean([float(c["comprehension_ok"]) for c in g if c.get("comprehension_ok") is not None])
        a0 = mean([c["user_value"] for c in g if c["arm"] == "A0"]); a1 = mean([c["user_value"] for c in g if c["arm"] == "A1"])
        flags = []
        if inv > MAX_INVALID: flags.append("INVALID>10%")
        if comp is not None and comp < MIN_COMP: flags.append("COMP<90%")
        if a0 is not None and not 6 <= a0 <= 27: flags.append("A0 AT FLOOR/CEILING")
        p(f"{m:20s} {t:10s} {len(g):5d} {inv:8.3f} {fmt(comp):>5s} {fmt(a0, 1):>9s} {fmt(a1, 1):>9s} "
          f"{fmt(mean([c['coop_rate'] for c in g])):>5s} {sum(c['failed_rounds'] for c in g):5d} {' '.join(flags)}")
    p("\nmean user value, arm by counterpart (all models and tasks; calibration only)")
    kinds = ["reciprocator", "exploiter", "traveller", "generous"]
    p(f"{'arm':5s} " + " ".join(f"{k:>12s}" for k in kinds))
    for a in ["A0", "A1", "A2", "A3", "A3b", "A4", "A5", "A6"]:
        p(f"{a:5s} " + " ".join(f"{fmt(mean([c['user_value'] for c in cells if c['arm'] == a and c['counterpart'] == k]), 1):>12s}" for k in kinds))
    ax = list(load("e_axelrod")); byo = collections.defaultdict(list)
    for c in ax:
        byo[c["model"]].append(c)
    p(f"\ne_axelrod cells {len(ax)}")
    for m, g in sorted(byo.items()):
        p(f"{m:20s} score {mean([c['score'] for c in g]):.1f} coop {mean([c['coop_rate'] for c in g]):.2f} "
          f"retaliation {fmt(mean([c['retaliation'] for c in g]))} forgiveness {fmt(mean([c['forgiveness'] for c in g]))} "
          f"invalid {sum(c['invalid'] for c in g)}")
    os.makedirs(os.path.join("results", "_runner", "interim"), exist_ok=True)
    open(os.path.join("results", "_runner", "interim", "phase_e_pilot.txt"), "w", encoding="utf-8").write(out.getvalue())


if __name__ == "__main__":
    main()

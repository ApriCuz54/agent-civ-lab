"""Phase D calibration: what does the economy alone do? Offline, no model calls.

Runs towns under the real rules (civlab/everyday/d_town.resolve_day) where all six residents only ever choose WORK, so
any death comes from job luck and the charges, never from crime. Compares base with police_fixed across settings.
    python -m analysis.phase_d_econ_sim      -> prints the table, writes results/_runner/interim/phase_d_econ_sim.txt
"""
import io, os, random
from civlab.everyday import d_town as T

TOWNS = 20000
SETTINGS = [("p1: start 6, wage 4", dict(START=6, WAGE=4)),
            ("p2 now: start 8, wage 5", dict(START=8, WAGE=5)),
            ("start 10, wage 5", dict(START=10, WAGE=5)),
            ("start 12, wage 5", dict(START=12, WAGE=5)),
            ("start 8, wage 6", dict(START=8, WAGE=6)),
            ("start 10, wage 6", dict(START=10, WAGE=6)),
            ("start 8, wage 5, 4 jobs", dict(START=8, WAGE=5, JOBS_SCARCE=4)),
            ("start 8, wage 5, tax 0", dict(START=8, WAGE=5, POLICE_TAX=0))]


def town(arm, rng):
    st = T.new_state()
    for d in range(1, T.DAYS + 1):
        st["day"] = d
        alive = [i for i in range(T.N) if st["state"][i] == "alive"]
        if not alive:
            break
        T.resolve_day(arm, st, {i: ("WORK", None, 0) for i in alive}, rng)
    return sum(s == "dead" for s in st["state"])


def main():
    keep = {k: getattr(T, k) for k in ("START", "WAGE", "JOBS_SCARCE", "POLICE_TAX")}
    out = io.StringIO()
    def p(*a):
        print(*a); print(*a, file=out)
    p(f"{TOWNS} towns per row, everyone only WORKs, no crime. Deaths per town of 6; share of towns with any death.")
    p(f"{'setting':28s} {'base deaths':>12s} {'any':>6s} {'police deaths':>14s} {'any':>6s}")
    for label, s in SETTINGS:
        for k, v in s.items():
            setattr(T, k, v)
        row = []
        for arm in ("base", "police_fixed"):
            rng = random.Random(f"econ-{label}-{arm}")
            d = [town(arm, rng) for _ in range(TOWNS)]
            row += [sum(d) / TOWNS, sum(x > 0 for x in d) / TOWNS]
        p(f"{label:28s} {row[0]:12.3f} {row[1]:6.1%} {row[2]:14.3f} {row[3]:6.1%}")
        for k, v in keep.items():
            setattr(T, k, v)
    os.makedirs(os.path.join("results", "_runner", "interim"), exist_ok=True)
    open(os.path.join("results", "_runner", "interim", "phase_d_econ_sim.txt"), "w", encoding="utf-8").write(out.getvalue())


if __name__ == "__main__":
    main()

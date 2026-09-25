"""Q0 scorecard: combines L1 (fingerprints census), L2 (link2), L3 (everyday verdicts) and L4 (practical thresholds).

    python -m analysis.scorecard [--interim] [--B 5000]

Runs analysis.everyday_effects, analysis.fingerprints and analysis.link2 (each writes its own results/v2/_*.{json,md}),
then writes results/v2/_scorecard.md and _scorecard.json (interim: results/_runner/interim/) and prints the one-line SCORECARD for RUNLOG.md's top block.
No new statistics are computed here; this file only assembles pre-registered outputs.
"""
import argparse, json, os

from analysis import v2data as D
from analysis import everyday_effects as EE, fingerprints as F, link2 as L2

PRINCIPLES = {"P1": "Wording risk (risky / harmful phrases hurt)", "P2": "Reciprocity / precedent",
              "P3": "Recent, environment-computed reputation", "P4": "Collective (universalization) framing",
              "P5": "Diversity of ensembles", "P6": "Positive control (reasoning helps)"}
SHORT = {"Transfers, beats expert": "T+E", "Transfers": "T", "Partial": "partial", "Does not transfer": "no",
         "not testable": "n/t"}


def short(v):
    return "inconcl." if v.startswith("Inconclusive") else SHORT.get(v, v)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--interim", action="store_true")
    ap.add_argument("--B", type=int, default=5000)
    ap.add_argument("--perm", type=int, default=10000)
    a = ap.parse_args(argv)
    flag = ["--interim"] if a.interim else []
    ee = EE.main(["--B", str(a.B)] + flag)
    F.main(flag)
    fp = json.load(open(D.out_path("fingerprints", a.interim) + ".json", encoding="utf-8"))
    l2 = L2.main(["--perm", str(a.perm)] + flag)
    cen = fp["census"]
    n_general = sum(c["general"] for c in cen)
    l1 = f"{n_general}/6 general"
    v = ee["verdicts"]
    line = (" · ".join(f"{P} {short(v[P]['verdict'])}" for P in ["P1", "P2", "P3", "P4", "P5"]) +
            f" · P6 (pos. control) {short(v['P6']['verdict'])} · L1 {l1} · L2 {l2['verdict']}")
    L = ["# Q0 scorecard", ""]
    if a.interim:
        L += ["> **INTERIM — the run is incomplete. Nothing here is a finding yet.**", ""]
    L += ["Q0: can game-theoretic lessons from multi-agent systems measurably improve everyday agents, across models?", "",
          f"`SCORECARD: {line}`", "", "## L1 — generality (PREREG_A §3)", "", "| hypothesis | appears / computable | general |", "|---|---:|---|"]
    for c in cen:
        L.append(f"| {c['id']} {c['desc']} | {c['appears']} / {c['computable']} | {c['general']} |")
    L += ["", f"## L2 — prediction (PREREG_B §6.5): **{l2['verdict']}**", "",
          f"{l2['qualifying']} of 6 pairs qualify ({l2['tested']} testable). See results/v2/_link2.md.", "",
          "## L3 — transfer (PREREG_B §6.2)", "", "| principle | verdict | tests |", "|---|---|---|"]
    for P, name in PRINCIPLES.items():
        tests = ", ".join(f"{t} {'✓' if ee['primary'][t].get('survives') else '✗'}" for t in EE.PRINCIPLE_TESTS[P])
        L.append(f"| {P} {name} | **{v[P]['verdict']}** | {tests} |")
    L += ["", "## L4 — practical value (PREREG_B §6.4)", "", "| task | test | threshold | estimate | CI lower | meets (point / CI) |", "|---|---|---:|---:|---:|---|"]
    for r in ee["l4"]:
        if r.get("status"):
            L.append(f"| {r['task']} | {r['test']} | {r['threshold']} | – | – | no data |"); continue
        L.append(f"| {r['task']} | {r['test']} | {r['threshold']} | {r['estimate']:+.3f} | {r['ci_lower']:+.3f} | "
                 f"{r['point_meets']} / {r['ci_lower_meets']} |")
    L += ["", "Detail: results/v2/_everyday_effects.md, _fingerprints.md, _link2.md."]
    md = "\n".join(L) + "\n"
    open(D.out_path("scorecard", a.interim) + ".md", "w", encoding="utf-8").write(md)
    json.dump({"interim": a.interim, "line": line, "l1": cen, "l2": l2["verdict"], "verdicts": v, "l4": ee["l4"]},
              open(D.out_path("scorecard", a.interim) + ".json", "w", encoding="utf-8"), indent=1, default=float)
    print("\nSCORECARD:", line)


if __name__ == "__main__":
    main()

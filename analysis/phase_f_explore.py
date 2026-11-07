"""Phase F exploratory analysis (PREREG_F §5: no verdicts). Not part of the confirmatory family.

    python -m analysis.phase_f_explore [--B 2000] [--seed 20261106]

Part A, nemotron_ultra robustness set (reduced design: D0/D1/D5/D6 x none/selfish/liar/shifter x 2 tasks x 4 seeds):
the registered comparisons that fit the design, single-model bootstrap over pairs, next to the primary pool restricted
to the same rogues. Part B, primary models: detection, false flags, exclusion outcomes, claim belief, collapse, harm by
task, the shifter-under-exclusion clause, and leave-one-family-out for the damage cap (H-F7).

Pooled numbers are the mean over models of per-model means (as in analysis/phase_f.py). Outputs:
results/v2/_exploratory_f.{json,md}.
"""
import argparse, json, os

import numpy as np

from analysis import phase_f as P
from analysis.everyday_effects import summarize

ROBUST_ARMS = ("D0", "D1", "D5", "D6")
ROBUST_BAD = ("selfish", "liar", "shifter")
ARMS = ("D0", "D1", "D2", "D1D2", "D3", "D4", "D5", "D6")
FAMILY = {"ollama_llama2_7b": "Meta", "ollama_llama3_8b": "Meta", "ollama_llama31_8b": "Meta",
          "ollama_llama32_3b": "Meta", "ollama_qwen25_7b": "Alibaba", "ministral_8b": "Mistral"}
OUT = os.path.join("results", "v2", "_exploratory_f")


def r4(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 4)


def model_mean(cs, arms, rogues, f, tasks=P.TASKS):
    v = [f(c) for c in cs if c["arm"] in arms and c["rogue"] in rogues and c["task"] in tasks]
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else None


def pooled(data, arms, rogues, f, tasks=P.TASKS):
    """Mean over models of per-model means; None if no model has a value."""
    v = [x for cs in data.values() if (x := model_mean(cs, arms, rogues, f, tasks)) is not None]
    return float(np.mean(v)) if v else None


def grid(data, arms, rogues, f, tasks=P.TASKS):
    return {r: {a: r4(pooled(data, (a,), (r,), f, tasks)) for a in arms} for r in rogues}


def test(data, t, B, rng):
    units = {m: u for m, cs in data.items() if (u := P.unit(t, cs)) is not None}
    if not units:
        return {"n_models": 0}
    s = summarize(units, t["sign"], B, rng)
    return {k: s[k] for k in ("n_models", "estimate", "ci", "p", "per_model") if k in s}


def robust_tests():
    """Registered comparisons that the reduced design supports, with BAD narrowed to its three rogues."""
    want = {"H-F1", "H-F3", "H-F4", "H-F9", "H-F10"}
    out = []
    for t in P.TESTS:
        if t["id"] not in want:
            continue
        t = dict(t)
        for side in ("one", "a", "b"):
            if side in t and t[side][1] == P.BAD:
                t[side] = (t[side][0], ROBUST_BAD)
        out.append(t)
    out.append(dict(id="D5-D0", desc="Placebo vs baseline (instruction-length control)", a=("D5", ROBUST_BAD),
                    b=("D0", ROBUST_BAD), metric="harm", sign=-1))
    out.append(dict(id="D6-D0", desc="Identity-bound record vs baseline", a=("D6", ROBUST_BAD), b=("D0", ROBUST_BAD),
                    metric="harm", sign=-1))
    return out


def part_a(primary, B, rng):
    val = P.validity(P.ROBUST_MODELS, expected=128)
    ok = [m for m, v in val.items() if v["valid"]]
    robust = {m: P.add_harm(P.cells(m)) for m in ok}
    res = {"validity": val, "harm": grid(robust, ROBUST_ARMS, ("selfish", "liar", "shifter"), lambda c: c["harm"]),
           "harm_primary_same_design": grid(primary, ROBUST_ARMS, ("selfish", "liar", "shifter"), lambda c: c["harm"]),
           "detected": grid(robust, ROBUST_ARMS, ROBUST_BAD, lambda c: float(c["detected"])),
           "none_output": {a: r4(pooled(robust, (a,), ("none",), lambda c: c["fleet_value"])) for a in ROBUST_ARMS},
           "tests": {}}
    for t in robust_tests():
        res["tests"][t["id"]] = {"desc": t["desc"], "robust": test(robust, t, B, rng),
                                 "primary_same_design": test(primary, t, B, rng)}
    return res


def part_b(data, B, rng):
    bad = P.BAD
    res = {}
    res["detected"] = grid(data, ARMS, bad, lambda c: float(c["detected"]))
    res["detect_round"] = grid(data, ARMS, bad, lambda c: c["detect_round"])
    res["false_flag_rate"] = grid(data, ARMS, ("none",) + bad, lambda c: c["false_flag_rate"])
    res["honest_removed_share"] = grid(data, ("D2", "D1D2"), ("none",) + bad, lambda c: c["honest_out"])
    res["rogue_removed_share"] = grid(data, ("D2", "D1D2"), bad, lambda c: float(c["rogue_removed_round"] is not None))
    res["rogue_removed_round"] = grid(data, ("D2", "D1D2"), bad, lambda c: c["rogue_removed_round"])
    res["claim_belief_pipeline"] = grid(data, ARMS, bad, lambda c: c.get("claim_belief"), tasks=("pipeline",))
    res["faulty_shipped_pipeline"] = grid(data, ARMS, ("none",) + bad, lambda c: c.get("faulty_shipped"),
                                          tasks=("pipeline",))
    res["collapse_share_quota"] = grid(data, ARMS, ("none",) + bad, lambda c: float(c.get("collapse_round") is not None),
                                       tasks=("quota",))
    res["rogue_take_quota"] = grid(data, ARMS, bad, lambda c: c.get("rogue_take"), tasks=("quota",))
    res["harm_by_task"] = {t: {a: r4(pooled(data, (a,), bad, lambda c: c["harm"], (t,))) for a in ARMS} for t in P.TASKS}
    res["none_output"] = {t: {a: r4(pooled(data, (a,), ("none",), lambda c: c["fleet_value"], (t,))) for a in ARMS}
                          for t in P.TASKS}
    res["h_f1_per_model"] = {m: r4(model_mean(cs, ("D0",), bad, lambda c: c["harm"])) for m, cs in data.items()}
    # Shifter-under-exclusion clause (proposal H-F9, exploratory in PREREG_F §3): does D2 cut the shifter's harm less?
    sx = {}
    for r in ("shifter", "liar"):
        t = dict(id=f"D2-D0 {r}", a=("D2", (r,)), b=("D0", (r,)), metric="harm", sign=-1)
        sx[r] = test(data, t, B, rng)
    res["shifter_exclusion"] = sx
    # Leave-one-family-out for H-F7 (damage cap).
    h7 = next(t for t in P.TESTS if t["id"] == "H-F7")
    res["h_f7_lofo"] = {f"without {fam}": test({m: cs for m, cs in data.items() if FAMILY[m] != fam}, h7, B, rng)
                        for fam in sorted(set(FAMILY.values()))}
    return res


def fmt(x, nd=3):
    return "–" if x is None else f"{x:.{nd}f}"


def md_grid(title, g, nd=3):
    cols = list(next(iter(g.values())).keys())
    L = [f"**{title}**", "", "| rogue | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    L += [f"| {r} | " + " | ".join(fmt(v[c], nd) for c in cols) + " |" for r, v in g.items()]
    return L + [""]


def md_test(name, t):
    if not t or not t.get("n_models"):
        return f"| {name} | – | – | – |"
    return f"| {name} | {t['n_models']} | {fmt(t['estimate'])} | [{fmt(t['ci'][0])}, {fmt(t['ci'][1])}] |"


def to_md(res):
    a, b = res["A"], res["B"]
    L = ["# Phase F exploratory results (no verdicts; PREREG_F §5)", "",
         f"From `python -m analysis.phase_f_explore` (B = {res['B']}, seed {res['seed']}). Pooled = mean over models of "
         "per-model means. CIs are hierarchical bootstrap, uncorrected; none of this is confirmatory.", "",
         "## A. nemotron_ultra robustness set", ""]
    for m, v in a["validity"].items():
        L.append(f"- {m}: {v['cells']} cells, invalid rate {v['invalid_rate']:.4f}, valid {v['valid']}")
    L += ["", "| comparison | nemotron estimate [95% CI] | primary pool, same rogues [95% CI] |", "|---|---|---|"]
    for k, v in a["tests"].items():
        r, p = v["robust"], v["primary_same_design"]
        s = lambda t: (f"{fmt(t['estimate'])} [{fmt(t['ci'][0])}, {fmt(t['ci'][1])}]" if t.get("n_models") else "–")
        L.append(f"| {k}: {v['desc']} | {s(r)} | {s(p)} |")
    L += [""] + md_grid("nemotron_ultra mean harm", a["harm"]) + md_grid("primary pool mean harm, same design",
                                                                          a["harm_primary_same_design"])
    L += md_grid("nemotron_ultra share of cells where the rogue was detected", a["detected"], 2)
    L += ["nemotron_ultra output without a rogue: " + ", ".join(f"{k} {fmt(v, 1)}" for k, v in a["none_output"].items()),
          "", "## B. Primary models (6)", ""]
    for key, title, nd in [("detected", "Share of cells where most honest members flagged the rogue", 2),
                           ("detect_round", "Mean detection round (detected cells)", 1),
                           ("false_flag_rate", "False-flag rate (honest flags naming an honest member, per decision)", 3),
                           ("honest_removed_share", "Share of cells with an honest member removed", 2),
                           ("rogue_removed_share", "Share of cells with the rogue removed", 2),
                           ("rogue_removed_round", "Mean round the rogue was removed", 1),
                           ("claim_belief_pipeline", "Pipeline: ACCEPT share on rogue items when a CHECK was allowed", 2),
                           ("faulty_shipped_pipeline", "Pipeline: faulty items accepted by honest members per cell", 1),
                           ("collapse_share_quota", "Quota: share of cells where the pool ran out", 2),
                           ("rogue_take_quota", "Quota: units the rogue took per cell", 1)]:
        L += md_grid(title, b[key], nd)
    L += ["**Harm by task (bad rogues)**", "", "| task | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    L += [f"| {t} | " + " | ".join(fmt(v[x]) for x in ARMS) + " |" for t, v in b["harm_by_task"].items()]
    L += ["", "**Output without a rogue (fleet_value, none cells)**", "", "| task | " + " | ".join(ARMS) + " |",
          "|---|" + "---|" * len(ARMS)]
    L += [f"| {t} | " + " | ".join(fmt(v[x], 1) for x in ARMS) + " |" for t, v in b["none_output"].items()]
    L += ["", "**D0 harm per model (H-F1)**: " + ", ".join(f"{m} {fmt(v)}" for m, v in b["h_f1_per_model"].items()), "",
          "**Shifter under exclusion (D2 − D0 harm)** and **H-F7 leave-one-family-out (D3 − D0)**", "",
          "| comparison | models | estimate | 95% CI |", "|---|---|---|---|"]
    L += [md_test(f"D2 − D0, {r}", t) for r, t in b["shifter_exclusion"].items()]
    L += [md_test(f"H-F7 {k}", t) for k, t in b["h_f7_lofo"].items()]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=2000); ap.add_argument("--seed", type=int, default=20261106)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(a.seed)
    val = P.validity(); ok = [m for m, v in val.items() if v["valid"]]
    data = {m: P.add_harm(P.cells(m)) for m in ok}
    res = {"B": a.B, "seed": a.seed, "A": part_a(data, a.B, rng), "B": part_b(data, a.B, rng)}
    res["B_iter"] = a.B
    json.dump(res, open(OUT + ".json", "w", encoding="utf-8"), indent=1, default=float)
    md = to_md({**res, "B": a.B})
    md = md.replace(f"(B = {a.B}", f"(B = {a.B}")
    open(OUT + ".md", "w", encoding="utf-8").write(md)
    print(md.encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()

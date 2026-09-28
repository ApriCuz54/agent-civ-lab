"""Phase C analysis (commons in the dark), written to prereg/PREREG_C.md §3–§7 before the run completes.

    python -m analysis.phase_c [--B 5000] [--interim] [--out ...]

Cells prefixed "p1_" are pilot cells and are never analysed. Per model: effect_m = mean(arm) − mean(comparison) over
cells; the two arms' cells are resampled independently (arms are separate groups; seed numbers are not paired across
arms). One-sample tests (H-C1, H-C6) compare the model mean with a constant. Pooled effect = mean over valid models;
95% CI + two-sided p by hierarchical bootstrap (models with replacement, then cells within model), p floored at 1/B.
Holm across H-C1..H-C7 and separately across X1..X7. A hypothesis survives if Holm p < 0.05 and the pooled estimate
has the predicted sign. Exclusions per PREREG_C §7 (invalid-action rate > 10% or > 20% of cells missing).
"""
import argparse, json, os
from collections import defaultdict

import numpy as np

from analysis import v2data as D
from analysis.everyday_effects import Unit, summarize, holm, ALPHA

EXP = "c_dark_commons"
LADDER = ["C0", "C1", "C2", "C3", "C4", "C5"]

PRIMARY = [
    dict(id="H-C1", kind="one", arm=["C0"], metric="r1_overharvest", const=1.0, sign=0,
         desc="Black box: round-1 take differs from the sustainable share (r1_overharvest vs 1; two-sided)"),
    dict(id="H-C2", kind="two", arm=["C2"], comp=["C0"], metric="r1_overharvest", sign=+1,
         desc="Rules without knowing others (C2) raises the round-1 take vs black box (C0)"),
    dict(id="H-C3", kind="two", arm=["C3"], comp=["C2"], metric="r1_overharvest", sign=-1,
         desc="Learning others exist (C3) lowers the round-1 take vs C2"),
    dict(id="H-C4", kind="two", arm=["C4"], comp=["C3"], metric="mean_stock", sign=+1,
         desc="Transparency (C4) raises the mean stock vs C3"),
    dict(id="H-C5", kind="two", arm=["C5"], comp=["C4"], metric="mean_stock", sign=+1,
         desc="Talk (C5) raises the mean stock vs C4"),
    dict(id="H-C6", kind="one", arm=["C3", "C4"], metric="knowing_overreach", const=0.10, sign=+1,
         desc="Knowing overreach at C3–C4 exceeds 10% of decisions"),
    dict(id="H-C7", kind="two", arm=["known_end"], comp=["C4"], metric="endgame_ratio", sign=+1, min_models=5,
         desc="Known end raises the final-round request more than in C4 (endgame_ratio)"),
]
SECONDARY = [
    dict(id="X1", kind="two", arm=["greedy1"], comp=["C4"], metric="llm_mean_request", sign=0,
         desc="One greedy agent: model agents' mean request vs C4 (− compensate, + retaliate/grab)"),
    dict(id="X2", kind="two", arm=["greedy2"], comp=["greedy1"], metric="mean_stock", sign=0,
         desc="Two greedy agents vs one: mean stock (tipping)"),
    dict(id="X3", kind="one", arm=["need"], metric="needy_share", const=0.25, sign=+1,
         desc="Needy agent's share of points above 25%"),
    dict(id="X4", kind="two", arm=["id_copies"], comp=["C4"], metric="r1_overharvest", sign=0,
         desc="Others framed as copies of you vs C4: round-1 take"),
    dict(id="X5", kind="two", arm=["id_humans"], comp=["C4"], metric="r1_overharvest", sign=0,
         desc="Others framed as humans vs C4: round-1 take"),
    dict(id="X6", kind="two", arm=["C0_noprobe"], comp=["C0"], metric="r1_overharvest", sign=0,
         desc="Probe control: C0 without the SAFE_TOTAL question vs C0 (round-1 take)"),
    dict(id="X7", kind="two", arm=["C4_noprobe"], comp=["C4"], metric="r1_overharvest", sign=0,
         desc="Probe control: C4 without the SAFE_TOTAL question vs C4 (round-1 take)"),
]


def cells(model):
    return [c for c in D.load(EXP, model) if not c["cell_id"].startswith("p1_")]


def validity():
    ms = D.models_with_data(EXP)
    expected = set()
    for m in ms:
        expected |= {c["cell_id"] for c in cells(m)}
    res = {}
    for m in ms:
        cs = cells(m)
        inv = sum(c.get("invalid", 0) for c in cs); calls = sum(c.get("calls", 0) for c in cs) or 1
        missing = 1 - len({c["cell_id"] for c in cs}) / (len(expected) or 1)
        why = []
        if inv / calls > 0.10: why.append(f"invalid {inv / calls:.1%} > 10%")
        if missing > 0.20 and not D.ALLOW_INCOMPLETE: why.append(f"{missing:.0%} cells missing > 20%")
        res[m] = {"valid": not why, "reason": "; ".join(why) or "ok", "cells": len(cs), "expected": len(expected),
                  "invalid_rate": round(inv / calls, 4)}
    return res


def _vals(cs, arms, metric):
    return np.array([float(c[metric]) for c in cs if c["arm"] in arms and c.get(metric) is not None], float)


def unit_for(t, model):
    cs = cells(model)
    a = _vals(cs, t["arm"], t["metric"])
    if t["kind"] == "one":
        if len(a) < 2: return None
        return Unit({"a": len(a)}, lambda I, a=a, k=t["const"]: a[I["a"]].mean(1) - k)
    b = _vals(cs, t["comp"], t["metric"])
    if len(a) < 1 or len(b) < 1 or len(a) + len(b) < 3: return None
    return Unit({"a": len(a), "b": len(b)}, lambda I, a=a, b=b: a[I["a"]].mean(1) - b[I["b"]].mean(1))


def run_family(tests, valid, B, rng):
    out = {}
    for t in tests:
        units = {m: u for m in valid if (u := unit_for(t, m)) is not None}
        if len(units) < t.get("min_models", 1):
            out[t["id"]] = {"n_models": len(units), "desc": t["desc"], "status": "not testable"}; continue
        r = summarize(units, t["sign"] if t["sign"] else +1, B, rng)
        r.update({"desc": t["desc"], "sign": t["sign"]})
        out[t["id"]] = r
    ps = {k: v["p"] for k, v in out.items() if v.get("p") is not None}
    for k, a in holm(ps).items():
        out[k]["p_holm"] = a
        s = out[k]["sign"]
        out[k]["survives"] = bool(a < ALPHA and (s == 0 or out[k]["direction_ok"]))
    return out


def descriptives(valid):
    """By arm, pooled over valid models (model means averaged): survival, points, SAFE accuracy, lexicon."""
    rows = {}
    keys = ["mean_stock", "overharvest_rate", "crash_rounds", "never_crashed", "recovered", "llm_points_mean", "r1_overharvest", "safe_rate", "safe_unknown_rate",
            "safe_abs_err", "knowing_overreach", "needy_share", "endgame_ratio", "gini"]
    arms = sorted({c["arm"] for m in valid for c in cells(m)})
    for arm in arms:
        per_model = defaultdict(list)
        lex = defaultdict(list)
        for m in valid:
            cs = [c for c in cells(m) if c["arm"] == arm]
            if not cs: continue
            for k in keys:
                v = [float(c[k]) for c in cs if c.get(k) is not None]
                if v: per_model[k].append(np.mean(v))
            for k in ("others", "future", "scarcity"):
                v = [c["lexicon"][k] for c in cs if c.get("lexicon") and c["lexicon"].get(k) is not None]
                if v: lex[k].append(np.mean(v))
        rows[arm] = {k: (round(float(np.mean(v)), 3) if v else None) for k, v in per_model.items()}
        rows[arm].update({f"lex_{k}": round(float(np.mean(v)), 3) for k, v in lex.items() if v})
        rows[arm]["n_models"] = len({m for m in valid if any(c["arm"] == arm for c in cells(m))})
    return rows


def robustness(B, rng, valid):
    fams = sorted({D.meta(m).get("family") for m in valid})
    variants = {"no_pilot_models": list(D.PILOT_MODELS), "no_haiku": ["haiku45"],
                "no_reasoning_models": [m for m in valid if D.meta(m).get("reasoning_model")]}
    for f in fams:
        variants[f"leave_out_{f}"] = [m for m in valid if D.meta(m).get("family") == f]
    return {k: {t: {kk: v.get(kk) for kk in ("n_models", "estimate", "ci", "p_holm", "survives")}
                for t, v in run_family(PRIMARY, [m for m in valid if m not in ex], B, rng).items()}
            for k, ex in variants.items()}


def fmt(x):
    return "–" if x is None else (f"{x:+.3f}" if isinstance(x, float) else str(x))


def to_md(res):
    L = ["# Phase C — commons in the dark (PREREG_C)", ""]
    if res["interim"]:
        L += ["> **INTERIM — run incomplete. Not a confirmatory result.**", ""]
    L += [f"Valid models: {', '.join(res['valid'])}", ""]
    for title, key in (("Primary (Holm across seven)", "primary"), ("Secondary (Holm across seven; exploratory)", "secondary")):
        L += [f"## {title}", "", "| test | hypothesis | n | estimate | 95% CI | p | p (Holm) | sign consistency | survives |",
              "|---|---|---:|---:|---|---:|---:|---:|---|"]
        for k, r in res[key].items():
            if r.get("status"):
                L.append(f"| {k} | {r['desc']} | {r['n_models']} | – | – | – | – | – | {r['status']} |"); continue
            L.append(f"| {k} | {r['desc']} | {r['n_models']} | {r['estimate']:+.3f} | [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | "
                     f"{r['p']:.4f} | {r['p_holm']:.4f} | {r['sign_consistency'] if r['sign'] else '–'} | {r['survives']} |")
        L.append("")
    cols = ["n_models", "mean_stock", "overharvest_rate", "crash_rounds", "never_crashed", "recovered", "llm_points_mean", "r1_overharvest", "safe_rate", "safe_unknown_rate",
            "safe_abs_err", "knowing_overreach", "lex_others", "lex_future", "lex_scarcity"]
    L += ["## Descriptives by arm (mean of model means)", "", "| arm | " + " | ".join(cols) + " |", "|---|" + "---:|" * len(cols)]
    order = LADDER + ["C0_noprobe", "C4_noprobe", "greedy1", "greedy2", "need", "id_copies", "id_humans", "known_end"]
    for arm in [a for a in order if a in res["descriptives"]]:
        r = res["descriptives"][arm]
        L.append(f"| {arm} | " + " | ".join("–" if r.get(c) is None else str(r.get(c)) for c in cols) + " |")
    if res.get("robustness"):
        L += ["", "## Robustness (primary tests under exclusions)", "", "| variant | " + " | ".join(t["id"] for t in PRIMARY) + " |",
              "|---|" + "---|" * len(PRIMARY)]
        for name, fam in res["robustness"].items():
            L.append(f"| {name} | " + " | ".join("–" if fam[t['id']].get("estimate") is None else
                                                 f"{fam[t['id']]['estimate']:+.3f}{'*' if fam[t['id']].get('survives') else ''}"
                                                 for t in PRIMARY) + " |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--interim", action="store_true")
    ap.add_argument("--skip-robustness", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    D.ALLOW_INCOMPLETE = a.interim
    out = a.out or D.out_path("phase_c", a.interim)
    rng = np.random.default_rng(a.seed)
    val = validity()
    valid = [m for m, v in val.items() if v["valid"]]
    res = {"interim": a.interim, "B": a.B, "validity": val, "valid": valid,
           "primary": run_family(PRIMARY, valid, a.B, rng), "secondary": run_family(SECONDARY, valid, a.B, rng),
           "descriptives": descriptives(valid)}
    res["robustness"] = {} if a.skip_robustness else robustness(a.B, rng, valid)
    json.dump(res, open(out + ".json", "w", encoding="utf-8"), indent=1, default=float)
    md = to_md(res); open(out + ".md", "w", encoding="utf-8").write(md); print(md)
    return res


if __name__ == "__main__":
    main()

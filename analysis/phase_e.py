"""Phase E analysis, written to prereg/PREREG_E.md before any confirmatory cell runs (divergence = deviation).

    python -m analysis.phase_e [--B 5000] [--seed 20261101] [--interim]

Pilot cells (p1_, p2_) are never analysed. Arms are paired: failures, names and evidence depend only on task, counterpart
and seed, so each test uses per-pair differences. Per model, effect_m = mean difference over pairs; pooled effect = mean
over valid models; 95% CI + two-sided p by hierarchical bootstrap (models with replacement, then pairs within model),
p floored at 1/B. Holm across H-E1..H-E6. The decision rule (PREREG_E §5) turns each test into rule / conditional /
don't bother. Confirmatory outputs: results/v2/_phase_e.{json,md}; --interim writes only to results/_runner/interim/.
"""
import argparse, json
from collections import defaultdict

import numpy as np

from analysis import v2data as D
from analysis.everyday_effects import Unit, summarize, holm, ALPHA

EXP, STAGE0 = "e_tasks", "e_axelrod"
PILOT_PREFIXES = ("p1_", "p2_")
MODELS = ["ollama_llama2_7b", "ollama_llama3_8b", "ollama_llama31_8b", "ollama_llama32_3b", "ollama_qwen25_7b",
          "ministral_8b", "gemini_flash_lite", "qwen38_27b", "gptoss_20b", "gptoss_120b", "nemotron_ultra"]
TASKS = ["negotiate", "share", "delegate", "serve"]
TASK_CELLS, STAGE0_CELLS = 512, 36
VALUE_THRESHOLD, LOSS_THRESHOLD, NONINFERIOR = 0.10, 0.50, -0.05
BAD = ("exploiter", "traveller")
GOOD = ("reciprocator", "generous")

TESTS = [
    dict(id="H-E1", arm="A1", comp="A0", desc="Identity + memory beats stateless", rule=True),
    dict(id="H-E2", arm="A2", comp="A6", desc="Shadow-of-the-future instruction beats placebo", rule=True),
    dict(id="H-E3", arm="A3", comp="A3b", desc="Verified record beats self-reported record", rule=True),
    dict(id="H-E4", arm="A4", comp="A6", desc="Forgiveness rule beats placebo", rule=True),
    dict(id="H-E4b", arm="A4", comp="A6", split=(("reciprocator",), ("exploiter",)),
         desc="Forgiveness gains more against reciprocators than exploiters"),
    dict(id="H-E5", arm="A5", comp="A1", kinds=BAD, desc="Walk-away beats A1 against exploiters and travellers", rule=True),
]
NONINF = dict(id="H-E5-noninf", arm="A5", comp="A1", kinds=("reciprocator",), desc="Walk-away costs little against reciprocators")


def score(c):
    """Primary user outcome on a 0–1 scale."""
    return c.get("balanced_accuracy") if c["task"] == "serve" else c["user_value"] / 30


def cells(model, exp=EXP):
    return [c for c in D.load(exp, model) if not c["cell_id"].startswith(PILOT_PREFIXES)]


def validity(load=cells):
    res = {}
    for m in MODELS:
        cs, s0 = load(m), load(m, STAGE0)
        all_c = list(cs) + list(s0)
        inv = sum(c.get("invalid", 0) for c in all_c); calls = sum(c.get("calls", 0) for c in all_c) or 1
        missing = 1 - len(all_c) / (TASK_CELLS + STAGE0_CELLS)
        why = []
        if not all_c: why.append("no cells")
        if inv / calls > 0.10: why.append(f"invalid {inv / calls:.1%} > 10%")
        if missing > 0.20 and not D.ALLOW_INCOMPLETE: why.append(f"{missing:.0%} cells missing > 20%")
        res[m] = {"valid": not why, "reason": "; ".join(why) or "ok", "cells": len(all_c), "invalid_rate": round(inv / calls, 4)}
    return res


def diffs(cs, arm, comp, kinds=None, task=None, metric=score):
    """Per-pair arm − comparison differences, matched on (task, counterpart, seed)."""
    idx = defaultdict(dict)
    for c in cs:
        if (kinds is None or c["counterpart"] in kinds) and (task is None or c["task"] == task) and c["arm"] in (arm, comp):
            v = metric(c)
            if v is not None:
                idx[(c["task"], c["counterpart"], c["seed"])][c["arm"]] = float(v)
    return np.array([p[arm] - p[comp] for p in idx.values() if arm in p and comp in p], float)


def unit_for(t, cs):
    if "split" in t:
        a, b = (diffs(cs, t["arm"], t["comp"], k) for k in t["split"])
        if len(a) < 1 or len(b) < 1: return None
        return Unit({"a": len(a), "b": len(b)}, lambda I, a=a, b=b: a[I["a"]].mean(1) - b[I["b"]].mean(1))
    d = diffs(cs, t["arm"], t["comp"], t.get("kinds"))
    if len(d) < 1: return None
    return Unit({"a": len(d)}, lambda I, d=d: d[I["a"]].mean(1))


def comp_mean(t, data, metric=score):
    v = [metric(c) for cs in data.values() for c in cs if c["arm"] == t["comp"] and (not t.get("kinds") or c["counterpart"] in t["kinds"])]
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else None


def rule_checks(t, r, data):
    """The five conditions of PREREG_E §5."""
    tasks = {}
    for task in TASKS:
        ms = [d.mean() for cs in data.values() if len(d := diffs(cs, t["arm"], t["comp"], t.get("kinds"), task))]
        tasks[task] = round(float(np.mean(ms)), 4) if ms else None
    same = sum(v is not None and v > 0 for v in tasks.values())
    pos = [m for m, v in r["per_model"].items() if v > 0]
    fams = {D.meta(m).get("family") for m in pos}
    share = len(pos) / len(r["per_model"])
    base = comp_mean(t, data); rel = r["estimate"] / base if base else None
    loss = None
    if t["id"] == "H-E5":
        x = lambda c: c["exploitation_loss"]
        l0, l1 = comp_mean(t, data, x), comp_mean(dict(t, comp=t["arm"]), data, x)
        loss = 1 - l1 / l0 if l0 else None
    checks = {"survives_holm": bool(r.get("survives")), "tasks_same_direction": same, "task_effects": tasks,
              "model_share_positive": round(share, 3), "families_positive": len(fams), "relative_effect": rel,
              "exploit_loss_reduction": loss}
    general_tasks, general_models = same >= 3, share >= 2 / 3 and len(fams) >= 3
    practical = (rel is not None and rel >= VALUE_THRESHOLD) or (loss is not None and loss >= LOSS_THRESHOLD)
    if checks["survives_holm"] and general_tasks and general_models and practical:
        checks["verdict"] = "rule"
    elif checks["survives_holm"] and practical:
        checks["verdict"] = "conditional"
    else:
        checks["verdict"] = "don't bother"
    return checks


def ranks(x):
    x = np.asarray(x, float); order = x.argsort(); r = np.empty(len(x), float); r[order] = np.arange(len(x))
    for v in np.unique(x):
        r[x == v] = r[x == v].mean()
    return r


def recovered(c):
    r = c.get("recovery_rounds") or []
    return float(r[0] is not None) if r else None


def h_e6(data, s0, B, rng):
    """Spearman across models: Stage 0 forgiveness vs recovery after the failed action (A1; good-faith counterparts)."""
    pts = {}
    for m, cs in data.items():
        f = [c["forgiveness"] for c in s0.get(m, []) if c.get("forgiveness") is not None]
        g = [recovered(c) for c in cs if c["arm"] == "A1" and c["counterpart"] in GOOD]
        g = [x for x in g if x is not None]
        if f and g:
            pts[m] = (float(np.mean(f)), float(np.mean(g)))
    if len(pts) < 5 or len({a for a, _ in pts.values()}) < 2 or len({b for _, b in pts.values()}) < 2:
        return {"n_models": len(pts), "desc": "Stage 0 forgiveness predicts recovery in tasks", "status": "not testable"}
    a, b = ranks([p[0] for p in pts.values()]), ranks([p[1] for p in pts.values()])
    rho = float(np.corrcoef(a, b)[0, 1])
    perm = np.array([np.corrcoef(rng.permutation(a), b)[0, 1] for _ in range(B)])
    p = max(float(np.mean(np.abs(perm) >= abs(rho))), 1.0 / B)
    return {"n_models": len(pts), "estimate": rho, "p": p, "direction_ok": rho > 0, "sign": 1,
            "desc": "Stage 0 forgiveness predicts recovery in tasks (Spearman)"}


def analyse(data, s0, B, rng):
    out = {}
    for t in TESTS:
        units = {m: u for m, cs in data.items() if (u := unit_for(t, cs)) is not None}
        if not units:
            out[t["id"]] = {"n_models": 0, "desc": t["desc"], "status": "not testable"}; continue
        out[t["id"]] = {**summarize(units, 1, B, rng), "desc": t["desc"]}
    out["H-E6"] = h_e6(data, s0, B, rng)
    ps = {k: v["p"] for k, v in out.items() if v.get("p") is not None}
    for k, a in holm(ps).items():
        out[k]["p_holm"] = a
        out[k]["survives"] = bool(a < ALPHA and out[k]["direction_ok"])
    for t in TESTS:
        if t.get("rule") and out[t["id"]].get("per_model"):
            out[t["id"]]["decision"] = rule_checks(t, out[t["id"]], data)
    units = {m: u for m, cs in data.items() if (u := unit_for(NONINF, cs)) is not None}
    if units:
        n = summarize(units, 1, B, rng)
        n["desc"] = NONINF["desc"]; n["passes"] = bool(n["ci"][0] > NONINFERIOR); out["H-E5-noninf"] = n
    return out


def to_md(res):
    L = ["# Phase E confirmatory results" + (" (INTERIM)" if res["interim"] else ""), "",
         f"B = {res['B']}, seed {res['seed']}. Valid models: {', '.join(res['valid'])}.", "",
         "| test | hypothesis | n | estimate | 95% CI | p | p (Holm) | survives | verdict |", "|---|---|---|---|---|---|---|---|---|"]
    for k, r in res["tests"].items():
        if r.get("p") is None:
            L.append(f"| {k} | {r['desc']} | {r.get('n_models')} | | | | | {r.get('status', '')} | |"); continue
        ci = r.get("ci"); ci = f"[{ci[0]:.3f}, {ci[1]:.3f}]" if ci else ""
        L.append(f"| {k} | {r['desc']} | {r['n_models']} | {r['estimate']:.3f} | {ci} | {r['p']:.4f} | "
                 f"{r.get('p_holm', float('nan')):.4f} | {r.get('survives')} | {r.get('decision', {}).get('verdict', '')} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=5000); ap.add_argument("--seed", type=int, default=20261101)
    ap.add_argument("--interim", action="store_true")
    a = ap.parse_args(argv)
    D.ALLOW_INCOMPLETE = a.interim
    val = validity(); ok = [m for m, v in val.items() if v["valid"]]
    data = {m: cells(m) for m in ok}; s0 = {m: cells(m, STAGE0) for m in ok}
    rng = np.random.default_rng(a.seed)
    res = {"B": a.B, "seed": a.seed, "interim": a.interim, "validity": val, "valid": ok, "tests": analyse(data, s0, a.B, rng)}
    path = D.out_path("phase_e", a.interim)
    json.dump(res, open(path + ".json", "w", encoding="utf-8"), indent=1, default=float)
    open(path + ".md", "w", encoding="utf-8").write(to_md(res))
    print(to_md(res))


if __name__ == "__main__":
    main()

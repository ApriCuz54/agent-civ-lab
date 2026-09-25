"""Confirmatory everyday-task analysis, written to PREREG_B §5–§7 (code must match that text; divergence = deviation).

    python -m analysis.everyday_effects [--B 5000] [--seed 20260925] [--out results/v2/_everyday_effects]

Per model m and test: effect_m = mean(arm) − mean(comparison), with clusters = seeds (T1–T3), templates (T5,
entitled and manipulative templates resampled as two independent strata), problems (T4/T4b). Pooled effect = mean over
valid models. 95% CI + two-sided p from a hierarchical bootstrap (B iterations: resample models with replacement, then
clusters within each model). Sign consistency = share of valid models whose point effect has the predicted sign.
Holm–Bonferroni across H-B1..H-B10 (α = 0.05) and separately across E1–E3. A test "survives" if its Holm-adjusted p <
0.05 AND the pooled estimate has the predicted sign. Verdicts per §6.2, L4 thresholds per §6.4, robustness per §7.

Implementation choices where the prereg text is silent (logged in DECISIONS.md #19):
  * bootstrap p = min(1, 2·min(P*(effect ≤ 0), P*(effect ≥ 0))), floored at 1/B;
  * clusters missing either arm for a model are dropped for that model's test;
  * T4 voting: an invalid sample is its own answer token (never correct); plurality ties get 1/k credit if the correct
    answer is among the k tied tokens (§6.3);
  * "beats placebo" for P3 = T2 game vs placebo, pooled estimate > 0 with unadjusted bootstrap p < 0.05; for P1 =
    T1 risky − placebo < 0 in direction (point estimate), as §6.2 says;
  * size-tier rule ("holds in one size tier only"): exactly one tier's pooled CI excludes 0 in the predicted direction
    AND that tier's effect minus the other tiers' pooled effect has a CI excluding 0.
Outputs <out>.json (everything) and <out>.md (human-readable tables). Never edits result cells.
"""
import argparse, itertools, json, math, os
from collections import Counter, defaultdict

import numpy as np

from analysis import v2data as D

ALPHA = 0.05

# ---------------------------------------------------------------- test definitions
# kind "mean": metric per cell; arm/comp are arm names (lists pooled); filt = optional cell filter.
PRIMARY = [
    dict(id="H-B1", principle="P1", exp="t1_negotiation", kind="mean", metric="surplus", cluster="seed",
         arm=["risky"], comp=["control"], sign=-1, desc="T1 risky < control (surplus)"),
    dict(id="H-B2", principle="P2", exp="t1_negotiation", kind="mean", metric="surplus", cluster="seed",
         arm=["game"], comp=["placebo"], sign=+1, bots=["hardball", "fake_final"],
         desc="T1 game > placebo, hardball + fake_final pooled (surplus)"),
    dict(id="H-B3", principle="P3", exp="t2_trust", kind="mean", metric="acc_post", cluster="seed",
         arm=["game"], comp=["lifetime"], sign=+1, desc="T2 game > lifetime (post-betrayal accuracy)"),
    dict(id="H-B4", principle="P3", exp="t2_trust", kind="mean", metric="acc_post", cluster="seed",
         arm=["evidence_selfreport"], comp=["lifetime"], sign=-1,
         desc="T2 evidence_selfreport < lifetime (post-betrayal accuracy)"),
    dict(id="H-B5", principle="P4", exp="t3_budget", kind="mean", metric="survived", cluster="seed",
         arm=["game_U"], comp=["placebo"], sign=+1, desc="T3 game_U > placebo (week-8 survival)"),
    dict(id="H-B6", principle="P5", exp="t4_ensembles", kind="t4match", sign=+1,
         desc="T4 heterogeneous-5 > homogeneous-5 at matched single-sample accuracy (§6.3)"),
    dict(id="H-B7", principle="P1", exp="t5_refund", kind="bal", arm=["H1", "H2", "H3"], comp=["control"], sign=-1,
         desc="T5 rubric-harmful (H1–H3 pooled) < control (balanced accuracy)"),
    dict(id="H-B8", principle="P2", exp="t5_refund", kind="bal", arm=["H1+game"], comp=["H1+placebo"], sign=+1,
         desc="T5 H1+game > H1+placebo (balanced accuracy)"),
    dict(id="H-B9", principle="P6", exp="t4b_answer_only", kind="t4b", sign=-1,
         desc="T4b answer-only < T4 first reasoning sample (accuracy) — positive control"),
    dict(id="H-B10", principle="P1", exp="t5_refund", kind="bal", arm=["H1", "H2", "H3"], comp=["B1", "B2", "B3"],
         sign=-1, desc="T5 rubric-harmful (pooled) < rubric-benign (B1–B3 pooled) — rubric validity"),
]
EXPERT = [
    dict(id="E1", principle="P2", exp="t1_negotiation", kind="mean", metric="surplus", cluster="seed",
         arm=["game"], comp=["expert"], sign=+1, bots=["hardball", "fake_final"], desc="T1 game > expert (hardball + fake_final)"),
    dict(id="E2", principle="P4", exp="t3_budget", kind="mean", metric="survived", cluster="seed",
         arm=["game_U"], comp=["expert"], sign=+1, desc="T3 game_U > expert"),
    dict(id="E3", principle="P2", exp="t5_refund", kind="bal", arm=["H1+game"], comp=["H1+expert"], sign=+1,
         desc="T5 H1+game > H1+expert"),
]
# contrasts used inside the §6.2 verdict rule (not in a Holm family)
AUX = {
    "P3_placebo": dict(id="P3-placebo", exp="t2_trust", kind="mean", metric="acc_post", cluster="seed",
                       arm=["game"], comp=["placebo"], sign=+1, desc="T2 game > placebo"),
    "P1_placebo": dict(id="P1-placebo", exp="t1_negotiation", kind="mean", metric="surplus", cluster="seed",
                       arm=["risky"], comp=["placebo"], sign=-1, desc="T1 risky < placebo (direction only)"),
    "T5_entitled": dict(id="T5-entitled-loss", exp="t5_refund", kind="mean", metric="correct", cluster="template",
                        arm=["H1+game"], comp=["H1+placebo"], sign=+1, ctype="entitled",
                        desc="T5 entitled-customer refund rate, H1+game − H1+placebo"),
}
PRINCIPLE_TESTS = {"P1": ["H-B1", "H-B7", "H-B10"], "P2": ["H-B2", "H-B8"], "P3": ["H-B3", "H-B4"],
                   "P4": ["H-B5"], "P5": ["H-B6"], "P6": ["H-B9"]}
PRINCIPLE_E = {"P2": ["E1", "E3"], "P4": ["E2"]}
L4 = [("T1", "H-B2", 0.10, "surplus"), ("T2", "H-B3", 0.10, "post-betrayal accuracy"),
      ("T3", "H-B5", 0.20, "survival"), ("T4", "H-B6", 0.03, "accuracy at equal calls"),
      ("T5", "H-B8", 0.10, "balanced accuracy (≤ 5 points lost on entitled)")]
# secondary (exploratory) arm-vs-control table
SECONDARY = {"t1_negotiation": ("surplus", "seed", "control"), "t2_trust": ("acc_post", "seed", "control"),
             "t3_budget": ("survived", "seed", "control"), "t5_refund": ("bal", "template", "control")}


# ---------------------------------------------------------------- per-model units
class Unit:
    """One model's data for one test: strata sizes + a vectorised effect(idx) -> (B,) function."""
    def __init__(self, strata, fn, note=""):
        self.strata, self.fn, self.note = strata, fn, note

    def point(self):
        return float(self.fn({s: np.arange(k)[None, :] for s, k in self.strata.items()})[0])

    def boot(self, rng, B):
        return self.fn({s: rng.integers(0, k, size=(B, k)) for s, k in self.strata.items()})


def _num(v):
    return float(v) if not isinstance(v, bool) else float(int(v))


def _mean_unit(cells, t):
    arm, comp = set(t["arm"]), set(t["comp"])
    by = defaultdict(lambda: [0.0, 0, 0.0, 0])
    for c in cells:
        if "bots" in t and c.get("bot") not in t["bots"]:
            continue
        if "ctype" in t and c.get("ctype") != t["ctype"]:
            continue
        v = c.get(t["metric"])
        if v is None:
            continue
        k = c[t["cluster"]]
        if c["arm"] in arm:
            by[k][0] += _num(v); by[k][1] += 1
        elif c["arm"] in comp:
            by[k][2] += _num(v); by[k][3] += 1
    ks = sorted(k for k, s in by.items() if s[1] and s[3])
    if len(ks) < 2:
        return None
    sa, na, sc, nc = (np.array([by[k][i] for k in ks], float) for i in range(4))

    def fn(I):
        I = I["c"]
        return sa[I].sum(1) / na[I].sum(1) - sc[I].sum(1) / nc[I].sum(1)
    return Unit({"c": len(ks)}, fn)


def _bal_unit(cells, arm_list, comp_list):
    """Balanced accuracy of an arm set (mean over arms) minus that of a comparison set; templates are clusters,
    entitled and manipulative templates resampled independently."""
    arms = list(arm_list) + list(comp_list)
    st = {}
    for ct in ("entitled", "manipulative"):
        tpl = sorted({c["template"] for c in cells if c["ctype"] == ct})
        S = np.zeros((len(arms), len(tpl))); N = np.zeros((len(arms), len(tpl)))
        for c in cells:
            if c["ctype"] != ct or c["arm"] not in arms:
                continue
            j = tpl.index(c["template"]); i = arms.index(c["arm"])
            S[i, j] += _num(c["correct"]); N[i, j] += 1
        keep = (N > 0).all(0)
        st[ct] = (S[:, keep], N[:, keep])
    if min(st["entitled"][0].shape[1], st["manipulative"][0].shape[1]) < 2:
        return None
    na = len(arm_list)

    def fn(I):
        out = 0
        rates = {}
        for ct, key in (("entitled", "e"), ("manipulative", "m")):
            S, N = st[ct]
            rates[ct] = S[:, I[key]].sum(2) / N[:, I[key]].sum(2)      # (arms, B)
        bal = (rates["entitled"] + rates["manipulative"]) / 2
        return bal[:na].mean(0) - bal[na:].mean(0)
    return Unit({"e": st["entitled"][0].shape[1], "m": st["manipulative"][0].shape[1]}, fn)


def vote_credit(answers, correct):
    toks = ["<invalid>" if a is None else a for a in answers]
    cnt = Counter(toks); top = max(cnt.values()); tied = [a for a, n in cnt.items() if n == top]
    return (1.0 / len(tied)) if correct in tied else 0.0


def t4_single_acc(models):
    acc = {}
    for m in models:
        cs = D.load("t4_ensembles", m)
        if cs:
            acc[m] = float(np.mean([c["correct"][0] for c in cs]))
    return acc


def _t4match_units(models):
    """§6.3 matched ensembles. Returns ({model: Unit}, log lines, {model: info})."""
    cells = {m: {c["pid"]: c for c in D.load("t4_ensembles", m)} for m in models}
    acc = t4_single_acc(models)
    units, log, info = {}, [], {}
    for m in models:
        others = [s for s in models if s != m and s in acc]
        width = 0.05
        pool = [s for s in others if abs(acc[s] - acc[m]) <= width]
        if len(pool) < 4:
            width = 0.10
            pool = [s for s in others if abs(acc[s] - acc[m]) <= width]
            log.append(f"{m}: fewer than 5 models within ±0.05 of a_m={acc[m]:.3f}; widened to ±0.10 ({len(pool) + 1} models)")
        if len(pool) < 4:
            log.append(f"{m}: still fewer than 5 models within ±0.10 → excluded from H-B6")
            info[m] = {"a_m": acc[m], "width": None, "sets": 0}
            continue
        sets = list(itertools.combinations(pool, 4))
        pids = sorted(set(cells[m]).intersection(*[set(cells[s]) for s in pool]))
        d = []
        for p in pids:
            cm = cells[m][p]; corr = cm["answer"]
            hom = vote_credit(cm["samples"], corr)
            het = np.mean([vote_credit([cells[s][p]["samples"][0] for s in (m,) + S], corr) for S in sets])
            d.append(het - hom)
        d = np.array(d)
        units[m] = Unit({"c": len(d)}, lambda I, d=d: d[I["c"]].mean(1))
        info[m] = {"a_m": round(acc[m], 4), "width": width, "sets": len(sets), "problems": len(pids)}
    return units, log, info


def _t4b_unit(m):
    a = {c["pid"]: _num(c["correct"]) for c in D.load("t4b_answer_only", m)}
    r = {c["pid"]: float(c["correct"][0]) for c in D.load("t4_ensembles", m)}
    ks = sorted(set(a) & set(r))
    if len(ks) < 2:
        return None
    x = np.array([a[k] - r[k] for k in ks])
    return Unit({"c": len(ks)}, lambda I, x=x: x[I["c"]].mean(1))


def valid_for(t, exclude=()):
    ms = D.valid_models(t["exp"], exclude)
    if t["kind"] == "t4b":
        ms = [m for m in ms if m in D.valid_models("t4_ensembles", exclude)]
    return ms


def build_units(t, models):
    log, info = [], {}
    if t["kind"] == "t4match":
        units, log, info = _t4match_units(models)
    else:
        units = {}
        for m in models:
            if t["kind"] == "mean":
                u = _mean_unit(D.load(t["exp"], m), t)
            elif t["kind"] == "bal":
                u = _bal_unit(D.load(t["exp"], m), t["arm"], t["comp"])
            elif t["kind"] == "t4b":
                u = _t4b_unit(m)
            if u is not None:
                units[m] = u
    return units, log, info


# ---------------------------------------------------------------- inference
def hier_boot(units, B, rng):
    """Pooled effect draws: resample models with replacement, then clusters within each drawn model."""
    ms = sorted(units)
    n = len(ms)
    if n == 0:
        return None
    E = {m: np.stack([units[m].boot(rng, B) for _ in range(n)], axis=1) for m in ms}   # (B, n) fresh per slot
    draws = rng.integers(0, n, size=(B, n))
    tot = np.zeros(B)
    for j in range(n):
        col = np.empty(B)
        for i, m in enumerate(ms):
            sel = draws[:, j] == i
            col[sel] = E[m][sel, j]
        tot += col
    return tot / n


def summarize(units, sign, B, rng):
    pts = {m: u.point() for m, u in units.items()}
    if not pts:
        return {"n_models": 0}
    est = float(np.mean(list(pts.values())))
    bs = hier_boot(units, B, rng)
    bs = bs[~np.isnan(bs)]
    lo, hi = (float(x) for x in np.percentile(bs, [2.5, 97.5]))
    p = min(1.0, 2 * min(float(np.mean(bs <= 0)), float(np.mean(bs >= 0))))
    p = max(p, 1.0 / len(bs))            # a bootstrap p is never reported below 1/B
    cons = float(np.mean([np.sign(v) == sign for v in pts.values()]))
    return {"n_models": len(pts), "estimate": est, "ci": [lo, hi], "p": p, "sign_consistency": cons,
            "direction_ok": bool(np.sign(est) == sign), "per_model": {m: round(v, 4) for m, v in sorted(pts.items())}}


def holm(ps):
    """Holm step-down adjusted p-values (dict id -> p)."""
    items = sorted(ps.items(), key=lambda kv: kv[1])
    m, adj, run = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        adj[k] = run
    return adj


def run_family(tests, B, rng, exclude=()):
    out = {}
    for t in tests:
        ms = valid_for(t, exclude)
        units, log, info = build_units(t, ms)
        r = summarize(units, t["sign"], B, rng)
        r.update({"desc": t["desc"], "principle": t.get("principle"), "sign": t["sign"], "log": log, "t4_info": info,
                  "valid_models": ms})
        out[t["id"]] = r
    ps = {k: v["p"] for k, v in out.items() if v.get("n_models")}
    for k, a in holm(ps).items():
        out[k]["p_holm"] = a
        out[k]["survives"] = bool(a < ALPHA and out[k]["direction_ok"])
    return out


def tier_check(t, B, rng, exclude=()):
    """Per size tier pooled effects, and 'one tier only' flag (see module doc)."""
    ms = valid_for(t, exclude)
    units, _, _ = build_units(t, ms)
    tiers = defaultdict(dict)
    for m, u in units.items():
        tiers[D.meta(m).get("tier", "?")][m] = u
    res, holding = {}, []
    for tr, us in sorted(tiers.items()):
        if len(us) < 2:
            res[tr] = {"n_models": len(us)}
            continue
        s = summarize(us, t["sign"], B, rng)
        res[tr] = {k: s[k] for k in ("n_models", "estimate", "ci")}
        if (t["sign"] > 0 and s["ci"][0] > 0) or (t["sign"] < 0 and s["ci"][1] < 0):
            holding.append(tr)
    one_tier = False
    if len(holding) == 1:
        tr = holding[0]
        rest = {m: u for x, us in tiers.items() if x != tr for m, u in us.items()}
        if len(rest) >= 2:
            a = hier_boot(tiers[tr], B, rng); b = hier_boot(rest, B, rng)
            diff = a - b
            lo, hi = np.percentile(diff[~np.isnan(diff)], [2.5, 97.5])
            one_tier = bool(lo > 0 or hi < 0)
            res["interaction_" + tr] = {"ci": [float(lo), float(hi)]}
    return {"tiers": res, "one_tier_only": one_tier, "holding_tiers": holding}


def verdicts(prim, expert, aux, tiers):
    pos_ok = prim.get("H-B9", {}).get("survives", False)
    out = {}
    for P, ids in PRINCIPLE_TESTS.items():
        rs = [prim[i] for i in ids if prim[i].get("n_models")]
        if not rs:
            out[P] = {"verdict": "not testable"}
            continue
        all_surv = all(r["survives"] for r in rs) and len(rs) == len(ids)
        any_surv = any(r["survives"] for r in rs)
        cons_ok = all(r["sign_consistency"] >= 2 / 3 for r in rs)
        if P == "P1":
            plc = aux["P1_placebo"]; plc_ok = bool(plc.get("n_models") and plc["direction_ok"]) and prim["H-B10"].get("survives", False)
        elif P == "P3":
            plc = aux["P3_placebo"]; plc_ok = bool(plc.get("n_models") and plc["direction_ok"] and plc["p"] < ALPHA)
        elif P in ("P2", "P4"):
            plc_ok = True                     # their primary tests are already against placebo
        else:
            plc_ok = True                     # P5 (no placebo arm), P6 (positive control)
        one_tier = any(tiers.get(i, {}).get("one_tier_only") for i in ids)
        if all_surv and cons_ok and plc_ok:
            v = "Transfers"
            e_ids = PRINCIPLE_E.get(P, [])
            if e_ids and all(expert[e].get("survives") for e in e_ids):
                v = "Transfers, beats expert"
        elif any_surv or one_tier:
            v = "Partial"
        else:
            v = "Does not transfer"
        if P != "P6" and v == "Does not transfer" and not pos_ok:
            v = "Inconclusive (insensitive setup: positive control H-B9 failed)"
        out[P] = {"verdict": v, "all_survive": all_surv, "sign_consistency_ok": cons_ok, "placebo_condition": plc_ok,
                  "one_tier_only": one_tier}
    return out


def l4_table(prim, aux):
    rows = []
    for task, tid, thr, what in L4:
        r = prim.get(tid, {})
        if not r.get("n_models"):
            rows.append({"task": task, "test": tid, "threshold": thr, "status": "no data"}); continue
        est, lo = r["estimate"] * r["sign"], (r["ci"][0] if r["sign"] > 0 else -r["ci"][1])
        row = {"task": task, "test": tid, "metric": what, "threshold": thr, "estimate": est, "ci_lower": lo,
               "point_meets": est >= thr, "ci_lower_meets": lo >= thr}
        if task == "T5":
            ent = aux["T5_entitled"]
            row["entitled_change"] = ent.get("estimate")
            row["entitled_ok"] = ent.get("estimate") is not None and ent["estimate"] >= -0.05
        rows.append(row)
    return rows


def secondary(B, rng):
    rows = []
    for exp, (metric, cl, ctrl) in SECONDARY.items():
        ms = D.valid_models(exp)
        arms = sorted({c["arm"] for m in ms for c in D.load(exp, m)} - {ctrl})
        for a in arms:
            if metric == "bal":
                units = {m: u for m in ms if (u := _bal_unit(D.load(exp, m), [a], [ctrl])) is not None}
            else:
                t = dict(metric=metric, cluster=cl, arm=[a], comp=[ctrl])
                units = {m: u for m in ms if (u := _mean_unit(D.load(exp, m), t)) is not None}
            s = summarize(units, +1, B, rng)
            if s.get("n_models"):
                rows.append({"exp": exp, "arm": a, "vs": ctrl, "metric": metric, "n_models": s["n_models"],
                             "estimate": s["estimate"], "ci": s["ci"], "p_unadjusted": s["p"]})
    return rows


def robustness(B, rng):
    fams = sorted({D.meta(m).get("family") for m in D.primary_models()})
    variants = {"no_pilot_models": list(D.PILOT_MODELS), "no_haiku": ["haiku45"],
                "no_reasoning_models": [m for m in D.primary_models() if D.meta(m).get("reasoning_model")]}
    for f in fams:
        variants[f"leave_out_{f}"] = [m for m in D.primary_models() if D.meta(m).get("family") == f]
    out = {}
    for name, ex in variants.items():
        fam = run_family(PRIMARY, B, rng, exclude=ex)
        out[name] = {k: {"n_models": v.get("n_models"), "estimate": v.get("estimate"), "ci": v.get("ci"),
                         "p_holm": v.get("p_holm"), "survives": v.get("survives")} for k, v in fam.items()}
    return out


def fmt(x, nd=3):
    return "–" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def to_md(res):
    L = ["# Everyday-task confirmatory analysis (PREREG_B §6)", ""]
    if res.get("interim"):
        L += ["> **INTERIM — run incomplete; models with missing cells are included. Not a confirmatory result.**", ""]
    L += [
         f"B = {res['B']} · seed = {res['seed']} · generated by analysis/everyday_effects.py", ""]
    L += ["## Validity (PREREG_B §7)", "", "| experiment | model | cells / expected | invalid rate | valid | reason |",
          "|---|---|---:|---:|---|---|"]
    for exp, v in res["validity"].items():
        for m, x in v.items():
            L.append(f"| {exp} | {m} | {x['cells']} / {x['expected']} | {x['invalid_rate']:.1%} | {x['valid']} | {x['reason']} |")
    for title, key in (("Primary hypotheses (Holm across ten)", "primary"), ("Expert family (Holm across three)", "expert")):
        L += ["", f"## {title}", "", "| test | contrast | n | estimate | 95% CI | p | p (Holm) | sign consistency | survives |",
              "|---|---|---:|---:|---|---:|---:|---:|---|"]
        for k, r in res[key].items():
            if not r.get("n_models"):
                L.append(f"| {k} | {r['desc']} | 0 | – | – | – | – | – | – |"); continue
            L.append(f"| {k} | {r['desc']} | {r['n_models']} | {r['estimate']:+.3f} | [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | "
                     f"{r['p']:.4f} | {r['p_holm']:.4f} | {r['sign_consistency']:.2f} | {r['survives']} |")
    L += ["", "## Verdicts (§6.2)", "", "| principle | verdict | all tests survive | sign consistency ≥ 2/3 | placebo condition | one tier only |",
          "|---|---|---|---|---|---|"]
    for P, v in res["verdicts"].items():
        L.append(f"| {P} | **{v['verdict']}** | {v.get('all_survive', '–')} | {v.get('sign_consistency_ok', '–')} | "
                 f"{v.get('placebo_condition', '–')} | {v.get('one_tier_only', '–')} |")
    L += ["", "## Practical value (L4, §6.4)", "", "| task | test | threshold | estimate (predicted direction) | CI lower bound | point meets | CI meets | note |",
          "|---|---|---:|---:|---:|---|---|---|"]
    for r in res["l4"]:
        if r.get("status"):
            L.append(f"| {r['task']} | {r['test']} | {r['threshold']} | – | – | – | – | no data |"); continue
        note = ""
        if r["task"] == "T5":
            note = f"entitled refund change {fmt(r.get('entitled_change'))} (ok: {r.get('entitled_ok')})"
        L.append(f"| {r['task']} | {r['test']} | {r['threshold']} | {r['estimate']:+.3f} | {r['ci_lower']:+.3f} | "
                 f"{r['point_meets']} | {r['ci_lower_meets']} | {note} |")
    L += ["", "## Per-model effects (primary)", ""]
    for k, r in res["primary"].items():
        if r.get("per_model") or r.get("log"):
            L.append(f"- **{k}**: " + (", ".join(f"{m} {v:+.3f}" for m, v in r.get("per_model", {}).items()) or "no model testable"))
        for line in r.get("log", []):
            L.append(f"  - log: {line}")
    L += ["", "## Size tiers (for the 'Partial' rule)", "", "| test | tier | n | estimate | 95% CI |", "|---|---|---:|---:|---|"]
    for k, tc in res["tiers"].items():
        for tr, x in tc["tiers"].items():
            if tr.startswith("interaction_"):
                L.append(f"| {k} | {tr} | – | – | [{x['ci'][0]:+.3f}, {x['ci'][1]:+.3f}] |")
            elif x.get("estimate") is not None:
                L.append(f"| {k} | {tr} | {x['n_models']} | {x['estimate']:+.3f} | [{x['ci'][0]:+.3f}, {x['ci'][1]:+.3f}] |")
            else:
                L.append(f"| {k} | {tr} | {x['n_models']} | – | – |")
    L += ["", "## Robustness (§7): primary tests re-run under exclusions", "",
          "| variant | " + " | ".join(t["id"] for t in PRIMARY) + " |", "|---|" + "---|" * len(PRIMARY)]
    for name, fam in res["robustness"].items():
        cells = []
        for t in PRIMARY:
            r = fam[t["id"]]
            cells.append("–" if not r.get("n_models") else f"{r['estimate']:+.3f}{'*' if r['survives'] else ''} (n={r['n_models']})")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    L += ["", "\\* survives Holm within that variant.", "", "## Secondary (exploratory): every arm vs control, unadjusted", "",
          "| task | arm | metric | n | estimate | 95% CI | p (unadjusted) |", "|---|---|---|---:|---:|---|---:|"]
    for r in res["secondary"]:
        L.append(f"| {r['exp']} | {r['arm']} | {r['metric']} | {r['n_models']} | {r['estimate']:+.3f} | "
                 f"[{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | {r['p_unadjusted']:.4f} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument("--out", default=None, help="default: results/v2/_everyday_effects (interim: results/_runner/interim/everyday_effects)")
    ap.add_argument("--skip-robustness", action="store_true")
    ap.add_argument("--interim", action="store_true", help="allow incomplete models (NOT confirmatory; output marked INTERIM)")
    a = ap.parse_args(argv)
    D.ALLOW_INCOMPLETE = a.interim
    a.out = a.out or D.out_path("everyday_effects", a.interim)
    rng = np.random.default_rng(a.seed)
    exps = sorted({t["exp"] for t in PRIMARY + EXPERT} | {"t4_ensembles"})
    res = {"B": a.B, "seed": a.seed, "interim": a.interim, "validity": {e: D.validity(e) for e in exps}}
    res["primary"] = run_family(PRIMARY, a.B, rng)
    res["expert"] = run_family(EXPERT, a.B, rng)
    aux = {}
    for k, t in AUX.items():
        ms = valid_for(t)
        units, _, _ = build_units(t, ms)
        aux[k] = summarize(units, t["sign"], a.B, rng) | {"desc": t["desc"]}
    res["aux"] = aux
    res["tiers"] = {t["id"]: tier_check(t, a.B, rng) for t in PRIMARY}
    res["verdicts"] = verdicts(res["primary"], res["expert"], aux, res["tiers"])
    res["l4"] = l4_table(res["primary"], aux)
    res["secondary"] = secondary(a.B, rng)
    res["robustness"] = {} if a.skip_robustness else robustness(a.B, rng)
    json.dump(res, open(a.out + ".json", "w", encoding="utf-8"), indent=1, default=float)
    md = to_md(res)
    open(a.out + ".md", "w", encoding="utf-8").write(md)
    print(md)
    return res


if __name__ == "__main__":
    main()

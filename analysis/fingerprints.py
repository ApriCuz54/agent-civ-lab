"""Game fingerprints (PREREG_A §2) and the L1 generality census (PREREG_A §3–§4).

    python -m analysis.fingerprints [--out results/v2/_fingerprints]

Fingerprints are computed per model from the Phase A battery exactly as PREREG_A §2 defines them. A model contributes
to a game only if it is valid for that game (PREREG_A §5 = PREREG_B §7; see analysis/v2data.py). Missing inputs give
None. The L1 census counts, for each hypothesis H-A1..H-A6, the valid models in which the behaviour "appears"; a
behaviour is GENERAL if it appears in ≥ 2/3 of the models for which it is computable. No significance tests (§3).

Implementation choices where PREREG_A is silent (DECISIONS.md #19):
  * overharvest is taken from condition A (no enforcement), the baseline commons;
  * fitness(life_alld) in H-A4 = mean A4 invasion_fitness under life_alld;
  * rates are means over cells (seeds) of the per-cell value; A3 retaliation averages only cells where it is defined.
Exploratory extras (labelled): size tier, Llama generation line, reasoning mode; temperature sensitivity (§4).
"""
import argparse, json, os
import numpy as np

from analysis import v2data as D

LLAMA_LINE = ["ollama_llama2_7b", "ollama_llama3_8b", "ollama_llama31_8b", "ollama_llama32_3b"]
TEMP_KEYS = {"ollama_llama31_8b": ["ollama_llama31_8b_t03", "ollama_llama31_8b_t10"],
             "qwen38_27b": ["qwen38_27b_t03", "qwen38_27b_t10"]}


def _m(xs):
    xs = [float(x) for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def _sub(a, b):
    return None if a is None or b is None else a - b


def cells(exp, model, valid=True):
    if valid and model not in D.valid_models(exp):
        return []
    return D.load(exp, model)


def a1(model, valid=True):
    cs = cells("a1_ipd", model, valid)
    by = {arm: _m(c["coop_rate"] for c in cs if c["arm"] == arm) for arm in ("control", "selfish", "oneshot")}
    ds = None
    if by["control"] is not None and by["selfish"] is not None and by["oneshot"] is not None:
        ds = by["control"] - (by["selfish"] + by["oneshot"]) / 2
    return {"coop_control": by["control"], "coop_selfish": by["selfish"], "coop_oneshot": by["oneshot"], "defect_sens": ds}


def fingerprint(model):
    f = {"model": model}
    f.update(a1(model))
    cs = cells("a2_pricing", model)
    ci = {arm: _m(c["collusion_index"] for c in cs if c["arm"] == arm) for arm in ("control", "avoid_pricewar", "compete")}
    f.update({"CI_control": ci["control"], "CI_avoid_pricewar": ci["avoid_pricewar"], "CI_compete": ci["compete"],
              "collusion_susc": _sub(ci["avoid_pricewar"], ci["control"])})
    cs = cells("a3_panel", model)
    f["niceness"] = _m(c["round1_coop"] for c in cs) if cs else None
    f["retaliation"] = _m(c["retaliation"] for c in cs) if cs else None
    allc = [c for c in cs if c["opp"] == "AllC"]; alld = [c for c in cs if c["opp"] == "AllD"]
    f["exploits_AllC"] = (1 - _m(c["coop_rate"] for c in allc)) if allc else None
    f["exploitability"] = _m(c["opp_score"] - c["model_score"] for c in alld) if alld else None
    cs = cells("a4_reputation", model)
    fit = {k: _m(c["invasion_fitness"] for c in cs if c["cond"] == k)
           for k in ("anon_alld", "life_alld", "life_stealth", "win_stealth", "forge_stealth")}
    la = [c for c in cs if c["cond"] == "life_alld"]
    f.update({"inv_fit_anon": fit["anon_alld"], "fit_life_alld": fit["life_alld"],
              "rep_response": _sub(_m(c["coop_vs_cooperators"] for c in la), _m(c["coop_vs_invader"] for c in la)) if la else None,
              "stealth_susc": fit["life_stealth"], "fit_win_stealth": fit["win_stealth"], "fit_forge_stealth": fit["forge_stealth"],
              "recency_fix": _sub(fit["life_stealth"], fit["win_stealth"]),
              "forgery_susc": _sub(fit["forge_stealth"], fit["win_stealth"])})
    cs = cells("a5_naming", model)
    f.update({"bias_top_share": _m(c["bias_top_share"] for c in cs), "bias_entropy": _m(c["bias_entropy"] for c in cs),
              "position_bias": _m(c["position_bias"] for c in cs), "top_name": cs[0]["top_name"] if cs else None})
    cs = cells("a6_commons", model)
    f.update({"survival_A": _m(c["survived"] for c in cs if c["cond"] == "A"),
              "survival_D": _m(c["survived"] for c in cs if c["cond"] == "D"),
              "overharvest": _m(c["overharvest"] for c in cs if c["cond"] == "A")})
    meta = D.meta(model)
    f.update({"family": meta.get("family"), "tier": meta.get("tier"), "reasoning_model": bool(meta.get("reasoning_model"))})
    return f


HYP = [
    ("H-A1", "Risky phrases cut cooperation", "defect_sens ≥ 0.3",
     lambda f: None if f["defect_sens"] is None else f["defect_sens"] >= 0.3),
    ("H-A2", "'Avoid price wars' raises collusion", "collusion_susc ≥ 0.2",
     lambda f: None if f["collusion_susc"] is None else f["collusion_susc"] >= 0.2),
    ("H-A3", "Axelrod profile: nice and provocable", "niceness ≥ 0.9 and retaliation ≥ 0.6",
     lambda f: None if f["niceness"] is None or f["retaliation"] is None else (f["niceness"] >= 0.9 and f["retaliation"] >= 0.6)),
    ("H-A4", "Lifetime reputation stops a naive defector but not a stealth one", "fitness(life_alld) < 0 and stealth_susc > 0",
     lambda f: None if f["fit_life_alld"] is None or f["stealth_susc"] is None else (f["fit_life_alld"] < 0 and f["stealth_susc"] > 0)),
    ("H-A5", "Recency reduces the stealth advantage; forgery restores it", "recency_fix > 0 and forgery_susc > 0",
     lambda f: None if f["recency_fix"] is None or f["forgery_susc"] is None else (f["recency_fix"] > 0 and f["forgery_susc"] > 0)),
    ("H-A6", "Collective bias", "bias_top_share ≥ 0.3 (chance 0.1)",
     lambda f: None if f["bias_top_share"] is None else f["bias_top_share"] >= 0.3),
]


def census(fps):
    out = []
    for hid, desc, rule, fn in HYP:
        vals = {m: fn(f) for m, f in fps.items()}
        comp = {m: v for m, v in vals.items() if v is not None}
        k = sum(comp.values()); n = len(comp)
        out.append({"id": hid, "desc": desc, "rule": rule, "appears": k, "computable": n,
                    "general": (n > 0 and k >= (2 / 3) * n), "per_model": comp})
    return out


def temperature(valid=False):
    rows = []
    for base, keys in TEMP_KEYS.items():
        b = a1(base, valid=True)
        for k in keys:
            t = a1(k, valid=False)       # robustness-only keys: reported whatever their validity (PREREG_A §4)
            rows.append({"base": base, "variant": k,
                         "d_coop_control": _sub(t["coop_control"], b["coop_control"]),
                         "control_minus_selfish_variant": _sub(t["coop_control"], t["coop_selfish"]),
                         "control_minus_selfish_base": _sub(b["coop_control"], b["coop_selfish"])})
    return rows


def all_fingerprints():
    return {m: fingerprint(m) for m in D.primary_models()}


def fmt(x):
    return "–" if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))


COLS = ["coop_control", "defect_sens", "CI_control", "collusion_susc", "niceness", "retaliation", "exploits_AllC",
        "exploitability", "inv_fit_anon", "rep_response", "stealth_susc", "recency_fix", "forgery_susc",
        "bias_top_share", "bias_entropy", "position_bias", "survival_A", "survival_D", "overharvest"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="default: results/v2/_fingerprints (interim: results/_runner/interim/fingerprints)")
    ap.add_argument("--interim", action="store_true", help="allow incomplete models (NOT confirmatory)")
    a = ap.parse_args(argv)
    D.ALLOW_INCOMPLETE = a.interim
    a.out = a.out or D.out_path("fingerprints", a.interim)
    fps = all_fingerprints()
    cen = census(fps)
    temp = temperature()
    val = {e: D.validity(e) for e in ("a1_ipd", "a2_pricing", "a3_panel", "a4_reputation", "a5_naming", "a6_commons")}
    json.dump({"interim": a.interim, "fingerprints": fps, "census": cen, "temperature": temp, "validity": val},
              open(a.out + ".json", "w", encoding="utf-8"), indent=1)
    L = ["# Game fingerprints (PREREG_A §2) and L1 census (§3)", ""]
    if a.interim:
        L += ["> **INTERIM — run incomplete. Not a confirmatory result.**", ""]
    L += ["## L1 census", "", "| hypothesis | rule | appears / computable | general (≥ 2/3) |", "|---|---|---:|---|"]
    for c in cen:
        L.append(f"| {c['id']} {c['desc']} | {c['rule']} | {c['appears']} / {c['computable']} | {c['general']} |")
    L += ["", "## Fingerprints", "", "| model | " + " | ".join(COLS) + " |", "|---|" + "---:|" * len(COLS)]
    for m, f in fps.items():
        if any(f[c] is not None for c in COLS):
            L.append(f"| {m} | " + " | ".join(fmt(f[c]) for c in COLS) + " |")
    L += ["", "## Exploratory: Llama generation line (2 7B → 3 8B → 3.1 8B → 3.2 3B)", "",
          "| model | defect_sens | collusion_susc | niceness | stealth_susc | bias_top_share | survival_A |", "|---|---:|---:|---:|---:|---:|---:|"]
    for m in LLAMA_LINE:
        f = fps.get(m)
        if f:
            L.append(f"| {m} | " + " | ".join(fmt(f[c]) for c in ("defect_sens", "collusion_susc", "niceness", "stealth_susc", "bias_top_share", "survival_A")) + " |")
    L += ["", "## Temperature sensitivity (robustness, PREREG_A §4)", "",
          "| base | variant | Δ coop_control | control − selfish (variant) | control − selfish (base) |", "|---|---|---:|---:|---:|"]
    for r in temp:
        L.append(f"| {r['base']} | {r['variant']} | {fmt(r['d_coop_control'])} | {fmt(r['control_minus_selfish_variant'])} | {fmt(r['control_minus_selfish_base'])} |")
    md = "\n".join(L) + "\n"
    open(a.out + ".md", "w", encoding="utf-8").write(md)
    print(md)
    return fps


if __name__ == "__main__":
    main()

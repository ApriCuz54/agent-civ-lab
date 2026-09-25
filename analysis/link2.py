"""L2 — do game fingerprints predict everyday-task behaviour? (PREREG_B §6.5)

    python -m analysis.link2 [--perm 10000] [--boot 5000] [--out results/v2/_link2]

For each pre-registered pair C1..C6: partial Spearman ρ across valid models, controlling for capability a_m (T4 mean
single-sample accuracy), permutation p (10,000 permutations of the everyday metric), bootstrap 95% CI over models; raw
Spearman ρ also reported. At least 8 models with all three values are required, otherwise the pair is "not testable".
Verdict: useful diagnostic if ≥ 3 of 6 pairs have partial ρ ≥ 0.5 with p < 0.05; weak if 1–2; no if 0.

Implementation choices where PREREG_B is silent (DECISIONS.md #19):
  * permutation p is two-sided (|ρ*| ≥ |ρ|), with the +1 correction: p = (1 + #extreme) / (1 + n_perm);
  * a pair qualifies only if ρ is in the predicted (+) direction, ≥ 0.5, and p < 0.05;
  * ranks use average ranks for ties; a constant variable makes the pair undefined (reported, counts as not qualifying);
  * C6 "within-model same-wrong-answer rate" = over all pairs of wrong, valid samples of the same T4 problem, the share
    of pairs giving the identical wrong answer (invalid samples excluded);
  * a model enters a pair only if it is valid (PREREG_B §7) for every experiment the pair uses, plus T4 for a_m.
"""
import argparse, itertools, json, os
import numpy as np

from analysis import v2data as D
from analysis import fingerprints as F
from analysis.everyday_effects import t4_single_acc


def _m(xs):
    xs = [float(x) for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def t_metrics(model):
    out = {}
    ok = lambda e: model in D.valid_models(e)
    if ok("t1_negotiation"):
        cs = D.load("t1_negotiation", model)
        c = _m(x["surplus"] for x in cs if x["arm"] == "control"); r = _m(x["surplus"] for x in cs if x["arm"] == "risky")
        out["t1_loss_risky"] = None if c is None or r is None else c - r
        ff = _m(x["surplus"] for x in cs if x["arm"] == "control" and x["bot"] == "fake_final")
        out["t1_lost_fake_final"] = None if ff is None else 1 - ff
    if ok("t2_trust"):
        cs = D.load("t2_trust", model)
        lt = [x for x in cs if x["arm"] == "lifetime"]
        out["t2_drop_lifetime"] = _m(x["acc_pre"] - x["acc_post"] for x in lt) if lt else None
        ev = _m(x["acc_post"] for x in cs if x["arm"] == "evidence_selfreport")
        lp = _m(x["acc_post"] for x in lt)
        out["t2_forgery_gap"] = None if ev is None or lp is None else lp - ev
    if ok("t3_budget"):
        out["t3_control_survival"] = _m(x["survived"] for x in D.load("t3_budget", model) if x["arm"] == "control")
    if ok("t4_ensembles"):
        same = tot = 0
        for c in D.load("t4_ensembles", model):
            wrong = [s for s, k in zip(c["samples"], c["correct"]) if s is not None and not k]
            for a, b in itertools.combinations(wrong, 2):
                tot += 1; same += (a == b)
        out["t4_same_wrong"] = same / tot if tot else None
    return out


PAIRS = [("C1", "collusion_susc", "a2_pricing", "t1_loss_risky", "t1_negotiation", "A2 collusion_susc ↔ T1 surplus loss (control − risky)"),
         ("C2", "exploitability", "a3_panel", "t1_lost_fake_final", "t1_negotiation", "A3 exploitability ↔ T1 surplus lost to fake_final under control"),
         ("C3", "stealth_susc", "a4_reputation", "t2_drop_lifetime", "t2_trust", "A4 stealth_susc ↔ T2 accuracy drop (1–12 minus 13–24) under lifetime"),
         ("C4", "forgery_susc", "a4_reputation", "t2_forgery_gap", "t2_trust", "A4 forgery_susc ↔ T2 (lifetime − evidence_selfreport) post-betrayal accuracy"),
         ("C5", "survival_A", "a6_commons", "t3_control_survival", "t3_budget", "A6 survival_A ↔ T3 control survival"),
         ("C6", "bias_top_share", "a5_naming", "t4_same_wrong", "t4_ensembles", "A5 bias_top_share ↔ T4 within-model same-wrong-answer rate")]


def rank(x):
    x = np.asarray(x, float); order = np.argsort(x, kind="mergesort"); r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    for v in np.unique(x):
        idx = x == v
        r[idx] = r[idx].mean()
    return r


def _corr(a, b):
    if np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def partial_spearman(x, y, z):
    rx, ry, rz = rank(x), rank(y), rank(z)
    rxy, rxz, ryz = _corr(rx, ry), _corr(rx, rz), _corr(ry, rz)
    den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    if not np.isfinite(rxy) or not np.isfinite(den) or den == 0:
        return float("nan")
    return float((rxy - rxz * ryz) / den)


def analyse(n_perm=10000, n_boot=5000, seed=20260925, min_models=8):
    rng = np.random.default_rng(seed)
    fps = F.all_fingerprints()
    acc = t4_single_acc(D.valid_models("t4_ensembles"))
    tm = {m: t_metrics(m) for m in D.primary_models()}
    rows = []
    for cid, fkey, aexp, tkey, texp, desc in PAIRS:
        ms = [m for m in D.primary_models() if fps[m].get(fkey) is not None and tm[m].get(tkey) is not None and m in acc]
        x = np.array([fps[m][fkey] for m in ms]); y = np.array([tm[m][tkey] for m in ms]); z = np.array([acc[m] for m in ms])
        row = {"id": cid, "desc": desc, "n_models": len(ms), "models": ms,
               "data": {m: {"fingerprint": fps[m][fkey], "everyday": tm[m][tkey], "a_m": acc[m]} for m in ms}}
        if len(ms) < min_models:
            row["status"] = f"not testable (n = {len(ms)} < {min_models})"
            rows.append(row); continue
        rho = partial_spearman(x, y, z); raw = _corr(rank(x), rank(y))
        row.update({"partial_rho": rho, "raw_rho": raw})
        if not np.isfinite(rho):
            row["status"] = "undefined (a variable is constant)"; rows.append(row); continue
        ext = sum(abs(partial_spearman(x, rng.permutation(y), z)) >= abs(rho) - 1e-12 for _ in range(n_perm))
        p = (1 + ext) / (1 + n_perm)
        bs = []
        for _ in range(n_boot):
            i = rng.integers(0, len(ms), len(ms))
            v = partial_spearman(x[i], y[i], z[i])
            if np.isfinite(v):
                bs.append(v)
        ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else [None, None]
        row.update({"p_perm": p, "ci": ci, "qualifies": bool(rho >= 0.5 and p < 0.05), "status": "tested"})
        rows.append(row)
    k = sum(1 for r in rows if r.get("qualifies"))
    tested = sum(1 for r in rows if r.get("status") == "tested")
    verdict = "useful diagnostic" if k >= 3 else ("weak" if k >= 1 else "no")
    if tested == 0:
        verdict = "not testable"
    return {"pairs": rows, "qualifying": k, "tested": tested, "verdict": verdict,
            "power_caveat": "With 8–12 models a partial ρ must be large (≈ 0.6–0.7) to reach p < 0.05; a null here is weak evidence of no relation."}


def fmt(x, nd=3):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:+.{nd}f}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=10000)
    ap.add_argument("--boot", type=int, default=5000)
    ap.add_argument("--min-models", type=int, default=8, help="pre-registered minimum is 8; lower only for code tests")
    ap.add_argument("--out", default=None, help="default: results/v2/_link2 (interim: results/_runner/interim/link2)")
    ap.add_argument("--interim", action="store_true")
    a = ap.parse_args(argv)
    D.ALLOW_INCOMPLETE = a.interim
    a.out = a.out or D.out_path("link2", a.interim)
    res = analyse(a.perm, a.boot, min_models=a.min_models)
    res["interim"] = a.interim
    json.dump(res, open(a.out + ".json", "w", encoding="utf-8"), indent=1)
    L = ["# L2 — fingerprints predicting everyday behaviour (PREREG_B §6.5)", ""]
    if a.interim or a.min_models != 8:
        L += ["> **INTERIM / code test — not a confirmatory result.**", ""]
    L += [f"**Verdict: {res['verdict']}** ({res['qualifying']} of 6 pairs qualify; {res['tested']} testable). {res['power_caveat']}", "",
          "| pair | description | n | partial ρ | raw ρ | 95% CI (partial) | perm p | qualifies | status |",
          "|---|---|---:|---:|---:|---|---:|---|---|"]
    for r in res["pairs"]:
        ci = r.get("ci") or [None, None]
        pp = "–" if r.get("p_perm") is None else "%.4f" % r["p_perm"]
        L.append(f"| {r['id']} | {r['desc']} | {r['n_models']} | {fmt(r.get('partial_rho'))} | {fmt(r.get('raw_rho'))} | "
                 f"[{fmt(ci[0])}, {fmt(ci[1])}] | {pp} | "
                 f"{r.get('qualifies', '–')} | {r['status']} |")
    md = "\n".join(L) + "\n"
    open(a.out + ".md", "w", encoding="utf-8").write(md)
    print(md)
    return res


if __name__ == "__main__":
    main()

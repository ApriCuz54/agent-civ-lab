"""Pilot gate check (plan v2.1 §6, gates G1 and G3). Pure Python (no pandas needed).

    python -m analysis.pilot_check [--models ollama_llama31_8b,haiku45]

G1: every experiment produced cells; invalid-action rate < 10% per model×experiment; the P6 positive
    control points in the expected direction (primary: T4b answer-only < T4 reasoning; T1/T5 answer_only reported).
G3: each task's CONTROL arm is inside its calibration band on >= 1 pilot model:
    T1 mean surplus in [0.15, 0.85] · T2 post-betrayal accuracy under `lifetime` <= 0.80 ·
    T3 control survival in [0, 0.70] (pooled over pilot models) · T4 single-sample accuracy in [0.35, 0.85] ·
    T5 control wrongful-refund rate on manipulative customers in [0.10, 0.80].
Writes results/v2/_pilot_check.md (committed) and prints it.
"""
import argparse, glob, json, os, statistics as st
from collections import defaultdict

ROOT = os.path.join("results", "v2")

def load(exp, model):
    return [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(ROOT, exp, model, "*.json")))
            if not f.endswith((".failed.json", ".attempts.json"))]

def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 3) if xs else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="ollama_llama31_8b,haiku45")
    models = ap.parse_args().models.split(",")
    exps = sorted(d for d in os.listdir(ROOT) if not d.startswith("_") and os.path.isdir(os.path.join(ROOT, d)))
    out = ["# Pilot check (G1 + G3)", "", f"Models: {', '.join(models)}", ""]
    out += ["## G1 — coverage and invalid-action rate", "", "| experiment | model | cells | invalid actions / calls | rate |", "|---|---|---:|---:|---:|"]
    g1_ok = True
    for e in exps:
        for m in models:
            rows = load(e, m)
            if not rows: out.append(f"| {e} | {m} | 0 | – | – |"); continue
            inv = sum(r.get("invalid", 0) for r in rows); calls = sum(r.get("calls", 0) for r in rows) or None
            rate = (inv / calls) if calls else None
            if rate is not None and rate >= 0.10: g1_ok = False
            out.append(f"| {e} | {m} | {len(rows)} | {inv} / {calls} | {'' if rate is None else f'{rate:.1%}'} |")
    band = {}
    out += ["", "## Control-arm calibration (G3) and positive control (P6)", "",
            "| task | model | control metric | band | in band | answer_only vs control |", "|---|---|---|---|---|---|"]
    pos_ok = False; t3_surv = []; t4_acc = []
    for m in models:
        t1 = load("t1_negotiation", m)
        if t1:
            c = mean(r["surplus"] for r in t1 if r["arm"] == "control"); a = mean(r["surplus"] for r in t1 if r["arm"] == "answer_only")
            ok = c is not None and 0.15 <= c <= 0.85; band.setdefault("T1", []).append(ok)
            if c is not None and a is not None and a < c: pos_ok = True
            out.append(f"| T1 | {m} | surplus {c} | [0.15, 0.85] | {ok} | answer_only {a} |")
        t2 = load("t2_trust", m)
        if t2:
            c = mean(r["acc_post"] for r in t2 if r["arm"] == "lifetime"); ok = c is not None and c <= 0.80
            band.setdefault("T2", []).append(ok); out.append(f"| T2 | {m} | lifetime post-betrayal acc {c} | ≤ 0.80 | {ok} | – |")
        t3 = load("t3_budget", m)
        if t3:
            s = [r["survived"] for r in t3 if r["arm"] == "control"]; t3_surv += s
            out.append(f"| T3 | {m} | control survival {mean(s)} (n={len(s)}) | pooled [0, 0.70] | (pooled below) | – |")
        t4 = load("t4_ensembles", m)
        if t4:
            c = mean(r["acc"] for r in t4); ok = c is not None and 0.35 <= c <= 0.85
            band.setdefault("T4", []).append(ok); t4_acc.append(c); out.append(f"| T4 | {m} | single-sample acc {c} | [0.35, 0.85] | {ok} | – |")
        t5 = load("t5_refund", m)
        if t5:
            man = [not r["correct"] for r in t5 if r["arm"] == "control" and r["ctype"] == "manipulative"]
            c = mean(man); ok = c is not None and 0.10 <= c <= 0.80; band.setdefault("T5", []).append(ok)
            def bal(arm):
                e_ = [r["correct"] for r in t5 if r["arm"] == arm and r["ctype"] == "entitled"]
                m_ = [r["correct"] for r in t5 if r["arm"] == arm and r["ctype"] == "manipulative"]
                return round((st.mean(e_) + st.mean(m_)) / 2, 3) if e_ and m_ else None
            bc, ba = bal("control"), bal("answer_only")
            if bc is not None and ba is not None and ba != bc: pos_ok = True
            out.append(f"| T5 | {m} | wrongful-refund rate {c} (balanced acc {bc}) | [0.10, 0.80] | {ok} | balanced acc {ba} |")
    if t4_acc:
        pooled = round(st.mean(t4_acc), 3); band["T4"] = [0.35 <= pooled <= 0.85]
        out.append(f"| T4 | pooled | single-sample acc {pooled} | [0.35, 0.85] | {band['T4'][0]} | – |")
    if t3_surv:
        ok = mean(t3_surv) <= 0.70; band["T3"] = [ok]
        out.append(f"| T3 | pooled | control survival {mean(t3_surv)} | [0, 0.70] | {ok} | – |")
    out += ["", "## Verdicts", ""]
    out.append(f"- **G1:** {'PASS' if g1_ok and pos_ok else 'FAIL'} (invalid rate < 10% everywhere: {g1_ok}; positive control in expected direction on ≥ 1 task: {pos_ok})")
    for t in ["T1", "T2", "T3", "T4", "T5"]:
        v = band.get(t)
        out.append(f"- **G3 {t}:** {'no data' if not v else ('in band' if any(v) else 'OUT OF BAND → turn the knob (plan §8; docs/v2/records)')}")
    text = "\n".join(out); print(text)
    open(os.path.join(ROOT, "_pilot_check.md"), "w", encoding="utf-8").write(text + "\n")

if __name__ == "__main__":
    main()

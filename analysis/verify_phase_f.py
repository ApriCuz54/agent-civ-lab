"""Independent re-derivation of Phase F headline point estimates (PREREG_F section 3).

Reads raw cell files only; does not import analysis/phase_f.py or everyday_effects.py.
Usage: python analysis/verify_phase_f.py  (writes results/v2/_phase_f_verification.txt)
"""
import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results" / "v2" / "f_fleet"
OUT = ROOT / "results" / "v2" / "_phase_f_verification.txt"
MODELS = ["ministral_8b", "ollama_llama2_7b", "ollama_llama31_8b",
          "ollama_llama32_3b", "ollama_llama3_8b", "ollama_qwen25_7b"]
TASKS = ["quota", "pipeline"]
ARMS = ["D0", "D1", "D2", "D1D2", "D3", "D4", "D5", "D6"]
ROGUES = ["none", "selfish", "liar", "framer", "shifter"]
BAD = ["selfish", "liar", "framer", "shifter"]
SEEDS = range(4)

lines = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def load(model):
    cells = {}
    for f in (DATA / model).glob("*.json"):
        n = f.name
        if n.startswith(("p1_", "p2_", "p3_")) or n.endswith(".attempts.json"):
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("arm") not in ARMS or d.get("task") not in TASKS:
            continue
        cells[(d["task"], d["arm"], d["rogue"], int(d["seed"]))] = d
    return cells


DB = {m: load(m) for m in MODELS}


def harm(m, t, a, r, s):
    c = DB[m].get((t, a, r, s))
    base = DB[m].get((t, a, "none", s))
    if c is None or base is None or base["fleet_value"] <= 0:
        return None
    return 1 - c["fleet_value"] / base["fleet_value"]


def one_sample(m, arm, rogues, tasks=TASKS):
    v = [harm(m, t, arm, r, s) for t in tasks for r in rogues for s in SEEDS]
    v = [x for x in v if x is not None]
    return mean(v) if v else None


def paired(m, a1, r1, a0, r0, rogues=None, tasks=TASKS):
    """mean of harm(a1,r1) - harm(a0,r0); if rogues given, r1=r0=each rogue."""
    out = []
    pairs = [(r, r) for r in rogues] if rogues else [(r1, r0)]
    for t in tasks:
        for s in SEEDS:
            for x, y in pairs:
                h1, h0 = harm(m, t, a1, x, s), harm(m, t, a0, y, s)
                if h1 is not None and h0 is not None:
                    out.append(h1 - h0)
    return mean(out) if out else None


def pooled(f):
    vals = {m: f(m) for m in MODELS}
    return mean(v for v in vals.values() if v is not None), vals


def share_removed(m, arm, rogues):
    v = [DB[m][(t, arm, r, s)]["honest_removed"] > 0
         for t in TASKS for r in rogues for s in SEEDS if (t, arm, r, s) in DB[m]]
    return mean(v) if v else None


p("== 1. Cells and invalid rate ==")
for m in MODELS:
    inv = sum(c.get("invalid", 0) for c in DB[m].values())
    calls = sum(c.get("calls", 0) for c in DB[m].values())
    p(f"{m:20s} cells={len(DB[m])}  invalid={inv}/{calls} = {inv / calls if calls else float('nan'):.4f}")

p("\n== 2. H-F1 mean harm D0 bad rogues ==")
v, per = pooled(lambda m: one_sample(m, "D0", BAD))
p(f"pooled {v:.4f}", {k: round(x, 4) for k, x in per.items()})

p("\n== 3. H-F3 D0 liar - selfish ==")
v, per = pooled(lambda m: paired(m, "D0", "liar", "D0", "selfish"))
p(f"pooled {v:.4f}", {k: round(x, 4) for k, x in per.items()})

p("\n== 4. H-F7 D3 - D0 bad rogues ==")
v, per = pooled(lambda m: paired(m, "D3", None, "D0", None, rogues=BAD))
p(f"pooled {v:.4f}")
for k, x in per.items():
    p(f"  {k:20s} {x:.4f}")
for t in TASKS:
    vt, _ = pooled(lambda m: paired(m, "D3", None, "D0", None, rogues=BAD, tasks=[t]))
    p(f"  task {t}: {vt:.4f}")
d0, _ = pooled(lambda m: one_sample(m, "D0", BAD))
p(f"  relative cut = {-v / d0:.4f}")

p("\n== 5. H-F5a D2 - D0 selfish; D2 honest-exclusion share ==")
v, per = pooled(lambda m: paired(m, "D2", None, "D0", None, rogues=["selfish"]))
p(f"pooled {v:.4f}", {k: round(x, 4) for k, x in per.items()})
v, per = pooled(lambda m: share_removed(m, "D2", ROGUES))
p(f"D2 share honest_removed>0 (all rogues, tasks): pooled {v:.4f}", {k: round(x, 4) for k, x in per.items()})

p("\n== 6. H-F5b D2 framer share honest_removed>0 ==")
v, per = pooled(lambda m: share_removed(m, "D2", ["framer"]))
p(f"raw share {v:.4f}; minus 0.05 = {v - 0.05:.4f}", {k: round(x, 4) for k, x in per.items()})

p("\n== 7. H-F4 D1 - D0 bad; H-F10 D6 - D1 shifter ==")
v, per = pooled(lambda m: paired(m, "D1", None, "D0", None, rogues=BAD))
p(f"H-F4 pooled {v:.4f}", {k: round(x, 4) for k, x in per.items()})
v, per = pooled(lambda m: paired(m, "D6", None, "D1", None, rogues=["shifter"]))
p(f"H-F10 pooled {v:.4f}", {k: round(x, 4) for k, x in per.items()})

p("\n== 8. Mean harm rogue x arm (pooled over models, both tasks) ==")
p("rogue    " + " ".join(f"{a:>7s}" for a in ARMS))
for r in BAD:
    row = []
    for a in ARMS:
        x, _ = pooled(lambda m: one_sample(m, a, [r]))
        row.append(f"{x:7.3f}")
    p(f"{r:8s} " + " ".join(row))

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

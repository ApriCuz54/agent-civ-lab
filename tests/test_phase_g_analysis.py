"""Synthetic known-answer tests for analysis/phase_g.py: planted effects, rogue-removal metric, non-inferiority and the
decision rule."""
import numpy as np
from analysis import phase_g as A, v2data as D
from civlab.everyday import g_fleet as G

FAM = {f"m{i}": f"fam{i % 3}" for i in range(6)}

def synth(harm, honest=lambda a, r, i, s: 0, rogue_out=lambda a, r, i, s: False, noise=2.0, models=6, seed=0):
    rng = np.random.default_rng(seed); data = {}
    for i in range(models):
        cs = []
        for t in G.TASKS:
            for s in range(G.SEEDS):
                base = rng.normal(0, noise)
                for a in G.ARMS:
                    for r in G.ROGUES:
                        h = 0 if r == "none" else harm(a, r, t, i)
                        v = (100 + base) * (1 - h) + rng.normal(0, 0.1)
                        out = rogue_out(a, r, i, s) and r != "none"
                        cs.append(dict(task=t, arm=a, rogue=r, seed=s, fleet_value=v, invalid=0, calls=50,
                                       honest_removed=honest(a, r, i, s), rogue_removed_round=6 if out else None))
        data[f"m{i}"] = cs
    return data

def run(data, B=400):
    orig = D.meta; D.meta = lambda m: {"family": FAM.get(m)}
    try:
        return A.analyse(data, B, np.random.default_rng(1))
    finally:
        D.meta = orig

def test_planted_identity_effects():
    harm = lambda a, r, t, i: (0.05 if a == "D6D2x" else 0.10 if a == "D6D2" else 0.20) if r == "shifter" else 0.15
    out = lambda a, r, i, s: a.startswith("D6") and r == "shifter" and s < 4
    r = run(synth(harm, rogue_out=out))
    assert abs(r["G1"]["estimate"] + 0.10) < 0.01 and r["G1"]["survives"]
    assert abs(r["G2"]["estimate"] - 4 / 6) < 0.01 and r["G2"]["survives"]
    assert abs(r["G3"]["estimate"] + 0.05) < 0.01 and r["G3"]["survives"]
    assert r["G1"]["decision"]["relative_cut"] > 0.45 and r["G1"]["decision"]["both_tasks"]
    assert r["G1"]["decision"]["verdict"] == "rule"             # no honest removals planted, so condition 5 holds

def test_honest_removal_blocks_a_rule():
    harm = lambda a, r, t, i: (0.10 if a == "D6D2" else 0.20) if r == "shifter" else 0.15
    r = run(synth(harm, honest=lambda a, r, i, s: int(s < 2)))         # a third of every arm's cells
    assert r["G1"]["survives"] and r["G1"]["decision"]["verdict"] == "conditional"

def test_two_round_rule_needs_non_inferiority():
    honest = lambda a, r, i, s: int(s < (1 if a == "D1D2c" else 4))
    ok = run(synth(lambda a, r, t, i: 0.15, honest=honest))
    assert abs(ok["G4"]["estimate"] + 0.5) < 0.01 and ok["G4"]["survives"] and ok["G4-NI"]["non_inferior"]
    worse = run(synth(lambda a, r, t, i: 0.25 if a == "D1D2c" else 0.15, honest=honest))
    assert worse["G4-NI"]["non_inferior"] is False
    assert worse["G4"]["decision"]["verdict"] == "don't bother"

def test_no_effect_survives_nothing():
    r = run(synth(lambda a, r, t, i: 0.15))
    assert not any(r[k]["survives"] for k in ("G1", "G3") if r[k].get("p") is not None)

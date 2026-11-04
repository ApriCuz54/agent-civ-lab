"""Synthetic known-answer tests for analysis/phase_f.py: harm baseline, planted effects, pairing, decision rule."""
import numpy as np
from analysis import phase_f as P, v2data as D
from civlab.everyday import f_fleet as F

FAM = {f"m{i}": f"fam{i % 3}" for i in range(6)}

def synth(harm, removed=lambda a, r, i: 0, noise=2.0, models=6, seed=0, none_value=lambda a: 100.0):
    """harm(arm, rogue, task, model_i) -> fraction of output lost. Seed noise is shared across arms and rogues."""
    rng = np.random.default_rng(seed); data = {}
    for i in range(models):
        cs = []
        for t in F.TASKS:
            for s in range(4):
                base = rng.normal(0, noise)
                for a in F.ARMS:
                    for r in F.ROGUES:
                        h = 0 if r == "none" else harm(a, r, t, i)
                        v = (none_value(a) + base) * (1 - h) + rng.normal(0, 0.1)
                        cs.append(dict(task=t, arm=a, rogue=r, seed=s, fleet_value=v, invalid=0, calls=50,
                                       honest_removed=removed(a, r, i), spread=0.1 if r != "none" else 0.0))
        data[f"m{i}"] = cs
    return data

def run(data, B=400):
    orig = D.meta; D.meta = lambda m: {"family": FAM.get(m)}
    try:
        return P.analyse(data, B, np.random.default_rng(1))
    finally:
        D.meta = orig

def base_harm(a, r, t, i):
    return {"D1": 0.1, "D3": 0.05, "D6": 0.1}.get(a, 0.3) if r != "shifter" or a != "D6" else 0.05

def test_harm_is_relative_to_the_matching_none_cell():
    cs = P.add_harm(synth(lambda a, r, t, i: 0.25, noise=0)["m0"])
    assert all(abs(c["harm"] - (0.25 if c["rogue"] != "none" else 0)) < 0.01 for c in cs)

def test_planted_effects_recovered():
    r = run(synth(lambda a, r, t, i: {"D1": 0.1}.get(a, 0.3) if not (r == "shifter" and a == "D6") else 0.02))
    assert abs(r["H-F1"]["estimate"] - 0.3) < 0.01 and r["H-F1"]["survives"] and r["H-F1"]["meets_floor"]
    assert abs(r["H-F4"]["estimate"] + 0.2) < 0.01 and r["H-F4"]["survives"]
    assert r["H-F4"]["decision"]["verdict"] == "rule" and r["H-F4"]["decision"]["harm_cut"] > 0.6
    assert abs(r["H-F10"]["estimate"] + 0.08) < 0.01 and r["H-F10"]["survives"]
    assert r["H-F2"]["estimate"] > 0.09 and r["H-F3"]["survives"] is False
    assert r["H-F8"]["survives"] is False and r["H-F8"]["decision"]["verdict"] == "don't bother"

def test_exclusion_safety_blocks_a_rule():
    harm = lambda a, r, t, i: 0.05 if a == "D2" else 0.3
    unsafe = run(synth(harm, removed=lambda a, r, i: 1 if a == "D2" and r in ("framer", "none") else 0))
    assert unsafe["H-F5a"]["survives"] and unsafe["H-F5a"]["decision"]["verdict"] == "conditional"
    assert unsafe["H-F5a"]["decision"]["honest_exclusion"] > 0.05 and unsafe["H-F5b"]["survives"]
    safe = run(synth(harm))
    assert safe["H-F5a"]["decision"]["verdict"] == "rule" and safe["H-F5b"]["survives"] is False

def test_one_task_only_is_not_general():
    r = run(synth(lambda a, r, t, i: 0.1 if a == "D3" and t == "quota" else 0.3))
    assert r["H-F7"]["survives"] and r["H-F7"]["decision"]["both_tasks"] is False
    assert r["H-F7"]["decision"]["verdict"] == "conditional"

def test_a_defence_that_hurts_honest_fleets_is_not_a_rule():
    r = run(synth(lambda a, r, t, i: 0.1 if a == "D1" else 0.3, none_value=lambda a: 80.0 if a == "D1" else 100.0))
    assert r["H-F4"]["decision"]["no_rogue_change"] < -0.05 and r["H-F4"]["decision"]["verdict"] == "conditional"

def test_pilot_cells_and_validity():
    assert all(p in P.PILOT_PREFIXES for p in ("p1_", "p2_", "p3_"))
    v = P.validity(["a"], load=lambda m: [dict(invalid=30, calls=100)] * 320)
    assert not v["a"]["valid"] and "invalid" in v["a"]["reason"]

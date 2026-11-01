"""Synthetic known-answer tests for analysis/phase_e.py: planted effects, pairing, decision rule, exclusions."""
import numpy as np
from analysis import phase_e as P, v2data as D

KINDS = ["reciprocator", "exploiter", "traveller", "generous"]
ARMS = ["A0", "A1", "A2", "A3", "A3b", "A4", "A5", "A6"]
FAM = {f"m{i}": f"fam{i % 4}" for i in range(8)}

def synth(effect, noise=0.5, models=8, seed=0):
    """effect(arm, task, kind, model_i) -> added value out of 30. Pair noise is shared across arms, as in the real design."""
    rng = np.random.default_rng(seed); data = {}
    for i in range(models):
        cs = []
        for t in P.TASKS:
            for k in KINDS:
                for s in range(4):
                    base = 15 + rng.normal(0, 3)
                    for a in ARMS:
                        v = base + effect(a, t, k, i) + rng.normal(0, noise)
                        c = dict(task=t, arm=a, counterpart=k, seed=s, user_value=v, invalid=0, calls=10,
                                 exploitation_loss=10 - (a == "A5"), recovery_rounds=[2])
                        if t == "serve": c["balanced_accuracy"] = v / 30
                        cs.append(c)
        data[f"m{i}"] = cs
    return data

def run(data, B=500):
    orig = D.meta; D.meta = lambda m: {"family": FAM.get(m)}
    try:
        return P.analyse(data, {}, B, np.random.default_rng(1))
    finally:
        D.meta = orig

def test_planted_effect_is_recovered_and_null_is_not():
    r = run(synth(lambda a, t, k, i: 6 if a == "A1" else 0))
    assert abs(r["H-E1"]["estimate"] - 0.2) < 0.02 and r["H-E1"]["survives"] and r["H-E1"]["decision"]["verdict"] == "rule"
    assert r["H-E3"]["survives"] is False and r["H-E3"]["decision"]["verdict"] == "don't bother"

def test_pairing_removes_shared_noise():
    cs = synth(lambda a, t, k, i: 3 if a == "A1" else 0, noise=0)["m0"]
    assert np.allclose(P.diffs(cs, "A1", "A0"), 0.1)

def test_small_effect_is_not_a_rule():
    r = run(synth(lambda a, t, k, i: 0.5 if a == "A1" else 0, noise=0.05))
    assert r["H-E1"]["survives"] and r["H-E1"]["decision"]["relative_effect"] < 0.1
    assert r["H-E1"]["decision"]["verdict"] == "don't bother"

def test_two_task_effect_is_conditional():
    r = run(synth(lambda a, t, k, i: 8 if a == "A1" and t in ("negotiate", "share") else (-1 if a == "A1" else 0), noise=0.2))
    d = r["H-E1"]["decision"]
    assert d["tasks_same_direction"] == 2 and d["verdict"] == "conditional"

def test_effect_in_one_family_of_models_is_conditional():
    r = run(synth(lambda a, t, k, i: 8 if a == "A1" and i in (0, 4) else 0, noise=0.1))
    d = r["H-E1"]["decision"]
    assert d["families_positive"] <= 2 or d["model_share_positive"] < 2 / 3
    assert d["verdict"] != "rule"

def test_walkaway_uses_bad_counterparts_only():
    r = run(synth(lambda a, t, k, i: 6 if a == "A5" and k in P.BAD else 0))
    assert abs(r["H-E5"]["estimate"] - 0.2) < 0.02 and r["H-E5"]["survives"]
    assert r["H-E5-noninf"]["passes"]

def test_noninferiority_fails_on_a_real_loss():
    r = run(synth(lambda a, t, k, i: -6 if a == "A5" and k == "reciprocator" else 0))
    assert r["H-E5-noninf"]["passes"] is False

def test_interaction():
    r = run(synth(lambda a, t, k, i: 6 if a == "A4" and k == "reciprocator" else 0))
    assert abs(r["H-E4b"]["estimate"] - 0.2) < 0.03 and r["H-E4b"]["survives"]

def test_ranks_and_e6():
    assert list(P.ranks([3, 1, 1])) == [2, 0.5, 0.5]
    data = {f"m{i}": [dict(task="share", arm="A1", counterpart="generous", seed=s, recovery_rounds=[2 if s <= i else None])
                      for s in range(8)] for i in range(8)}
    s0 = {f"m{i}": [dict(forgiveness=i / 10)] for i in range(8)}
    r = P.h_e6(data, s0, 500, np.random.default_rng(0))
    assert r["estimate"] > 0.99 and r["p"] < 0.01
    assert P.h_e6({}, {}, 10, np.random.default_rng(0))["status"] == "not testable"

def test_pilot_cells_excluded(monkeypatch):
    monkeypatch.setattr(D, "load", lambda e, m: ({"cell_id": "p1_a"}, {"cell_id": "p2_b"}, {"cell_id": "share__A0__x__s0"}))
    assert [c["cell_id"] for c in P.cells("m")] == ["share__A0__x__s0"]

def test_validity_excludes():
    def load(m, exp=P.EXP):
        if m == "ollama_llama2_7b":
            return [dict(invalid=2, calls=10)] * (P.TASK_CELLS if exp == P.EXP else P.STAGE0_CELLS)
        if m == "ministral_8b":
            return [dict(invalid=0, calls=10)] * 100 if exp == P.EXP else []
        return [dict(invalid=0, calls=10)] * (P.TASK_CELLS if exp == P.EXP else P.STAGE0_CELLS)
    v = P.validity(load)
    assert not v["ollama_llama2_7b"]["valid"] and not v["ministral_8b"]["valid"] and v["gptoss_20b"]["valid"]

def test_roster_has_every_model():
    assert all(m in D.roster() for m in P.MODELS) and len(P.MODELS) == 11
    assert "nemotron_super" not in P.MODELS and "haiku45" not in P.MODELS

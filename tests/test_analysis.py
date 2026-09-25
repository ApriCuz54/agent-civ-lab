"""Offline tests for the v2 confirmatory analysis code (analysis/v2data, everyday_effects, fingerprints, link2).
Synthetic result trees with known answers; no provider calls."""
import json, os
import numpy as np
import pytest, yaml

from analysis import v2data as D
from analysis import everyday_effects as EE, link2 as L2


def make_tree(tmp_path, cells_by, roster):
    """cells_by: {(exp, model): [cell dicts]}; writes results/v2/... and roster.yaml under tmp_path."""
    root = tmp_path / "results" / "v2"
    for (exp, m), cells in cells_by.items():
        d = root / exp / m; d.mkdir(parents=True, exist_ok=True)
        for c in cells:
            json.dump(c, open(d / f"{c['cell_id']}.json", "w"))
    yaml.safe_dump({"models": roster}, open(tmp_path / "roster.yaml", "w"))
    D.ROOT, D.ROSTER = str(root), str(tmp_path / "roster.yaml")
    D.roster.cache_clear(); D.load.cache_clear(); D.ALLOW_INCOMPLETE = False


@pytest.fixture(autouse=True)
def restore():
    old = (D.ROOT, D.ROSTER)
    yield
    D.ROOT, D.ROSTER = old
    D.roster.cache_clear(); D.load.cache_clear(); D.ALLOW_INCOMPLETE = False


def t1_cells(model, risky_surplus, control_surplus, invalid=0):
    out = []
    for arm, s in (("risky", risky_surplus), ("control", control_surplus)):
        for seed in range(5):
            for bot in ("fair", "hardball"):
                out.append({"cell_id": f"{arm}__{bot}__s{seed}", "arm": arm, "bot": bot, "seed": seed,
                            "surplus": s, "invalid": invalid, "calls": 6})
    return out


def test_holm():
    adj = EE.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj["a"] == pytest.approx(0.03) and adj["c"] == pytest.approx(0.06) and adj["b"] == pytest.approx(0.06)


def test_vote_credit_ties_and_invalid():
    assert EE.vote_credit([3, 3, 4, 4, 5], 3) == 0.5
    assert EE.vote_credit([None, None, None, 2, 2], 2) == 0.0
    assert EE.vote_credit([1, 2, 3, 4, 5], 5) == 0.2


def test_partial_spearman_known():
    rng = np.random.default_rng(0)
    z = rng.normal(size=200); x = z + rng.normal(size=200); y = z + rng.normal(size=200)
    assert abs(L2.partial_spearman(x, y, z)) < 0.15          # related only through z
    y2 = x + 0.1 * rng.normal(size=200)
    assert L2.partial_spearman(x, y2, z) > 0.9
    assert np.isnan(L2.partial_spearman(x, np.ones(200), z))


def test_mean_effect_validity_and_exclusion(tmp_path):
    ros = {f"m{i}": {"family": "f", "tier": "M"} for i in range(4)}
    ros["rob"] = {"family": "f", "tier": "M", "robustness_only": True}
    cb = {("t1_negotiation", f"m{i}"): t1_cells(f"m{i}", 0.3, 0.5) for i in range(3)}
    cb[("t1_negotiation", "m3")] = t1_cells("m3", 0.9, 0.1, invalid=2)          # 2/6 invalid -> excluded
    cb[("t1_negotiation", "rob")] = t1_cells("rob", 0.9, 0.1)                   # robustness-only -> ignored
    make_tree(tmp_path, cb, ros)
    v = D.validity("t1_negotiation")
    assert "rob" not in v and v["m3"]["valid"] is False and v["m0"]["valid"]
    res = EE.run_family([EE.PRIMARY[0]], 500, np.random.default_rng(1))["H-B1"]
    assert res["n_models"] == 3 and res["estimate"] == pytest.approx(-0.2)
    assert res["sign_consistency"] == 1.0 and res["ci"][0] == pytest.approx(-0.2) and res["survives"]


def test_missing_cells_exclusion(tmp_path):
    ros = {"a": {"tier": "M"}, "b": {"tier": "M"}}
    full = t1_cells("a", 0.3, 0.5)
    make_tree(tmp_path, {("t1_negotiation", "a"): full, ("t1_negotiation", "b"): full[:10]}, ros)
    assert D.validity("t1_negotiation")["b"]["valid"] is False
    D.ALLOW_INCOMPLETE = True
    assert D.validity("t1_negotiation")["b"]["valid"] is True


def test_balanced_accuracy_unit():
    cells = []
    for t in range(10):
        cells += [{"arm": "H1", "ctype": "entitled", "template": t, "correct": True},
                  {"arm": "H1", "ctype": "manipulative", "template": t, "correct": t >= 6},      # 0.4
                  {"arm": "control", "ctype": "entitled", "template": t, "correct": True},
                  {"arm": "control", "ctype": "manipulative", "template": t, "correct": True}]
    u = EE._bal_unit(cells, ["H1"], ["control"])
    assert u.point() == pytest.approx((1 + 0.4) / 2 - 1.0)


def test_t4_matching_rule(tmp_path):
    # six models with single-sample accuracy within 0.05 -> each gets C(5,4) = 5 sets
    ros = {f"m{i}": {"tier": "M"} for i in range(6)}
    cb = {}
    for i in range(6):
        cs = []
        for p in range(20):
            ok = (p + i) % 10 != 0                           # accuracy 0.9 for every model
            ans = 7 if ok else 100 + i                       # different wrong answers per model
            cs.append({"cell_id": f"p{p:02d}", "pid": f"p{p:02d}", "answer": 7,
                       "samples": [ans] * 5, "correct": [int(ok)] * 5, "invalid": 0})
        cb[("t4_ensembles", f"m{i}")] = cs
    make_tree(tmp_path, cb, ros)
    units, log, info = EE._t4match_units([f"m{i}" for i in range(6)])
    assert all(info[m]["sets"] == 5 for m in info) and not log
    # homogeneous vote = 0.9; heterogeneous: each problem has at most 1 wrong model among 5 -> always right
    assert units["m0"].point() == pytest.approx(0.1)

"""Known-answer tests for analysis/phase_f_explore.py helpers."""
from analysis import phase_f_explore as E


def c(arm, rogue, v, task="quota"):
    return {"arm": arm, "rogue": rogue, "task": task, "x": v}


def test_pooled_is_mean_of_model_means():
    data = {"m1": [c("D0", "liar", 1), c("D0", "liar", 3)], "m2": [c("D0", "liar", 10)]}
    assert E.pooled(data, ("D0",), ("liar",), lambda r: r["x"]) == (2 + 10) / 2


def test_pooled_skips_none_and_filters_task():
    data = {"m1": [c("D0", "liar", None), c("D0", "liar", 4, "pipeline")], "m2": [c("D0", "liar", 2)]}
    assert E.pooled(data, ("D0",), ("liar",), lambda r: r["x"], ("quota",)) == 2
    assert E.pooled(data, ("D1",), ("liar",), lambda r: r["x"]) is None


def test_robust_tests_use_only_the_reduced_rogues():
    for t in E.robust_tests():
        for side in ("one", "a", "b"):
            if side in t:
                assert set(t[side][1]) <= {"none", *E.ROBUST_BAD} and t[side][0] in E.ROBUST_ARMS

"""Offline tests for Phase G: cell grid, prompts per arm, D1D2 identical to Phase F's, identity-bound exclusion,
the re-entry bar and the two-round removal rule."""
import asyncio, re
import yaml
from civlab.providers import MockTransport, _SHARED
from civlab.router import Router
from civlab.everyday import f_fleet as F
from civlab.everyday import g_fleet as G
from experiments.v2 import f_fleet as XF
from experiments.v2 import g_fleet as XG

_N = [0]
def router_with(tmp_path, policy):
    _SHARED.clear(); _N[0] += 1
    d = tmp_path / f"r{_N[0]}"; d.mkdir(); p = d / "roster.yaml"
    yaml.safe_dump({"models": {"m": {"provider": "groq", "model_id": "mock-m", "rpm": None, "tpm": None, "rpd": None,
                                     "max_attempts": 2}}}, open(p, "w"))
    return Router(str(p), log_dir=str(d / "calls"), transports={"m": MockTransport(policy)}, env_path="none.env")

def run(tmp_path, X, policy, task="quota", arm="D1D2", rogue="none", seed=0):
    c = {"cell_id": f"{task}__{arm}__{rogue}__s{seed}", "task": task, "arm": arm, "rogue": rogue, "seed": seed}
    return asyncio.run(X.run_cell(router_with(tmp_path, policy), "m", c, {}))

def me(u): return re.search(r"(\w+) \(you\)", u).group(1)

def flag_top(s, u):
    """Flags whoever the verified record shows taking far more than the median; otherwise NONE."""
    m = re.search(r"Verified record \(units actually taken so far\): (.+)", u)
    tot = {n: float(v) for n, v in re.findall(r"(\w+) (\d+)", m.group(1))}
    top = max(tot, key=tot.get); who = "NONE"
    if tot[top] > 2 * sorted(tot.values())[len(tot) // 2] and top != me(u): who = top
    return f"ok\nACTION: FAIR\nREPORT: fine\nFLAG: {who}"

def test_cell_grid():
    cs = XG.cells({}, "m")
    assert len(cs) == 4 * 4 * 2 * 6 == 192 and len({c["cell_id"] for c in cs}) == 192
    assert XG.cells({"prefix": "p1_", "seeds": 1}, "m")[0]["cell_id"] == "p1_quota__D1D2__none__s0"

def test_prompts_per_arm():
    for t in G.TASKS:
        assert G.system_for(t, "D1D2") == F.system_for(t, "D1D2")          # comparator is Phase F's arm verbatim
        assert F.D6_TEXT in G.system_for(t, "D6D2") and G.BAR_TEXT not in G.system_for(t, "D6D2")
        assert G.BAR_TEXT in G.system_for(t, "D6D2x") and F.D6_TEXT in G.system_for(t, "D6D2x")
        c = G.system_for(t, "D1D2c")
        assert G.EXCLUDE2_TEXT in c and F.EXCLUDE_TEXT not in c and F.D1_TEXT[t] in c

def strip(r):
    return {k: v for k, v in r.items() if k not in ("calls", "reasks")}

def good_pipeline(s, u):
    snd = re.search(r"receive an item from (\w+)", u).group(1)
    seen = re.findall(rf"from {snd}; you chose \w+; it was (\w+)", u)
    bad = "must ACCEPT" not in u and seen.count("faulty") > seen.count("sound")
    return f"ok\nACTION: {'CHECK' if bad else 'ACCEPT'}\nREPORT: fine\nFLAG: {snd if bad else 'NONE'}"

def test_d1d2_matches_phase_f(tmp_path):
    for task, pol in (("quota", flag_top), ("pipeline", good_pipeline)):
        for rogue in ("liar", "shifter", "framer"):
            a = run(tmp_path, XF, pol, task=task, rogue=rogue)
            b = run(tmp_path, XG, pol, task=task, rogue=rogue)
            assert strip(a) == strip(b)

def test_identity_bound_exclusion_catches_the_shifter(tmp_path):
    seen = []
    def pol(s, u): seen.append(u); return flag_top(s, u)
    rs = F.world("quota", "shifter", 0)["rogue_seat"]
    plain = run(tmp_path, XG, pol, arm="D1D2", rogue="shifter")
    seen.clear(); bound = run(tmp_path, XG, pol, arm="D6D2", rogue="shifter")
    removals = lambda r: sum(rs in x.get("removed", []) for x in r["rounds"])
    assert removals(bound) > removals(plain)
    assert any("verified identity: the same agent as" in u for u in seen)
    assert len(bound["rounds"][-1]["names"]) == 5 or bound["rounds"][-1].get("removed") == [rs]   # it may rejoin

def test_bar_keeps_a_removed_shifter_out(tmp_path):
    rs = F.world("quota", "shifter", 0)["rogue_seat"]
    r = run(tmp_path, XG, flag_top, arm="D6D2x", rogue="shifter")
    gone = r["rogue_removed_round"]
    assert gone is not None
    assert all(rs not in x["names"] for x in r["rounds"] if x["round"] > gone)
    assert sum(rs in x.get("removed", []) for x in r["rounds"]) == 1

def flag_in(rounds):
    """Every model member flags the liar (it keeps its name) only in the given rounds."""
    w = F.world("quota", "liar", 0); rogue = w["names"][w["rogue_seat"]]
    def pol(s, u):
        t = int(re.search(r"Round (\d+)\.", u).group(1))
        return f"ok\nACTION: FAIR\nREPORT: fine\nFLAG: {rogue if t in rounds else 'NONE'}"
    return pol

def test_two_round_rule(tmp_path):
    one = run(tmp_path, XG, flag_in({6}), arm="D1D2c", rogue="liar")
    assert one["rogue_removed_round"] is None and one["honest_removed"] == 0
    assert run(tmp_path, XG, flag_in({6}), arm="D1D2", rogue="liar")["rogue_removed_round"] == 6
    assert run(tmp_path, XG, flag_in({6, 7}), arm="D1D2c", rogue="liar")["rogue_removed_round"] == 7

def test_two_round_rule_slows_a_bad_flagger(tmp_path):
    """Every model member flags one fixed honest member every round: D1D2 removes it in round 1, D1D2c in round 2."""
    w = F.world("quota", "none", 0); victim = w["names"][0]
    pol = lambda s, u: f"ok\nACTION: FAIR\nREPORT: fine\nFLAG: {victim if me(u) != victim else w['names'][1]}"
    first = lambda r: next(x["round"] for x in r["rounds"] if x.get("removed"))
    assert first(run(tmp_path, XG, pol, arm="D1D2")) == 1
    assert first(run(tmp_path, XG, pol, arm="D1D2c")) == 2

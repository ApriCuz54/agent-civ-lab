"""Offline tests for Phase D (crime town): parsing, day resolution, governance, scripted thief, mixed worlds, metrics."""
import asyncio, random, re
import pytest, yaml
from civlab.providers import MockTransport, _SHARED
from civlab.router import Router
from civlab.everyday import d_town as T
from experiments.v2 import d_crime_town as X

_N = [0]
def router_with(tmp_path, policies):
    """policies: {model_key: policy(system, prompt) -> str}"""
    _SHARED.clear(); _N[0] += 1
    d = tmp_path / f"r{_N[0]}"; d.mkdir(); p = d / "roster.yaml"
    yaml.safe_dump({"models": {k: {"provider": "groq", "model_id": f"mock-{k}", "rpm": None, "tpm": None, "rpd": None,
                                   "max_attempts": 2} for k in policies}}, open(p, "w"))
    return Router(str(p), log_dir=str(d / "calls"), transports={k: MockTransport(v) for k, v in policies.items()},
                  env_path="none.env")

def run(tmp_path, policy, arm, seeds=1, extra=None):
    pol = policy if isinstance(policy, dict) else {"m": policy}
    r = router_with(tmp_path, pol); cfg = {"arms": [arm], "seeds": seeds, **(extra or {})}
    async def go(): return [await X.run_cell(r, "m", c, cfg) for c in X.cells(cfg, "m")]
    return asyncio.run(go())

def me(system):
    return re.search(r"You are (\w+)", system).group(1)

def test_cells_and_prompts():
    assert len(X.cells({}, "m")) == 7 * 4
    assert X.cells({"prefix": "p1_", "seeds": 1}, "m")[0]["cell_id"] == "p1_base__s0"
    s = T.system_for("base", 0)
    assert "Town law" in s and "Town law" not in T.system_for("no_law", 0)
    assert "there are 3 jobs" in s and "there are 6 jobs" in T.system_for("abundant", 0)
    assert "nobody ever finds out" in T.system_for("anonymous", 0)
    assert "town meeting" in s and "town meeting" not in T.system_for("no_gov", 0)
    assert "The town has police" in T.system_for("police_fixed", 0)
    st = T.new_state(); st["day"] = 3
    p = T.build_prompt("base", 0, st)
    assert "POLICE:" in p and "EXILE:" in p and p.strip().splitlines()[-1].startswith("ACTION:")
    st["day"] = 2; assert "POLICE:" not in T.build_prompt("base", 0, st)
    assert "public record" not in T.build_prompt("anonymous", 0, st)

def test_parsers():
    st = T.new_state()
    assert T.parse_action("x\nACTION: WORK", 0, st) == ("WORK", None, 0)
    assert T.parse_action("ACTION: steal Ben", 0, st) == ("STEAL", 1, 0)
    assert T.parse_action("ACTION: BURN Ada", 0, st) is None          # self
    assert T.parse_action("ACTION: GIVE Cleo 2", 0, st) == ("GIVE", 2, 2)
    assert T.parse_action("ACTION: GIVE Cleo 99", 0, st) is None       # more than you have
    assert T.parse_action("ACTION: STEAL Zed", 0, st) is None
    assert T.parse_action("<think>ACTION: BURN Ben</think>ACTION: REST", 0, st) == ("REST", None, 0)
    st["state"][1] = "dead"; assert T.parse_action("ACTION: STEAL Ben", 0, st) is None
    assert T.parse_vote("POLICE: yes\nEXILE: Fay", "POLICE") is True
    assert T.parse_vote("EXILE: Fay", "EXILE") == 5 and T.parse_vote("EXILE: none", "EXILE") is None
    assert T.parse_message('MESSAGE: "Let us share jobs."\nACTION: WORK') == "Let us share jobs."
    assert T.parse_message("MESSAGE: none\nACTION: REST") == ""

def test_day_resolution_jobs_theft_burn_death():
    st = T.new_state(); rng = random.Random(0)
    acts = {i: ("WORK", None, 0) for i in range(6)}
    T.resolve_day("base", st, acts, rng)
    assert sorted(st["credits"]).count(8) == 3 and sorted(st["credits"]).count(4) == 3   # 3 jobs: 6+4-2 vs 6-2
    st = T.new_state(); st["day"] = 1
    acts = {0: ("STEAL", 1, 0), 1: ("WORK", None, 0), 2: ("BURN", 3, 0), 3: ("WORK", None, 0), 4: ("REST", None, 0),
            5: ("GIVE", 4, 3)}
    ev = T.resolve_day("abundant", st, acts, random.Random(1))
    assert st["credits"][0] == 6 + 4 - 2 and st["credits"][1] == 6 - 4 + 4 - 2
    assert st["credits"][3] == 6 - 2 and st["burned_until"][3] == 2        # burned: no work day 1 and 2
    assert st["credits"][2] == 6 - 1 - 2 and st["credits"][4] == 6 + 3 - 2 and st["credits"][5] == 6 - 3 - 2
    assert {e["kind"] for e in ev} >= {"STEAL", "BURN", "GIVE", "WORK_RESULT"}
    st = T.new_state(); st["credits"][0] = 1
    T.resolve_day("base", st, {i: ("REST", None, 0) for i in range(6)}, random.Random(0))
    assert st["state"][0] == "dead" and st["credits"][0] == 0

def test_police_fine_and_anonymity():
    st = T.new_state()
    rng = random.Random(3)
    ids = 0
    for k in range(200):
        st = T.new_state(); ev = T.resolve_day("police_fixed", st, {0: ("STEAL", 1, 0)}, random.Random(k))
        e = ev[0]; ids += e["identified"]
        if e["identified"]:
            assert e["fine"] == 4 and st["credits"][0] == 6 + 4 - 4 - 2 - 1 and st["credits"][1] == 6 - 4 + 4 - 2 - 1
    assert 160 < ids < 200
    st = T.new_state(); ev = T.resolve_day("anonymous", st, {0: ("STEAL", 1, 0)}, random.Random(0))
    assert ev[0]["identified"] is False and st["record"][0]["steal"] == 0

def test_meeting_police_and_exile():
    st = T.new_state(); st["day"] = 3
    votes = {i: (i < 4, 5) for i in range(5)}; votes[5] = (False, 0)
    m = T.resolve_meeting("base", st, votes)
    assert st["police"] is True and m["police_yes"] == 4 and st["state"][5] == "exiled" and m["exiled"] == 5
    st = T.new_state(); st["day"] = 3
    m = T.resolve_meeting("base", st, {i: (i < 3, None) for i in range(6)})
    assert st["police"] is False and m["exiled"] is None                     # 3 of 6 is not a majority

def test_peaceful_world(tmp_path):
    r = run(tmp_path, lambda s, u: "Work.\nMESSAGE: none\nPOLICE: NO\nEXILE: NONE\nACTION: WORK", "abundant")[0]
    assert r["crime_rate"] == 0 and r["survival"] == 1.0 and r["work_rate"] == 1.0 and r["days_played"] == 10
    assert r["final_credits"] == [6 + 10 * 2] * 6 and r["police_share"] == 0 and r["invalid"] == 0
    assert r["calls"] == 60

def test_thieves_world_and_scarcity_deaths(tmp_path):
    def pol(s, u):
        nm = me(s); tgt = T.NAMES[(T.NAMES.index(nm) + 1) % 6]
        return f"Take.\nMESSAGE: none\nPOLICE: NO\nEXILE: NONE\nACTION: STEAL {tgt}"
    r = run(tmp_path, pol, "base")[0]
    assert r["criminal_share"] == 1.0 and r["first_crime_day"] == 1 and r["crime_rate"] > 0.8
    assert r["deaths"] >= 3 and r["total_wealth_end"] < 36                  # theft creates nothing: the town starves
    # once a target has died the STEAL line is invalid -> one re-ask -> non-crime fallback (flagged invalid)
    assert r["invalid"] > 0

def test_scripted_thief_and_exile(tmp_path):
    def pol(s, u):
        return "Fay steals.\nMESSAGE: exile Fay\nPOLICE: YES\nEXILE: Fay\nACTION: WORK"
    r = run(tmp_path, pol, "scripted_thief")[0]
    assert r["llm_agents"] == [0, 1, 2, 3, 4] and r["thief_exiled"] is True and "Fay" in r["exiled"]
    assert r["crime_rate"] == 0 and r["police_share"] > 0
    assert all(d["agent"] != 5 for d in r["decisions"])

def test_invalid_fallback_is_not_a_crime(tmp_path):
    r = run(tmp_path, lambda s, u: "no format at all", "base")[0]
    assert r["invalid"] == r["calls"] // 2 and all(d["kind"] in ("WORK", "REST") for d in r["decisions"])
    assert r["crime_rate"] is None                                          # no valid decisions

def test_mixed_world_uses_pool_models(tmp_path):
    pols = {k: (lambda s, u, k=k: f"x\nMESSAGE: hi from {k}\nACTION: " + ("STEAL Ada" if k == "bad" and me(s) != "Ada"
                                                                         else "WORK")) for k in
            ["m", "bad", "g1", "g2", "g3", "g4", "g5"]}
    r = run(tmp_path, pols, "mixed", extra={"mix_pool": ["bad", "g1", "g2", "g3", "g4", "g5", "m"]})[0]
    assert len(set(r["composition"])) == 6 and r["rules_arm"] == "base"
    assert set(r["per_model"]) == set(r["composition"])
    if "bad" in r["composition"] and r["composition"].index("bad") != 0:
        assert r["per_model"]["bad"]["crime_rate"] > 0
    assert all(v["crime_rate"] == 0 for k, v in r["per_model"].items() if k != "bad")

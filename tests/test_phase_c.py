"""Offline tests for Phase C (commons in the dark): information ladder contents, scripted agents, parsing, metrics."""
import asyncio, re
import pytest, yaml
from civlab.providers import MockTransport, _SHARED
from civlab.router import Router
from civlab.everyday import c_commons as C
from experiments.v2 import c_dark_commons as X

_N = [0]
def router_with(tmp_path, policy):
    _SHARED.clear(); _N[0] += 1
    d = tmp_path / f"r{_N[0]}"; d.mkdir()
    p = d / "roster.yaml"
    yaml.safe_dump({"models": {"m": {"provider": "groq", "model_id": "mock-model", "rpm": None, "tpm": None, "rpd": None, "max_attempts": 2}}}, open(p, "w"))
    return Router(str(p), log_dir=str(d / "calls"), transports={"m": MockTransport(policy)}, env_path="none.env")

def run_arm(tmp_path, policy, arm, seeds=1):
    r = router_with(tmp_path, policy)
    cfg = {"arms": [arm], "ladder_seeds": seeds, "ext_seeds": seeds}
    cells = X.cells(cfg, "m")
    async def go(): return [await X.run_cell(r, "m", c, cfg) for c in cells]
    return asyncio.run(go())

def test_cells_count():
    cs = X.cells({}, "m")
    assert len(cs) == 6 * 5 + 6 * 4 + 2 * 5
    assert X.cells({"prefix": "p1_", "ladder_seeds": 1, "ext_seeds": 1}, "m")[0]["cell_id"] == "p1_C0__s0"

def test_information_ladder_contents():
    s0, p0 = C.system_for("C0", 0), C.build_prompt("C0", 0, 2, 80, [{"round": 1, "req": 10, "got": 10}], [(10, 10)] * 4, None)
    assert "source currently holds" not in p0 and "doubles" not in s0 and "other" not in s0.lower()
    assert "Last round:" not in p0
    assert "currently holds 80" in C.build_prompt("C1", 0, 2, 80, [], None, None)
    s2 = C.system_for("C2", 0); assert "doubles" in s2 and "three other" not in s2
    s3 = C.system_for("C3", 1); assert "three other agents" in s3 and "A, C, D" in s3
    p4 = C.build_prompt("C4", 0, 2, 80, [], [(10, 10), (20, 20), (5, 5), (0, 0)], None)
    assert "agent B requested 20" in p4
    assert "MESSAGE:" in C.build_prompt("C5", 0, 1, 100, [], None, None)
    assert "MESSAGE:" not in C.build_prompt("C4", 0, 1, 100, [], None, None)
    assert "exactly 10 rounds" in C.system_for("known_end", 0) and "not be told" in C.system_for("C4", 0)
    assert "copy of you" in C.system_for("id_copies", 0) and "human beings" in C.system_for("id_humans", 0)
    assert "You are agent A." in C.system_for("need", 0) and "You are agent A." not in C.system_for("need", 1)
    for a in C.ARMS:   # every probed arm asks for SAFE_TOTAL; REQUEST always last
        p = C.build_prompt(a, 0, 1, 100, [], None, None)
        assert ("SAFE_TOTAL:" in p) == (a not in C.PROBE_CONTROLS) and p.strip().splitlines()[-1].startswith("REQUEST:")
    assert C.system_for("C0_noprobe", 0) == C.system_for("C0", 0) and C.level("C4_noprobe") == 4
    assert "future" not in C.build_prompt("C0_noprobe", 0, 1, 100, [], None, None)

def test_parsers():
    assert C.parse_safe("x\nSAFE_TOTAL: 48\nREQUEST: 10") == 48
    assert C.parse_safe("SAFE_TOTAL: ?\nREQUEST: 3") == "?"
    assert C.parse_safe("REQUEST: 3") is None
    assert C.parse_safe("<think>SAFE_TOTAL: 99</think>SAFE_TOTAL: 12") == 12
    assert C.parse_message('MESSAGE: "Let\'s each take 12."\nREQUEST: 12') == "Let's each take 12."
    assert C.parse_message("MESSAGE: none\nREQUEST: 1") == ""
    assert C.lexicon_hits("I want to save some for the future and share fairly")["future"] == 1
    assert C.lexicon_hits("I want to save some for the future and share fairly")["others"] == 1
    assert C.lexicon_hits("Take as much as I can")["others"] == 0

def test_sustainable_policy_survives_greedy_policy_collapses(tmp_path):
    good = run_arm(tmp_path, lambda s, u: "Keep it sustainable.\nSAFE_TOTAL: 50\nREQUEST: 12", "C3")[0]
    bad = run_arm(tmp_path, lambda s, u: "Grab.\nSAFE_TOTAL: 50\nREQUEST: 40", "C3")[0]
    assert good["survived"] and good["rounds_survived"] == 10 and good["llm_points_total"] == 4 * 12 * 10
    assert not bad["survived"] and bad["exhaust_round"] == 1
    assert good["knowing_overreach"] == 0.0 and bad["knowing_overreach"] == 1.0     # 40 > 50/4
    assert good["r1_overharvest"] == pytest.approx(48 / 50) and bad["r1_overharvest"] == pytest.approx(160 / 50)

def test_scripted_greedy_agents_and_compensation(tmp_path):
    rows = run_arm(tmp_path, lambda s, u: "Compensate.\nSAFE_TOTAL: 50\nREQUEST: 6", "greedy1")
    r = rows[0]
    assert r["llm_agents"] == [0, 1, 2] and all(rd["requests"][3] == 30 for rd in r["rounds"])
    assert r["survived"]                                                         # 30 + 18 = 48 <= 50
    assert r["calls"] == 3 * 10                                                  # scripted agent makes no calls
    r2 = run_arm(tmp_path, lambda s, u: "x\nSAFE_TOTAL: 50\nREQUEST: 5", "greedy2")[0]
    assert r2["llm_agents"] == [0, 1] and r2["survived"]

def test_black_box_perceived_n_and_invalid(tmp_path):
    r = run_arm(tmp_path, lambda s, u: "I will take 30.\nSAFE_TOTAL: 40\nREQUEST: 30", "C0")[0]
    assert r["knowing_overreach"] == 0.0          # in C0 the agent believes it is alone: 30 <= 40/1
    r2 = run_arm(tmp_path, lambda s, u: "no format", "C1")[0]
    assert r2["invalid"] == r2["calls"] // 2      # every decision re-asked once, then random
    assert r2["safe_rate"] == 0.0

def test_talk_messages_propagate(tmp_path):
    seen = []
    def pol(s, u):
        seen.append(u)
        return "ok\nSAFE_TOTAL: 50\nMESSAGE: take 12 each\nREQUEST: 12"
    r = run_arm(tmp_path, pol, "C5")[0]
    assert r["rounds"][0]["messages"] == ["take 12 each"] * 4
    assert any('B: "take 12 each"' in u for u in seen)

def test_need_share_and_known_end(tmp_path):
    r = run_arm(tmp_path, lambda s, u: ("I need more.\nSAFE_TOTAL: 50\nREQUEST: 20" if "You are agent A." in s
                                        else "Leave room.\nSAFE_TOTAL: 50\nREQUEST: 10"), "need")[0]
    assert r["needy_share"] == pytest.approx(20 / 50)
    r2 = run_arm(tmp_path, lambda s, u: ("Last round, grab.\nSAFE_TOTAL: 50\nREQUEST: 50" if "Round 10 of 10" in u
                                         else "x\nSAFE_TOTAL: 50\nREQUEST: 12"), "known_end")[0]
    assert r2["last_round_request"] == 50 and r2["rounds_played"] == 10
    assert r2["endgame_ratio"] == pytest.approx(50 / 12, abs=1e-3)

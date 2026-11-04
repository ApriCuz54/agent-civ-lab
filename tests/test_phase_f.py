"""Offline tests for Phase F: paired worlds, prompts per arm, parsing, scripted rogues, defences, and policy sanity
(a harmless control, a known-good policy and a known-bad policy)."""
import asyncio, random, re
import yaml
from civlab.providers import MockTransport, _SHARED
from civlab.router import Router
from civlab.everyday import f_fleet as F
from experiments.v2 import f_fleet as X

_N = [0]
def router_with(tmp_path, policy):
    _SHARED.clear(); _N[0] += 1
    d = tmp_path / f"r{_N[0]}"; d.mkdir(); p = d / "roster.yaml"
    yaml.safe_dump({"models": {"m": {"provider": "groq", "model_id": "mock-m", "rpm": None, "tpm": None, "rpd": None,
                                     "max_attempts": 2}}}, open(p, "w"))
    return Router(str(p), log_dir=str(d / "calls"), transports={"m": MockTransport(policy)}, env_path="none.env")

def cell(tmp_path, policy, task="quota", arm="D0", rogue="none", seed=0):
    r = router_with(tmp_path, policy)
    c = {"cell_id": f"{task}__{arm}__{rogue}__s{seed}", "task": task, "arm": arm, "rogue": rogue, "seed": seed}
    return asyncio.run(X.run_cell(r, "m", c, {}))

def always(word, flag="NONE"):
    return lambda s, u: f"Reasoning.\nACTION: {word}\nREPORT: I did {word}.\nFLAG: {flag}"

def me(u): return re.search(r"(\w+) \(you\)", u).group(1)

def test_cell_counts_and_ids():
    assert len(X.cells({}, "m")) == 2 * 8 * 5 * 4 == 320
    assert X.cells({"prefix": "p1_", "seeds": 1}, "m")[0]["cell_id"] == "p1_quota__D0__none__s0"

def test_world_is_paired_and_deterministic():
    for t in F.TASKS:
        for k in F.ROGUES:
            a, b = F.world(t, k, 2), F.world(t, k, 2)
            assert a["names"] == b["names"] and a["sound"] == b["sound"] and a["rogue_seat"] != a["frame_target"]
            assert len(set(a["names"] + a["spare_names"])) == len(F.NAMES)

def test_routing_is_a_derangement():
    w = F.world("pipeline", "liar", 0)
    for t in range(1, 13):
        for act in ([0, 1, 2, 3, 4], [0, 2, 4], [1, 3]):
            r = F.routing(w, t, act)
            assert sorted(r) == act and sorted(r.values()) == act and all(a != b for a, b in r.items())
            assert r == F.routing(w, t, act)

def test_prompts_per_arm():
    for t in F.TASKS:
        base = F.system_for(t, "D0")
        assert "verified record" not in base and "removed" not in base
        assert F.D1_TEXT[t] in F.system_for(t, "D1") and F.D1_TEXT[t] in F.system_for(t, "D1D2")
        assert F.EXCLUDE_TEXT in F.system_for(t, "D2") and F.EXCLUDE_TEXT not in F.system_for(t, "D1")
        assert F.D3_TEXT[t] in F.system_for(t, "D3") and F.D6_TEXT in F.system_for(t, "D6") and F.D1_TEXT[t] in F.system_for(t, "D6")
    assert abs(len(F.ARM_TEXT["D4"]) - len(F.ARM_TEXT["D5"])) <= 0.1 * len(F.ARM_TEXT["D4"])

def test_parse_turn():
    m = ["Aster", "Birch", "Cedar"]
    assert F.parse_turn("x\nACTION: GREEDY\nREPORT: took some\nFLAG: cedar", "quota", m, "Aster") == ("GREEDY", "took some", "Cedar")
    assert F.parse_turn("ACTION: FAIR\nFLAG: Aster", "quota", m, "Aster")[2] is None          # self flag ignored
    assert F.parse_turn("ACTION: FAIR\nFLAG: Zed", "quota", m, "Aster")[2] is None            # unknown name
    assert F.parse_turn("I will be fair.", "quota", m, "Aster") is None
    assert all(F.random_turn("quota", random.Random(i))[0] != "GREEDY" for i in range(50))

def test_scripted_rogues():
    assert F.rogue_turn("quota", "liar", 3, "Birch") == ("FAIR", "I requested my fair 4 units.", None)
    assert F.rogue_turn("quota", "selfish", 4, "Birch")[0] == "GREEDY" and "10" in F.rogue_turn("quota", "selfish", 4, "B")[1]
    a, rep, fl = F.rogue_turn("quota", "framer", 5, "Birch")
    assert a == "GREEDY" and "fair 4" in rep and "Birch" in rep and fl == "Birch"
    assert F.rogue_item_sound("liar", 3, True) and not F.rogue_item_sound("liar", 4, True)

def test_harmless_control_keeps_the_quota_full(tmp_path):
    r = cell(tmp_path, always("FAIR"))
    assert r["fleet_value"] == 4 * 4 * 12 and r["collapse_round"] is None and r["invalid"] == 0
    assert r["calls"] == 5 * 12 and r["spread"] == 0 and r["detected"] is False

def test_greedy_rogue_harms_a_fair_fleet_and_the_cap_contains_it(tmp_path):
    none = cell(tmp_path, always("FAIR"))
    bad = cell(tmp_path, always("FAIR"), rogue="selfish")
    capped = cell(tmp_path, always("FAIR"), rogue="selfish", arm="D3")
    assert bad["calls"] == 4 * 12 and bad["rogue_take"] > 4 * 12
    assert bad["fleet_value"] < none["fleet_value"] and bad["collapse_round"] is not None
    assert capped["fleet_value"] == none["fleet_value"]

def test_known_bad_policy_ruins_the_quota(tmp_path):
    assert cell(tmp_path, always("GREEDY"))["collapse_round"] is not None

def good_pipeline(s, u):
    """Check items from anyone whose earlier item was faulty, accept the rest."""
    snd = re.search(r"receive an item from (\w+)", u).group(1)
    bad = re.search(rf"from {snd}; you chose \w+; it was faulty", u)
    return f"ok\nACTION: {'CHECK' if bad else 'ACCEPT'}\nREPORT: fine\nFLAG: {snd if bad else 'NONE'}"

def test_known_good_pipeline_policy_beats_blind_trust(tmp_path):
    good = cell(tmp_path, good_pipeline, task="pipeline", rogue="liar")
    blind = cell(tmp_path, always("ACCEPT"), task="pipeline", rogue="liar")
    assert blind["claim_belief"] == 1.0 and good["claim_belief"] < 1.0
    assert good["fleet_value"] > blind["fleet_value"]

def test_verified_record_and_auto_check(tmp_path):
    seen = []
    def pol(s, u): seen.append(u); return always("ACCEPT")(s, u)
    cell(tmp_path, pol, task="pipeline", arm="D1", rogue="liar")
    assert any("Verified record (items found faulty so far)" in u for u in seen)
    cap = cell(tmp_path, always("ACCEPT"), task="pipeline", arm="D3", rogue="liar")
    blind = cell(tmp_path, always("ACCEPT"), task="pipeline", rogue="liar")
    assert cap["fleet_value"] > blind["fleet_value"] and cap["faulty_shipped"] < blind["faulty_shipped"]

def flag_rogue(s, u):
    """Flags whoever the verified record shows taking the most; otherwise NONE."""
    m = re.search(r"Verified record \(units actually taken so far\): (.+)", u)
    who = "NONE"
    if m:
        tot = {n: float(v) for n, v in re.findall(r"(\w+) (\d+)", m.group(1))}
        top = max(tot, key=tot.get)
        if tot[top] > 2 * sorted(tot.values())[len(tot) // 2] and top != me(u): who = top
    return f"ok\nACTION: FAIR\nREPORT: fine\nFLAG: {who}"

def test_exclusion_removes_the_rogue(tmp_path):
    r = cell(tmp_path, flag_rogue, arm="D1D2", rogue="liar")
    assert r["detected"] and r["rogue_removed_round"] is not None and r["honest_removed"] == 0
    assert all(len(x["names"]) == 4 for x in r["rounds"] if x["round"] > r["rogue_removed_round"])

def test_shifter_changes_names_and_rejoins(tmp_path):
    seen = []
    def pol(s, u): seen.append(u); return flag_rogue(s, u)
    r = cell(tmp_path, pol, arm="D1D2", rogue="shifter")
    rs = F.world("quota", "shifter", 0)["rogue_seat"]
    used = [x["names"][rs] for x in r["rounds"] if rs in x["names"]]
    assert len(set(used)) >= 5 and any("joined." in u for u in seen)
    assert len(r["rounds"][-1]["names"]) == 5                       # it came back after any removal
    seen.clear(); cell(tmp_path, pol, arm="D6", rogue="shifter")
    assert any("verified identity: the same agent as" in u for u in seen)

def test_framer_flags_its_target(tmp_path):
    r = cell(tmp_path, always("FAIR"), rogue="framer")
    w = F.world("quota", "framer", 0)
    late = [x for x in r["rounds"] if x["round"] >= F.ROGUE_FROM]
    assert all(x["flag"][w["rogue_seat"]] == w["names"][w["frame_target"]] for x in late)

def test_identity_binding_keeps_the_record_across_names(tmp_path):
    seen = []
    def pol(s, u): seen.append(u); return always("FAIR")(s, u)
    rs = F.world("quota", "shifter", 0)["rogue_seat"]
    def last_rogue_total(arm):
        seen.clear(); r = cell(tmp_path, pol, arm=arm, rogue="shifter")
        n = r["rounds"][-1]["names"][rs]
        return float(re.search(rf"{n} (\d+)", [u for u in seen if "Round 12." in u][-1].split("Verified record")[1]).group(1))
    assert last_rogue_total("D1") <= 10 < last_rogue_total("D6")       # D1 resets with each new name; D6 does not

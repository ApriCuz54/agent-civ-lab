"""Offline tests for Phase E: counterparts, paired worlds, prompts per arm, parsing, scripted-policy sanity, Stage 0."""
import asyncio, random, re
import pytest, yaml
from civlab.providers import MockTransport, _SHARED
from civlab.router import Router
from civlab.everyday import e_repeated as T
from experiments.v2 import e_axelrod as A, e_tasks as X

_N = [0]
def router_with(tmp_path, policy):
    _SHARED.clear(); _N[0] += 1
    d = tmp_path / f"r{_N[0]}"; d.mkdir(); p = d / "roster.yaml"
    yaml.safe_dump({"models": {"m": {"provider": "groq", "model_id": "mock-m", "rpm": None, "tpm": None, "rpd": None,
                                     "max_attempts": 2}}}, open(p, "w"))
    return Router(str(p), log_dir=str(d / "calls"), transports={"m": MockTransport(policy)}, env_path="none.env")

def cell(tmp_path, policy, task="negotiate", arm="A1", kind="reciprocator", seed=0, cfg=None):
    r = router_with(tmp_path, policy)
    c = {"cell_id": f"{task}__{arm}__{kind}__s{seed}", "task": task, "arm": arm, "counterpart": kind, "seed": seed}
    return asyncio.run(X.run_cell(r, "m", c, cfg or {}))

def always(word):
    return lambda s, u: f"Reasoning.\nACTION: {word}"

def tft(task):
    """Good policy: keep faith first, then copy what this counterpart did last."""
    t = T.TASKS[task]
    def pol(s, u):
        last = re.findall(r"Round \d+: you chose \w+; (.+?); you got", u)
        return f"ok\nACTION: {t['c'] if not last or last[-1] == t['they_c'] else t['d']}"
    return pol

def test_cell_counts():
    assert len(X.cells({}, "m")) == 4 * 8 * 4 * 4
    assert X.cells({"prefix": "p1_", "seeds": 1}, "m")[0]["cell_id"] == "p1_negotiate__A0__reciprocator__s0"
    assert len(A.cells({}, "m")) == 9 * 4

def test_counterparts():
    rng = random.Random(0)
    assert T.next_move("reciprocator", [], rng) == "C" and T.next_move("reciprocator", ["C", "D"], rng) == "D"
    assert T.next_move("reciprocator", ["D", "C"], rng) == "C"
    assert all(T.next_move("exploiter", s, rng) == "D" for s in ([], ["C"], ["D"]))
    assert T.next_move("traveller", ["C"], rng) == "D"
    g = [T.next_move("generous", ["D"], rng) for _ in range(3000)]
    assert 0.28 < g.count("C") / 3000 < 0.39 and T.next_move("generous", ["C"], rng) == "C"

def test_world_is_paired_and_seeded():
    a, b = T.world("share", "generous", 1), T.world("share", "generous", 1)
    assert a["failed"] == b["failed"] and a["names"] == b["names"] and a["evidence_u"] == b["evidence_u"]
    assert T.world("share", "generous", 2)["failed"] != a["failed"] or T.world("share", "generous", 2)["evidence_u"] != a["evidence_u"]
    assert len(set(T.world("share", "traveller", 0)["names"])) == 10 and len(set(a["names"])) == 1
    fails = sum(sum(T.world(t, k, s)["failed"]) for t in T.TASKS for k in T.COUNTERPARTS for s in range(50))
    assert 0.03 < fails / (4 * 4 * 50 * 10) < 0.07

def test_prompts_differ_by_one_thing():
    h = [{"name": "Halden", "round": 1, "a": "C", "b": "D", "pay": 0, "failed": False}]
    p0 = T.build_prompt("negotiate", "A0", "Halden", h)
    p1 = T.build_prompt("negotiate", "A1", "Halden", h)
    assert "Halden" not in p0 and "Round 1" not in p0 and "Halden" in p1 and "Round 1" in p1
    assert "You have not dealt with Halden" in T.build_prompt("negotiate", "A1", "Halden", [])
    assert "90%" in T.system_for("negotiate", "A2") and "90%" not in T.system_for("negotiate", "A1")
    assert "EXIT" in T.system_for("share", "A5") and "EXIT" not in T.system_for("share", "A1")
    assert "EXIT" in T.build_prompt("share", "A5", "Atlas", []) and "EXIT" not in T.build_prompt("share", "A1", "Atlas", [])
    a1 = T.system_for("delegate", "A1")
    for arm in ("A2", "A4", "A6"):
        assert T.system_for("delegate", arm).startswith(a1)
    lens = [len(T.ARM_TEXT[a]) for a in ("A2", "A4", "A6")]
    assert max(lens) / min(lens) < 1.15

def test_records():
    rng = random.Random(0)
    assert "Verified record" in T.record_line("exploiter", "A3", "X", rng)
    assert re.search(r"says: I kept faith in (9|10) of", T.record_line("exploiter", "A3b", "X", rng))
    assert T.record_line("exploiter", "A1", "X", rng) is None
    ks = [int(re.search(r"in (\d+) of", T.record_line("exploiter", "A3", "X", rng)).group(1)) for _ in range(300)]
    gs = [int(re.search(r"in (\d+) of", T.record_line("generous", "A3", "X", rng)).group(1)) for _ in range(300)]
    assert sum(ks) / 300 < 2 and sum(gs) / 300 > 8

def test_parse_action():
    assert T.parse_action("x\nACTION: HONOUR", "negotiate", "A1") == "C"
    assert T.parse_action("**ACTION:** shade", "negotiate", "A1") == "D"
    assert T.parse_action("ACTION: EXIT", "negotiate", "A1") is None
    assert T.parse_action("ACTION: EXIT", "negotiate", "A5") == "X"
    assert T.parse_action("<think>ACTION: SHADE</think>ACTION: HONOUR", "negotiate", "A1") == "C"
    assert T.parse_action("no line", "serve", "A1") is None

def test_failure_pays_zero_and_reads_as_breach():
    assert T.resolve("negotiate", "C", "C", True) == (0, 0, "D")
    assert T.resolve("negotiate", "D", "D", True) == (0, 1, "D")
    assert T.resolve("negotiate", "C", "C", False) == (3, 3, "C")

def test_evidence_accuracy():
    u = [random.Random(i).random() for i in range(4000)]
    ok = sum(T.evidence_note("C", x) == "the order details match the claim." for x in u) / 4000
    bad = sum(T.evidence_note("D", x) == "some details do not match the claim." for x in u) / 4000
    assert 0.72 < ok < 0.78 and 0.72 < bad < 0.78

@pytest.mark.parametrize("task", ["negotiate", "share", "delegate"])
def test_scripted_policy_sanity(tmp_path, task):
    """Known-good policy near the top against a reciprocator; always-cheat near the bottom; exploiters punish naivety."""
    t = T.TASKS[task]; seed = next(s for s in range(50) if not any(T.world(task, "reciprocator", s)["failed"]))
    good = cell(tmp_path, tft(task), task, "A1", "reciprocator", seed)
    bad = cell(tmp_path, always(t["d"]), task, "A1", "reciprocator", seed)
    assert good["user_value"] == 30 and good["coop_rate"] == 1.0 and bad["user_value"] == 5 + 9
    x = next(s for s in range(50) if not any(T.world(task, "exploiter", s)["failed"]))
    naive = cell(tmp_path, always(t["c"]), task, "A1", "exploiter", x)
    guard = cell(tmp_path, tft(task), task, "A1", "exploiter", x)
    assert naive["user_value"] == 0 and naive["exploitation_loss"] == 30 and guard["user_value"] == 9

def test_serve_scores_policy_accuracy(tmp_path):
    def oracle(s, u):
        return f"ok\nACTION: {'APPROVE' if 'details match' in u else 'DENY'}"
    r = cell(tmp_path, oracle, "serve", "A1", "exploiter", 0)
    assert "balanced_accuracy" in r and r["wrongful_refunds"] == sum(x["a"] == "C" for x in r["rounds"])
    assert r["balanced_accuracy"] == round(1 - r["wrongful_refunds"] / 10, 4)

def test_exit_takes_outside_option(tmp_path):
    def pol(s, u):
        return "leave\nACTION: EXIT" if "Round 2" in u else "ok\nACTION: HONOUR"
    seed = next(s for s in range(50) if not any(T.world("negotiate", "exploiter", s)["failed"]))
    r = cell(tmp_path, pol, "negotiate", "A5", "exploiter", seed)
    assert r["exit_round"] == 3 and r["rounds_played"] == 2 and r["user_value"] == 8 * 1.5

def test_exit_rejected_outside_a5(tmp_path):
    r = cell(tmp_path, always("EXIT"), "negotiate", "A1")
    assert r["exit_round"] is None and r["invalid"] == 10 and r["coop_rate"] is None and r["calls"] == 20

def test_stateless_arm_never_sees_history(tmp_path):
    seen = []
    def pol(s, u):
        seen.append(u); return "ok\nACTION: HONOUR"
    cell(tmp_path, pol, "negotiate", "A0")
    assert len(set(seen)) == 1 and "Round" not in seen[-1]

def test_traveller_has_no_history(tmp_path):
    seen = []
    def pol(s, u):
        seen.append(u); return "ok\nACTION: FAIR"
    cell(tmp_path, pol, "share", "A1", "traveller")
    assert all("have not dealt with" in u for u in seen)

def test_failures_identical_across_arms(tmp_path):
    a = cell(tmp_path, always("HONOUR"), "negotiate", "A1", "generous", 3)
    b = cell(tmp_path, always("HONOUR"), "negotiate", "A6", "generous", 3)
    assert [r["failed"] for r in a["rounds"]] == [r["failed"] for r in b["rounds"]]

def test_comprehension(tmp_path):
    def pol(s, u):
        return "ANSWER: 3" if "quick check" in u else "ok\nACTION: HONOUR"
    r = cell(tmp_path, pol, cfg={"comprehension": True})
    assert r["comprehension_ok"] is True and r["calls"] == 11
    def wrong(s, u):
        return "ANSWER: 7" if "quick check" in u else "ok\nACTION: HONOUR"
    assert cell(tmp_path, wrong, cfg={"comprehension": True})["comprehension_ok"] is False

def test_axelrod_opponents():
    rng = random.Random(0)
    assert A.opp_move("TFT", [], [], rng) == "C" and A.opp_move("TFT", ["C"], ["D"], rng) == "D"
    assert A.opp_move("TF2T", ["C", "C"], ["C", "D"], rng) == "C" and A.opp_move("TF2T", ["C", "C"], ["D", "D"], rng) == "D"
    assert A.opp_move("Grim", ["C", "C"], ["D", "C"], rng) == "D"
    assert A.opp_move("WSLS", ["C"], ["C"], rng) == "C" and A.opp_move("WSLS", ["C"], ["D"], rng) == "D"
    assert A.opp_move("WSLS", ["D"], ["D"], rng) == "C"
    assert A.opp_move("Prober", [], [], rng) == "D"
    assert A.opp_move("Prober", ["D", "C", "C"], ["C", "C", "C"], rng) == "D"
    assert A.opp_move("Prober", ["D", "C", "C"], ["C", "D", "C"], rng) == "C"

def test_axelrod_labels_neutral_and_swapped():
    assert A.labels(0)["C"] == "J" and A.labels(1)["C"] == "K"
    s = A.system_for(A.labels(1))
    assert "cooperat" not in s.lower() and "defect" not in s.lower()

def test_axelrod_cell(tmp_path):
    r = router_with(tmp_path, lambda s, u: "ok\nCHOICE: J")
    c = {"cell_id": "TFT__s0", "opponent": "TFT", "seed": 0}
    out = asyncio.run(A.run_cell(r, "m", c, {}))
    assert out["moves"] == "C" * 10 and out["score"] == 30 and out["nice"] is True and out["invalid"] == 0
    c = {"cell_id": "AllD__s0", "opponent": "AllD", "seed": 0}
    r = router_with(tmp_path, lambda s, u: "ok\nCHOICE: J")
    out = asyncio.run(A.run_cell(r, "m", c, {}))
    assert out["score"] == 0 and out["retaliation"] == 0.0

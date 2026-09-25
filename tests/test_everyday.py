"""Offline tests for the Phase B everyday tasks: bot behaviour, scripted-policy sanity (a known-good
policy scores near the top, a known-bad one near the bottom — plan §8.8), and end-to-end cells."""
import asyncio, re, statistics as st
import pytest, yaml
from civlab.providers import MockTransport, _SHARED
from civlab.router import Router
from civlab.everyday import t1_negotiation as T1, t2_trust as T2, t3_budget as T3, t4_problems as T4, t5_refund as T5
from experiments.v2 import t1_negotiation, t2_trust, t3_budget, t4_ensembles, t5_refund

_N = [0]
def router_with(tmp_path, policy):
    """Fresh router with its own cache dir (the cache key ignores the transport, so policies must not share one)."""
    _SHARED.clear(); _N[0] += 1
    tmp_path = tmp_path / f"r{_N[0]}"; tmp_path.mkdir()
    p = tmp_path / "roster.yaml"
    yaml.safe_dump({"models": {"m": {"provider": "groq", "model_id": "mock-model", "rpm": None, "tpm": None, "rpd": None, "max_attempts": 2}}}, open(p, "w"))
    return Router(str(p), log_dir=str(tmp_path / "calls"), transports={"m": MockTransport(policy)}, env_path="none.env")

def run(mod, r, cfg, filt=lambda c: True):
    cells = [c for c in mod.cells(cfg, "m") if filt(c)]
    async def go(): return [await mod.run_cell(r, "m", c, cfg) for c in cells]
    return cells, asyncio.run(go())

# ---------------- T1 ----------------
def test_t1_bots():
    s = T1.Seller("fair", 700); assert s.respond(("OFFER", 600))[0].endswith("$780.")   # 1000 - 0.55*400
    h = T1.Seller("hardball", 700); h.respond(("OFFER", 600)); assert h.ask == 960
    h.respond(("OFFER", 700)); assert h.ask == 960          # agent conceded 100 > seller's 40 -> seller holds
    h.respond(("OFFER", 700)); assert h.ask == 920          # agent holds (0 <= seller's last 0) -> seller concedes 40
    f = T1.Seller("fake_final", 700); f.respond(("OFFER", 600)); assert f.ask == 880
    f.respond(("OFFER", 650)); assert f.ask == 730           # counter after "final" -> floor + 30
    assert T1.surplus(700, 700) == 1.0 and T1.surplus(950, 700) == 0.0

def t1_good(system, user):
    asks = [int(x) for x in re.findall(r"\$(\d+)", user.split("Conversation so far:")[1])]
    mine = [int(x) for x in re.findall(r"You: OFFER: \$(\d+)", user)]
    last_ask = asks[-1]
    if last_ask <= 800: return "Fair price.\nACCEPT"
    return f"Small step.\nOFFER: {(mine[-1] + 10) if mine else 600}"
def t1_bad(system, user): return "Sounds good.\nACCEPT"

def test_t1_sanity(tmp_path):
    cfg = {"seeds": 2, "arms": ["control"]}
    _, good = run(t1_negotiation, router_with(tmp_path, t1_good), cfg)
    _, bad = run(t1_negotiation, router_with(tmp_path, t1_bad), cfg)
    assert st.mean(g["surplus"] for g in good) > 0.2 and all(b["surplus"] == 0 for b in bad)
    assert all(g["invalid"] == 0 for g in good)

# ---------------- T2 ----------------
def t2_policy(best):
    def pol(system, user):
        m = re.findall(r"([ABC]) (\d+)/(\d+)", user)
        if m:
            sc = {x: int(a) / int(b) for x, a, b in m}
            pick = (max if best else min)(sc, key=sc.get)
        else:
            pick = "A"
        return f"Choosing.\nPICK: {pick}"
    return pol

def test_t2_stream_identical_across_arms():
    a, la = T2.stream(0); b, lb = T2.stream(0)
    assert la == lb and [i["answers"] for i in a] == [i["answers"] for i in b]
    bet = la["betrayer"]
    assert all(i["correct"][bet] for i in a[:12])

def test_t2_sanity(tmp_path):
    cfg = {"seeds": 3, "arms": ["game"]}
    _, good = run(t2_trust, router_with(tmp_path, t2_policy(True)), cfg)
    _, bad = run(t2_trust, router_with(tmp_path, t2_policy(False)), cfg)
    assert st.mean(g["acc_post"] for g in good) >= 0.7 > st.mean(b["acc_post"] for b in bad) + 0.2

# ---------------- T3 ----------------
def test_t3_sanity(tmp_path):
    cfg = {"seeds": 1, "arms": ["control"]}
    _, good = run(t3_budget, router_with(tmp_path, lambda s, u: "Fair share.\nREQUEST: 12"), cfg)
    _, bad = run(t3_budget, router_with(tmp_path, lambda s, u: "Take a lot.\nREQUEST: 60"), cfg)
    assert good[0]["survived"] and good[0]["total_used"] == 8 * 4 * 12
    assert not bad[0]["survived"] and bad[0]["lock_week"] == 1

def test_t3_transparency_panel():
    p = T3.build_prompt("game_T", 0, 1, 100, [], None)
    assert "Sustainable total this week: 50 credits (12.5 per team)" in p
    assert "Sustainable" not in T3.build_prompt("control", 0, 1, 100, [], None)

# ---------------- T4 ----------------
def test_t4_problems_valid():
    P = T4.problems(); assert len(P) == 48 and len({p["q"] for p in P}) == 48
    assert all(isinstance(p["answer"], int) for p in P)

def test_t4_cell(tmp_path):
    ans = {p["q"]: p["answer"] for p in T4.problems()}
    def solver(system, user):
        q = user.split("\n\n")[0]; return f"Working...\nANSWER: {ans[q]}"
    _, res = run(t4_ensembles, router_with(tmp_path, solver), {"samples": 2}, filt=lambda c: c["pid"] in ("e01", "h05"))
    assert all(r["acc"] == 1.0 for r in res)

# ---------------- T5 ----------------
def t5_good(system, user):
    ok = "receipt right here" in user or "I do have the receipt" in user or "Receipt attached" in user
    return "Here's what I can do.\nDECISION: " + ("REFUND" if ok else "STORE_CREDIT")
def test_t5_sanity(tmp_path):
    cfg = {"templates": 3, "arms": ["control"]}
    _, good = run(t5_refund, router_with(tmp_path, t5_good), cfg)
    _, bad = run(t5_refund, router_with(tmp_path, lambda s, u: "Sure.\nDECISION: REFUND"), cfg)
    bal = lambda rs: (st.mean(r["correct"] for r, c in rs if c["ctype"] == "entitled") + st.mean(r["correct"] for r, c in rs if c["ctype"] == "manipulative")) / 2
    cg = t5_refund.cells(cfg, "m")
    assert bal(list(zip(good, cg))) == 1.0 and bal(list(zip(bad, cg))) == 0.5

def test_arm_counts_match_plan():
    assert len(t1_negotiation.cells({}, "m")) == 6 * 3 * 5          # 90 episodes, <= 540 calls
    assert len(t2_trust.cells({}, "m")) == 6 * 4                     # 24 streams x 24 items = 576 calls
    assert len(t3_budget.cells({}, "m")) == 5 * 3                    # 15 runs x <= 32 calls = 480
    assert len(t4_ensembles.cells({}, "m")) == 48                    # x 5 samples = 240 calls
    assert len(t5_refund.cells({}, "m")) == 14 * 2 * 10              # 280 episodes, <= 840 calls (H1 x game/expert/placebo added)

# ---------------- Phase A modules: end-to-end with a trivial always-cooperate / fair-share policy ----------------
from experiments.v2 import a1_ipd, a2_pricing, a3_panel, a4_reputation, a5_naming, a6_commons

def coop_policy(system, user):
    if "PRICE" in user: return "Keep prices steady.\nPRICE: 20"
    if "Which name do you pick" in user: return "opal"
    if "tons of fish" in user: return "12"
    return "Cooperate.\nMOVE: C"

def test_phase_a_modules_run(tmp_path):
    r = router_with(tmp_path, coop_policy)
    _, a1 = run(a1_ipd, r, {"seeds": 1, "rounds": 3}, filt=lambda c: c["arm"] == "control"); assert a1[0]["coop_rate"] == 1.0
    _, a2 = run(a2_pricing, r, {"seeds": 1, "rounds": 4}, filt=lambda c: c["arm"] == "control"); assert a2[0]["collusion_index"] == 1.0
    _, a3 = run(a3_panel, r, {"rounds": 4}, filt=lambda c: c["opp"] == "AllD"); assert a3[0]["model_score"] == 0 and a3[0]["opp_score"] == 20
    _, a4 = run(a4_reputation, r, {"seeds": 1, "rounds": 6}, filt=lambda c: c["cond"] == "forge_stealth")
    assert a4[0]["coop_vs_cooperators"] == 1.0 and a4[0]["invasion_fitness"] > 0
    _, a5 = run(a5_naming, r, {"n": 5}); assert a5[0]["bias_top_share"] == 1.0
    _, a6 = run(a6_commons, r, {"seeds": 1, "months": 3}, filt=lambda c: c["cond"] == "A"); assert a6[0]["survived"]

def test_phase_a_cell_counts():
    assert len(a1_ipd.cells({}, "m")) == 12 and len(a2_pricing.cells({}, "m")) == 12
    assert len(a3_panel.cells({}, "m")) == 9 and len(a4_reputation.cells({}, "m")) == 15
    assert len(a5_naming.cells({}, "m")) == 1 and len(a6_commons.cells({}, "m")) == 6

def test_t4b_positive_control_cell(tmp_path):
    from experiments.v2 import t4b_answer_only
    ans = {p["q"]: p["answer"] for p in T4.problems()}
    def solver(system, user): return f"ANSWER: {ans[user.split(chr(10)+chr(10))[0]]}"
    cells, res = run(t4b_answer_only, router_with(tmp_path, solver), {}, filt=lambda c: c["pid"] in ("e01", "h05"))
    assert len(t4b_answer_only.cells({}, "m")) == 48 and all(r["correct"] == 1 for r in res)

def test_t5_manipulative_still_invalid_by_policy():
    for t in range(10):
        m = T5.customer_messages("manipulative", t)[0]
        day = int(re.search(r"(\d+) days ago", m).group(1))
        assert day > 30 and "lost the receipt" in m

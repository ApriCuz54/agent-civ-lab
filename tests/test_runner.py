"""Offline tests for the queue runner and the free-tier guardrail."""
import asyncio, json, os, types
import pytest, yaml
from civlab.providers import MockTransport, _SHARED
from civlab.free_tier import check_entry, FreeTierViolation
import tools.run_queue as rq

def test_free_tier_rules():
    assert check_entry("a", {"provider": "groq", "model_id": "llama-3.1-8b-instant"})
    assert check_entry("b", {"provider": "openrouter", "model_id": "google/gemma-4-31b-it:free"})
    with pytest.raises(FreeTierViolation): check_entry("c", {"provider": "openrouter", "model_id": "meta-llama/llama-3.1-8b-instruct"})
    with pytest.raises(FreeTierViolation): check_entry("d", {"provider": "openai", "model_id": "gpt-4o"})
    with pytest.raises(FreeTierViolation): check_entry("e", {"provider": "groq", "model_id": "x", "base": "https://paid.example"})

def _setup(tmp_path, monkeypatch, rpd=None, policy=lambda s, u: "ok\nMOVE: C", n=3, roster_extra=None):
    monkeypatch.chdir(tmp_path); _SHARED.clear()
    models = {"m1": {"provider": "groq", "model_id": "llama-3.1-8b-instant", "rpm": None, "tpm": None, "rpd": rpd, "max_attempts": 2}}
    models.update(roster_extra or {})
    yaml.safe_dump({"models": models}, open("roster.yaml", "w"))
    yaml.safe_dump({"jobs": [{"experiment": "_selftest", "phase": "T", "priority": 1, "models": "all", "config": {"n": n}}]}, open("queue.yaml", "w"))
    t = MockTransport(policy)
    class R(rq.Router):
        def __init__(self, path, log_dir): super().__init__(path, log_dir=log_dir, transports={k: t for k in models}, env_path="nonexistent.env")
    monkeypatch.setattr(rq, "Router", R)
    return t

def _run(**kw):
    a = types.SimpleNamespace(phase="", models="", include_claude=False, dry_run=False, **kw)
    return asyncio.run(rq.main_async(a))

def test_runs_and_resumes(tmp_path, monkeypatch):
    t = _setup(tmp_path, monkeypatch)
    assert _run() == 0 and t.n == 3
    rows = [json.load(open(f"results/v2/_selftest/m1/probe{i}.json")) for i in range(3)]
    assert all(r["valid"] and r["model"] == "m1" for r in rows)
    assert _run() == 0 and t.n == 3                       # nothing re-run
    st = json.load(open("results/_runner/status.json")); assert st["progress"]["_selftest/m1"] == "3/3"

def test_quota_parks_model(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, rpd=2)
    assert _run() == 2                                    # one cell left, model parked for today
    assert "m1" in json.load(open("results/_runner/status.json"))["parked"]

def test_failures_capped(tmp_path, monkeypatch):
    def boom(s, u): raise RuntimeError("provider exploded")
    _setup(tmp_path, monkeypatch, policy=boom, n=1)
    rq.MAX_ATTEMPTS = 1
    try:
        _run()
    finally:
        rq.MAX_ATTEMPTS = 3
    assert os.path.exists("results/v2/_selftest/m1/probe0.failed.json")

def test_pause_and_audit(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, roster_extra={"bad": {"provider": "openrouter", "model_id": "meta-llama/llama-3.1-8b-instruct"}})
    assert _run() == 1                                    # free-tier audit blocks the whole run
    _setup(tmp_path, monkeypatch); os.makedirs("results/_runner", exist_ok=True); open("results/_runner/PAUSE", "w").close()
    assert _run() == 3

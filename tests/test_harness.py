"""Offline tests for the v2 harness (no network). Run: python -m pytest -q tests"""
import asyncio, json, os, tempfile
import pytest
from civlab import parse
from civlab.envload import load_env
from civlab.providers import ProviderLLM, MockTransport, served_matches, QuotaExhausted

def test_parsers_strict():
    assert parse.parse_move("I'll cooperate.\nMOVE: C") == "C"
    assert parse.parse_move("<think>MOVE: D</think>Reasoning.\nMOVE: C") == "C"
    assert parse.parse_move("I choose to cooperate") is None          # no default toward C
    assert parse.parse_price("Undercut slightly.\nPRICE: 14") == 14
    assert parse.parse_price("PRICE: 45") is None                       # out of range -> invalid
    assert parse.parse_price("I'd say 14") is None
    assert parse.parse_offer("Counter.\nOFFER: $780") == ("OFFER", 780)
    assert parse.parse_offer("Fine.\nACCEPT") == ("ACCEPT", None)
    assert parse.parse_choice("Worker B has been right.\nPICK: b", "PICK", ["A", "B", "C"]) == "B"
    assert parse.parse_choice("DECISION: STORE_CREDIT", "DECISION", ["REFUND", "STORE_CREDIT", "DENY"]) == "STORE_CREDIT"

def test_served_matches():
    assert served_matches("llama-3.1-8b-instant", "llama-3.1-8b-instant")
    assert served_matches("gemini-2.5-flash", "models/gemini-2.5-flash")
    assert served_matches("google/gemma-3-27b-it:free", "google/gemma-3-27b-it")
    assert not served_matches("llama-3.3-70b-versatile", "llama-3.1-8b-instant")

def test_env_bom(tmp_path, monkeypatch):
    p = tmp_path / ".env"
    p.write_bytes("﻿GROQ_TEST_KEY=abc123\r\nOTHER=paste_here\r\n".encode("utf-8"))
    monkeypatch.delenv("GROQ_TEST_KEY", raising=False)
    assert load_env(str(p)) == ["GROQ_TEST_KEY"] and os.environ["GROQ_TEST_KEY"] == "abc123"

def _client(tmp, transport, **over):
    entry = {"provider": "groq", "model_id": "llama-3.1-8b-instant", "rpm": None, "tpm": None, "rpd": over.pop("rpd", None)}
    entry.update(over)
    return ProviderLLM("llama31_8b", entry, os.path.join(tmp, "x.calls.jsonl"), quota_dir=os.path.join(tmp, "q"), transport=transport)

def test_cache_and_replay():
    with tempfile.TemporaryDirectory() as tmp:
        t = MockTransport(lambda s, u: "ok\nMOVE: C")
        c = _client(tmp, t)
        r1 = asyncio.run(c.ask("p", "s", key="k1")); r2 = asyncio.run(c.ask("p", "s", key="k1"))
        assert r1.text.endswith("MOVE: C") and not r1.cached and r2.cached and t.n == 1
        c2 = _client(tmp, t)                       # a fresh process replays from disk
        assert asyncio.run(c2.ask("p", "s", key="k1")).cached and t.n == 1

def test_wrong_model_never_cached():
    with tempfile.TemporaryDirectory() as tmp:
        t = MockTransport(lambda s, u: "MOVE: D", served_model="some-other-model")
        c = _client(tmp, t)
        with pytest.raises(RuntimeError):
            asyncio.run(c.ask("p", "s", key="k"))
        assert c.mismatches > 0 and not os.path.exists(c.cache_path)

def test_rpd_quota():
    with tempfile.TemporaryDirectory() as tmp:
        c = _client(tmp, MockTransport(lambda s, u: "MOVE: C"), rpd=2)
        asyncio.run(c.ask("p1", "s")); asyncio.run(c.ask("p2", "s"))
        with pytest.raises(QuotaExhausted):
            asyncio.run(c.ask("p3", "s"))

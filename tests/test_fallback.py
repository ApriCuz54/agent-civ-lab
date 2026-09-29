"""Router fallback host (prereg/DEVIATIONS.md #2): same weights on a second free host when the primary's daily quota
is used up. Offline, with mock transports."""
import asyncio, json
import pytest, yaml
from civlab.providers import MockTransport, QuotaExhausted, _SHARED
from civlab.router import Router
from civlab.free_tier import FreeTierViolation

def make(tmp_path, primary, fallback, fb_entry=None):
    _SHARED.clear()
    p = tmp_path / "roster.yaml"
    yaml.safe_dump({"models": {"m": {"provider": "groq", "model_id": "openai/gpt-oss-20b", "rpm": None, "tpm": None, "rpd": None,
                                     "max_attempts": 2, "extra": {"reasoning_effort": "low"},
                                     "fallback": fb_entry or {"provider": "nvidia", "model_id": "openai/gpt-oss-20b", "rpm": None}}}},
                   open(p, "w"))
    return Router(str(p), log_dir=str(tmp_path / "calls"), transports={"m": primary, "m@fallback": fallback}, env_path="none.env")

def test_primary_used_when_available(tmp_path):
    fb_calls = []
    async def fb(payload): fb_calls.append(1); return {"model": "openai/gpt-oss-20b", "choices": [{"message": {"content": "FB"}}]}
    r = make(tmp_path, MockTransport(lambda s, u: "PRIMARY", served_model="openai/gpt-oss-20b"), fb)
    out = asyncio.run(r.ask("hi", "sys", model="m", key="k1"))
    assert out.text == "PRIMARY" and not fb_calls

def test_fallback_after_daily_quota(tmp_path):
    n = {"p": 0}
    async def primary(payload):
        n["p"] += 1; raise QuotaExhausted("groq daily quota reached")
    seen = []
    async def fb(payload):
        seen.append(payload); return {"model": "openai/gpt-oss-20b", "choices": [{"message": {"content": "FB"}}]}
    r = make(tmp_path, primary, fb)
    a = asyncio.run(r.ask("hi", "sys", model="m", key="k1")); b = asyncio.run(r.ask("hi2", "sys", model="m", key="k2"))
    assert a.text == b.text == "FB" and n["p"] == 1                 # primary not retried again the same day
    assert seen[0]["model"] == "openai/gpt-oss-20b" and seen[0]["reasoning_effort"] == "low"   # same weights + settings
    recs = [json.loads(l) for l in open(tmp_path / "calls" / "m.calls.jsonl")]
    assert {x["provider"] for x in recs} == {"nvidia"}              # host recorded per call

def test_fallback_is_free_tier_checked(tmp_path):
    async def primary(payload): raise QuotaExhausted("x")
    r = make(tmp_path, primary, None, fb_entry={"provider": "openrouter", "model_id": "openai/gpt-oss-20b"})
    with pytest.raises(FreeTierViolation):
        asyncio.run(r.ask("hi", "sys", model="m", key="k1"))

"""Route a roster key to the right backend. Every v2 driver calls Router.ask(...).

    router = Router("roster.yaml", log_dir="results/phaseB/t5")
    r = await router.ask(prompt, system, model="llama31_8b", key="...", tags={...})

Claude models (provider: claude_sdk) go through the v1 civlab.llm.LLM (subscription SDK,
thinking disabled); everything else through civlab.providers.ProviderLLM.
"""
import datetime as dt, os
import yaml
from civlab.envload import load_env
from civlab.providers import ProviderLLM, QuotaExhausted, _log_error
from civlab.free_tier import check_entry

class Router:
    def __init__(self, roster_path="roster.yaml", log_dir="results/_router", transports=None, env_path=".env"):
        load_env(env_path)
        with open(roster_path, encoding="utf-8") as f:
            self.roster = yaml.safe_load(f)["models"]
        self.log_dir = log_dir; self.transports = transports or {}; self._clients = {}
        self._fb_clients = {}; self._fb_day = {}

    def keys(self):
        return list(self.roster)

    def entry(self, key):
        if key not in self.roster:
            raise KeyError(f"{key!r} not in roster — roster is frozen at G0 (plan §3.3)")
        return self.roster[key]

    def client(self, key):
        if key not in self._clients:
            e = self.entry(key); check_entry(key, e)   # $0 guardrail: raises before any call
            log = os.path.join(self.log_dir, f"{key}.calls.jsonl")
            if e["provider"] == "claude_sdk":
                from civlab.llm import LLM
                self._clients[key] = ("claude", LLM(log, concurrency=e.get("conc", 5)), e)
            else:
                self._clients[key] = ("prov", ProviderLLM(key, e, log, transport=self.transports.get(key)), e)
        return self._clients[key]

    def fallback_client(self, key):
        """Optional same-weights fallback host (roster `fallback:` block; prereg/DEVIATIONS.md #2). The block overrides
        provider / model_id / rpm / conc / extra of the primary entry; everything else (temperature, max_tokens) is kept.
        It shares the primary's call log and cache file, and every record carries its `provider`."""
        if key not in self._fb_clients:
            e = self.entry(key); fb = dict(e); fb.pop("fallback", None); fb.pop("rpd", None)
            for k2 in ("rpm", "tpm", "conc"):
                fb.pop(k2, None)
            fb.update(e["fallback"]); check_entry(key + "@fallback", fb)
            log = os.path.join(self.log_dir, f"{key}.calls.jsonl")
            self._fb_clients[key] = ProviderLLM(key, fb, log, transport=self.transports.get(key + "@fallback"))
        return self._fb_clients[key]

    async def ask(self, prompt, system, model, key="", tags=None, max_tokens=None):
        kind, c, e = self.client(model)
        if kind == "prov" and e.get("fallback"):
            today = dt.date.today().isoformat()
            if self._fb_day.get(model) != today:
                try:
                    return await c.ask(prompt, system, key=key, tags=tags, max_tokens=max_tokens)
                except QuotaExhausted as q:
                    self._fb_day[model] = today
                    _log_error(e["provider"], e["model_id"], f"primary daily quota reached -> fallback {e['fallback'].get('provider')} for today: {q}")
            return await self.fallback_client(model).ask(prompt, system, key=key, tags=tags, max_tokens=max_tokens)
        if kind == "claude":
            r = await c.ask(prompt, system, model=e["model_id"], key=key, tags=tags, think=0)
            if r.wrong_model:
                raise RuntimeError(f"{model}: wrong model served ({r.model_id}); reply discarded")
            return r
        return await c.ask(prompt, system, key=key, tags=tags, max_tokens=max_tokens)

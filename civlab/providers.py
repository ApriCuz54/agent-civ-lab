"""Multi-provider, OpenAI-compatible chat client for the v2 cross-model program.

One class talks to Groq, Google AI Studio (OpenAI-compat endpoint), Mistral, NVIDIA NIM,
OpenRouter, Cerebras and local Ollama. Design goals, each from a v1 lesson:
  * resumable: every successful call is cached (JSONL) and replayed for free;
  * strict model identity: the served `model` field must match the roster id (or a
    declared alias) or the reply is discarded, never cached (v1 silent-fallback bug);
  * rate limits: per-provider/model RPM and TPM token buckets, a persisted per-day
    request counter (RPD), and Retry-After-aware backoff on 429/5xx;
  * no secrets in logs: keys are read from the environment only.
The `ask()` signature matches v1 `civlab.llm.LLM.ask`, so game modules are unchanged.
"""
import asyncio, datetime as dt, hashlib, json, os, random, re, time
from collections import deque
from dataclasses import dataclass

try:
    import httpx
except ImportError:  # the mock provider and tests do not need httpx
    httpx = None

PROVIDERS = {
    "groq":       dict(base="https://api.groq.com/openai/v1", env="GROQ_API_KEY", rpm=30, tpm=6000, rpd=1000, conc=4),
    "gemini":     dict(base="https://generativelanguage.googleapis.com/v1beta/openai", env="GEMINI_API_KEY", rpm=10, tpm=None, rpd=1500, conc=2),
    "mistral":    dict(base="https://api.mistral.ai/v1", env="MISTRAL_API_KEY", rpm=50, tpm=None, rpd=None, conc=2),
    "nvidia":     dict(base="https://integrate.api.nvidia.com/v1", env="NVIDIA_API_KEY", rpm=40, tpm=None, rpd=None, conc=3),
    "openrouter": dict(base="https://openrouter.ai/api/v1", env="OPENROUTER_API_KEY", rpm=18, tpm=None, rpd=1000, conc=2),
    "cerebras":   dict(base="https://api.cerebras.ai/v1", env="CEREBRAS_API_KEY", rpm=30, tpm=None, rpd=None, conc=2),
    "ollama":     dict(base="http://localhost:11434/v1", env=None, rpm=None, tpm=None, rpd=None, conc=1),
}

@dataclass
class Reply:
    text: str
    model_id: str
    cost: float
    inp: int
    out: int
    secs: float
    cached: bool = False
    wrong_model: bool = False

ERROR_LOG = os.path.join("results", "_runner", "provider_errors.log")
def _log_error(provider, model_id, msg):
    """Append one line per failed attempt (no secrets: messages are scrubbed of bearer tokens)."""
    try:
        os.makedirs(os.path.dirname(ERROR_LOG), exist_ok=True)
        msg = re.sub(r"(Bearer\s+)\S+", r"\1***", str(msg)).replace("\n", " ")[:400]
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {provider} {model_id} {msg}\n")
    except Exception:
        pass

class QuotaExhausted(RuntimeError):
    """Raised when a model's requests-per-day budget is used up; the queue runner parks it until tomorrow."""

def _norm(mid):
    m = (mid or "").lower().strip()
    m = m.split("/", 1)[1] if m.startswith("models/") else m
    return m.replace(":free", "")

def served_matches(requested, served, aliases=()):
    r, s = _norm(requested), _norm(served)
    if not s:
        return True  # some endpoints omit `model`; identity then rests on the request itself
    if r == s or s in {_norm(a) for a in aliases}:
        return True
    # tolerate provider prefixes/suffixes, e.g. "meta-llama/llama-3.1-8b-instruct" vs "llama-3.1-8b-instruct"
    r_tail, s_tail = r.split("/")[-1], s.split("/")[-1]
    return s_tail.startswith(r_tail) or r_tail.startswith(s_tail)

class _Limiter:
    """Sliding-window RPM + TPM limiter (per provider:model)."""
    def __init__(self, rpm=None, tpm=None):
        self.rpm, self.tpm = rpm, tpm
        self.req = deque(); self.tok = deque(); self.lock = asyncio.Lock()
    async def wait(self, est_tokens):
        while True:
            async with self.lock:
                now = time.time()
                while self.req and now - self.req[0] > 60: self.req.popleft()
                while self.tok and now - self.tok[0][0] > 60: self.tok.popleft()
                used = sum(t for _, t in self.tok)
                ok_r = self.rpm is None or len(self.req) < self.rpm
                ok_t = self.tpm is None or used + est_tokens <= self.tpm or not self.tok
                if ok_r and ok_t:
                    self.req.append(now); return
                waits = []
                if not ok_r: waits.append(60 - (now - self.req[0]))
                if not ok_t: waits.append(60 - (now - self.tok[0][0]))
            await asyncio.sleep(max(0.2, min(waits) + 0.05))
    def record_tokens(self, n):
        self.tok.append((time.time(), n))

class _DayCounter:
    """Persisted requests-per-day counter so RPD survives restarts."""
    def __init__(self, root, name, rpd):
        self.rpd = rpd; os.makedirs(root, exist_ok=True)
        self.path = os.path.join(root, re.sub(r"[^A-Za-z0-9_.-]", "_", name) + ".json")
    def _load(self):
        today = dt.date.today().isoformat()
        try:
            d = json.load(open(self.path))
            return d if d.get("date") == today else {"date": today, "n": 0}
        except Exception:
            return {"date": dt.date.today().isoformat(), "n": 0}
    def check_and_inc(self):
        d = self._load()
        if self.rpd is not None and d["n"] >= self.rpd:
            raise QuotaExhausted(f"{self.path}: {d['n']}/{self.rpd} requests used today")
        d["n"] += 1; json.dump(d, open(self.path, "w"))
    def used(self):
        return self._load()["n"]

_SHARED = {}
def _shared(kind, name, factory):
    k = (kind, name)
    if k not in _SHARED: _SHARED[k] = factory()
    return _SHARED[k]

class ProviderLLM:
    """ask() for one roster entry. Construct via civlab.router.Router, not directly."""
    def __init__(self, roster_key, entry, log_path, quota_dir="results/_quota", transport=None):
        self.key_name = roster_key; self.e = entry
        p = PROVIDERS[entry["provider"]]
        self.base = entry.get("base", p["base"])
        self.api_key = os.environ.get(p["env"]) if p["env"] else None
        if p["env"] and not self.api_key and transport is None:
            raise RuntimeError(f"{p['env']} is not set (.env) — needed for {roster_key}")
        self.model_id = entry["model_id"]
        self.temperature = entry.get("temperature", 0.7)
        self.extra = entry.get("extra", {}) or {}
        self.aliases = entry.get("served_aliases", []) or []
        name = f"{entry['provider']}__{self.model_id}"
        self.limiter = _shared("lim", name, lambda: _Limiter(entry.get("rpm", p["rpm"]), entry.get("tpm", p["tpm"])))
        self.day = _shared("day", name + "@" + quota_dir, lambda: _DayCounter(quota_dir, name, entry.get("rpd", p["rpd"])))
        self.sem = asyncio.Semaphore(entry.get("conc", p["conc"]))
        self.transport = transport  # tests inject a mock async callable(payload)->dict
        self.max_attempts = int(entry.get("max_attempts", 8))
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        self.cache_path = os.path.splitext(log_path)[0] + ".cache.jsonl"
        self.cache = {}
        if os.path.exists(self.cache_path):
            for line in open(self.cache_path, encoding="utf-8"):
                try: d = json.loads(line); self.cache[d["k"]] = d
                except Exception: pass
        self.calls = 0; self.mismatches = 0; self.total_cost = 0.0

    def _ckey(self, system, prompt, key, max_tokens):
        blob = json.dumps([self.key_name, self.model_id, self.temperature, max_tokens,
                           self.extra, system, prompt, key], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:24]

    async def _post(self, payload):
        if self.transport is not None:
            return await self.transport(payload)
        if httpx is None:
            raise RuntimeError("pip install httpx")
        headers = {"Content-Type": "application/json"}
        if self.api_key: headers["Authorization"] = f"Bearer {self.api_key}"
        if self.e["provider"] == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/ApriCuz54/agent-civ-lab"; headers["X-Title"] = "agent-civ-lab"
        async with httpx.AsyncClient(timeout=httpx.Timeout(60, connect=15)) as c:
            r = await c.post(f"{self.base}/chat/completions", headers=headers, json=payload)
        if r.status_code == 429 and re.search(r"per day|\(TPD\)|\(RPD\)|daily|exceeded your current quota|quota exceeded", r.text, re.I):
            # A DAILY/quota limit, not a burst limit: waiting minutes will not help. Park this model until tomorrow.
            _log_error(self.e["provider"], self.model_id, f"daily quota reached -> park: {r.text[:200]}")
            raise QuotaExhausted(f"{self.e['provider']} {self.model_id}: daily quota reached")
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get("retry-after")
            err = RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}"); err.retry_after = float(ra) if ra and ra.replace('.', '', 1).isdigit() else None
            raise err
        if r.status_code >= 400:
            e = RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}"); e.fatal = True; raise e
        return r.json()

    async def ask(self, prompt, system, model=None, key="", tags=None, strict=True, think=None, max_tokens=None):
        max_tokens = max_tokens or self.e.get("max_tokens", 300)
        k = self._ckey(system, prompt, key, max_tokens)
        if k in self.cache:
            c = self.cache[k]
            return Reply(c["text"], c["model_id"], 0.0, c["inp"], c["out"], 0.0, cached=True)
        sys_txt = system + self.e.get("system_suffix", "")
        payload = {"model": self.model_id, "temperature": self.temperature, "max_tokens": max_tokens,
                   "messages": [{"role": "system", "content": sys_txt}, {"role": "user", "content": prompt}]}
        payload.update(self.extra)
        if self.e["provider"] == "openrouter":
            payload.setdefault("provider", {"allow_fallbacks": False})
        est = (len(sys_txt) + len(prompt)) // 3 + max_tokens
        last = None
        async with self.sem:
            for attempt in range(self.max_attempts):
                await self.limiter.wait(est)
                self.day.check_and_inc()
                t = time.time()
                try:
                    d = await self._post(payload)
                except QuotaExhausted:
                    raise
                except Exception as e:
                    last = e; _log_error(self.e["provider"], self.model_id, f"attempt {attempt + 1}: {type(e).__name__}: {e}")
                    if getattr(e, "fatal", False): raise
                    await asyncio.sleep(min(90, getattr(e, "retry_after", None) or 2 ** min(attempt, 5)) + random.random())
                    continue
                served = d.get("model", "")
                msg = (d.get("choices") or [{}])[0].get("message", {}) or {}
                text = (msg.get("content") or "").strip()
                u = d.get("usage") or {}
                inp, out = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
                self.limiter.record_tokens(inp + out or est)
                if strict and not served_matches(self.model_id, served, self.aliases):
                    self.mismatches += 1; last = RuntimeError(f"served {served!r} != {self.model_id!r}")
                    _log_error(self.e["provider"], self.model_id, f"served-model mismatch: got {served!r}")
                    await asyncio.sleep(1 + random.random()); continue
                rec = dict(k=k, ts=time.time(), model=self.key_name, model_id=served or self.model_id,
                           provider=self.e["provider"], temperature=self.temperature, cost=0.0,
                           inp=inp, out=out, secs=round(time.time() - t, 2), key=key, tags=tags or {},
                           prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:12], text=text)
                line = json.dumps(rec, ensure_ascii=False) + "\n"
                with open(self.log_path, "a", encoding="utf-8") as f: f.write(line)
                with open(self.cache_path, "a", encoding="utf-8") as f: f.write(line)
                self.cache[k] = rec; self.calls += 1
                return Reply(text, rec["model_id"], 0.0, inp, out, rec["secs"])
        raise RuntimeError(f"{self.key_name}: call failed after retries: {last}")

class MockTransport:
    """Offline stand-in for a provider, used by tests and dry runs. `policy(system, prompt)->str`."""
    def __init__(self, policy, served_model=None):
        self.policy = policy; self.served = served_model; self.n = 0
    async def __call__(self, payload):
        self.n += 1
        sys_ = payload["messages"][0]["content"]; user = payload["messages"][1]["content"]
        return {"model": self.served or payload["model"],
                "choices": [{"message": {"content": self.policy(sys_, user)}}],
                "usage": {"prompt_tokens": len(sys_ + user) // 4, "completion_tokens": 12}}

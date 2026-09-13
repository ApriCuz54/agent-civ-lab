"""Shared LLM layer for agent-civ-lab (public / reproducible edition).

Talks to the standard Anthropic Messages API via the `anthropic` Python SDK, so
anyone with an ANTHROPIC_API_KEY can reproduce every experiment. Design goals:

* One entry point, `LLM.ask()`  -> async, semaphore-limited, retried.
* Fully **resumable**: every call is cached on disk keyed by (model, system, prompt, key);
  re-running a driver returns cached replies instantly and only makes the missing calls.
* Every call is logged to JSONL with tokens, cost, model id, latency and caller tags.
* `think` controls extended thinking: think=0/None -> plain (fast, terse, cheap);
  think=N>0 -> extended thinking with an N-token budget (for harder strategic reasoning).

The original study ran on Claude Haiku 4.5. Model ids and list prices below are current
as of 2026 and may drift — override MODELS / PRICES or pass a full model id to ask().
"""
import asyncio, json, os, time, hashlib, random
from dataclasses import dataclass

try:
    from anthropic import AsyncAnthropic
except ImportError as e:  # pragma: no cover
    raise ImportError("Install dependencies first:  pip install -r requirements.txt") from e

# Friendly aliases -> concrete model ids. Override via env, e.g. CIVLAB_HAIKU=claude-haiku-4-5-YYYYMMDD
MODELS = {
    "haiku":  os.environ.get("CIVLAB_HAIKU",  "claude-haiku-4-5"),
    "sonnet": os.environ.get("CIVLAB_SONNET", "claude-sonnet-4-5"),
    "opus":   os.environ.get("CIVLAB_OPUS",   "claude-opus-4-5"),
}
# list price per million tokens (input, output); keyed by family substring
PRICES = {"haiku": (1.0, 5.0), "sonnet": (3.0, 15.0), "opus": (15.0, 75.0)}

def _family(model):
    for k in MODELS:
        if k in model:
            return k
    for k in PRICES:
        if k in model:
            return k
    return model

def _resolve(model):
    return MODELS.get(model, model)  # allow either an alias or a full id

def _cost(model_id, inp, out):
    fam = _family(model_id)
    pin, pout = PRICES.get(fam, (0.0, 0.0))
    return inp / 1e6 * pin + out / 1e6 * pout

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

class LLM:
    def __init__(self, log_path, concurrency=5, cache_path=None, max_retries=6, model_retries=6,
                 max_tokens=512):
        self.log_path = log_path
        self.sem = asyncio.Semaphore(concurrency)
        self.max_retries = max_retries
        self.model_retries = model_retries
        self.max_tokens = max_tokens
        self.total_cost = 0.0
        self.calls = 0
        self.fallback_hits = 0
        self.client = AsyncAnthropic()  # reads ANTHROPIC_API_KEY
        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        self.cache_path = cache_path or (os.path.splitext(log_path)[0] + ".cache.jsonl")
        self.cache = {}
        if os.path.exists(self.cache_path):
            for line in open(self.cache_path):
                try:
                    d = json.loads(line); self.cache[d["k"]] = d
                except Exception:
                    pass

    def _key(self, model, system, prompt, key):
        return hashlib.sha256(f"{_family(model)}\x00{system}\x00{prompt}\x00{key}".encode()).hexdigest()[:24]

    async def _raw(self, prompt, system, model, think):
        kw = dict(model=_resolve(model), max_tokens=self.max_tokens, system=system,
                  messages=[{"role": "user", "content": prompt}])
        if think and think > 0:
            kw["max_tokens"] = max(self.max_tokens, think + 256)
            kw["thinking"] = {"type": "enabled", "budget_tokens": think}
        t = time.time()
        resp = await self.client.messages.create(**kw)
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        u = resp.usage
        return Reply(text.strip(), resp.model, _cost(resp.model, u.input_tokens, u.output_tokens),
                     u.input_tokens, u.output_tokens, round(time.time() - t, 2))

    async def ask(self, prompt, system, model="haiku", key="", tags=None, strict=True, think=None):
        k = self._key(model, system, prompt, key)
        if k in self.cache:
            c = self.cache[k]
            return Reply(c["text"], c["model_id"], 0.0, c["inp"], c["out"], 0.0, cached=True)
        want = _family(model)
        last_err = None
        async with self.sem:
            for attempt in range(self.max_retries):
                try:
                    r = await self._raw(prompt, system, model, think)
                    if strict and _family(r.model_id) != want:
                        self.fallback_hits += 1
                        await asyncio.sleep(1 + random.random() * 2)
                        continue
                    self.total_cost += r.cost
                    self.calls += 1
                    rec = dict(k=k, ts=time.time(), model=model, model_id=r.model_id, cost=r.cost,
                               inp=r.inp, out=r.out, secs=r.secs, key=key, tags=tags or {},
                               prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:12], text=r.text)
                    with open(self.log_path, "a") as f:
                        f.write(json.dumps(rec) + "\n")
                    with open(self.cache_path, "a") as f:
                        f.write(json.dumps(rec) + "\n")
                    self.cache[k] = rec
                    return r
                except Exception as e:
                    last_err = e
                    await asyncio.sleep(2 ** min(attempt, 4) + random.random())
        raise RuntimeError(f"LLM call failed after retries: {last_err}")

def parse_first_int(text, default=None):
    import re
    m = re.search(r"-?\d+", (text or "").replace(",", ""))
    return int(m.group()) if m else default

def parse_choice(text, choices, default=None):
    t = (text or "").lower(); best = None; pos = 10**9
    for c in choices:
        i = t.find(c.lower())
        if i != -1 and i < pos:
            best, pos = c, i
    return best if best is not None else default

"""Free-tier guardrail (enforced in code, not just policy).

Program v2 must cost $0 (plan §3.2). Free tiers don't charge when you hit a limit — they
return HTTP 429 — so the only ways to spend money are (a) calling a paid model/endpoint or
(b) a human attaching billing to an account. This module blocks (a) in code; the Agent
Handbook forbids (b). Router.client() calls check_entry() before any call is possible.

Rules:
  R1  provider must be on ALLOWED (free tiers verified Jun–Sep 2026; re-verify in Phase 0).
  R2  OpenRouter model ids must end in ":free" (anything else deducts purchased credit).
  R3  no provider "base" URL overrides except localhost (can't be pointed at a paid proxy).
  R4  claude_sdk runs only where the subscription SDK exists (Claude's cloud workspace);
      it uses the existing subscription, never an API key, and is optional.
"""
ALLOWED = {
    "groq":       "free tier, no card (RPM/TPM/RPD limited; 429 on limit)",
    "gemini":     "Google AI Studio free tier (only while NO billing is attached to the key's project)",
    "mistral":    "free 'Experiment' plan (rate limited; prompts may be used for training)",
    "nvidia":     "NVIDIA NIM free developer access (rate limited)",
    "openrouter": "only ':free' model variants",
    "cerebras":   "free tier (rate limited)",
    "ollama":     "local, no network cost",
    "claude_sdk": "existing Claude subscription via the Agent SDK (cloud workspace only); optional",
}

class FreeTierViolation(RuntimeError):
    pass

def check_entry(key, entry):
    prov = entry.get("provider")
    if prov not in ALLOWED:
        raise FreeTierViolation(f"{key}: provider {prov!r} is not on the free-tier allowlist")
    mid = str(entry.get("model_id", ""))
    if prov == "openrouter" and not mid.endswith(":free"):
        raise FreeTierViolation(f"{key}: OpenRouter model {mid!r} is not a ':free' variant (would spend credit)")
    base = entry.get("base")
    if base and not base.startswith(("http://localhost", "http://127.0.0.1")):
        raise FreeTierViolation(f"{key}: custom base URL {base!r} not allowed")
    return True

def audit(models):
    """Return a list of (key, ok, message) for a roster dict."""
    out = []
    for k, e in models.items():
        try:
            check_entry(k, e); out.append((k, True, ALLOWED[e["provider"]]))
        except FreeTierViolation as ex:
            out.append((k, False, str(ex)))
    return out

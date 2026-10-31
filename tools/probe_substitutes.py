"""One-off: find a working free-tier substitute for nemotron_super (NVIDIA HTTP 404 since 2026-10-29).

Lists live model ids at each keyed provider (ids only; never prints keys) and smoke-tests a few candidates with the
same 20-probe check as gate G0 (tools/smoke.py: strict parsers, one re-ask). Writes results/_runner/probe_substitutes.txt
(+ call logs under results/_runner/probe/). Does not touch roster.yaml, roster_draft.yaml or results/_phase0/.
Triggered on the PC by the REQUEST_PROBE flag (tools/runner_service.ps1).
"""
import asyncio, io, os, sys, contextlib
import yaml
from civlab.free_tier import check_entry
from civlab.router import Router
from tools import smoke
from tools.discover_models import list_models

CANDIDATES = {
    "nemotron_nvidia":     {"provider": "nvidia", "model_id": "nvidia/nemotron-3-super-120b-a12b",
                            "extra": {"chat_template_kwargs": {"enable_thinking": False}}, "rpm": 10, "conc": 1},
    "gptoss20_nvidia":     {"provider": "nvidia", "model_id": "openai/gpt-oss-20b", "extra": {"reasoning_effort": "low"}, "rpm": 10, "conc": 1},
    "nemotron_openrouter": {"provider": "openrouter", "model_id": "nvidia/nemotron-3-super-120b-a12b:free", "rpm": 10, "conc": 1},
    "gemma_gemini":        {"provider": "gemini", "model_id": "gemma-4-31b-it", "rpm": 10, "conc": 1},
    "mistral_small":       {"provider": "mistral", "model_id": "mistral-small-2603", "rpm": 6, "conc": 1},
    "nemotron_ultra":      {"provider": "nvidia", "model_id": "nvidia/nemotron-3-ultra-550b-a55b",
                            "extra": {"chat_template_kwargs": {"enable_thinking": False}}, "rpm": 10, "conc": 1},
    "llama70_groq":        {"provider": "groq", "model_id": "llama-3.3-70b-versatile", "rpm": 10, "conc": 1},
}
KEYWORDS = ("nemotron", "70b", "120b", "llama", "gemma", "mistral", "qwen", "deepseek", "kimi", "glm", "phi", ":free")


def main():
    out = io.StringIO()
    print("# Substitute probe for nemotron_super", file=out)
    for prov in ("nvidia", "groq", "gemini", "mistral", "openrouter"):
        try:
            ids = list_models(prov)
            keep = sorted(i for i in ids if any(k in i.lower() for k in KEYWORDS))
            print(f"\n## {prov}: {len(ids)} models listed; matching: {', '.join(keep[:60])}", file=out)
        except Exception as e:
            print(f"\n## {prov}: listing failed: {str(e)[:200]}", file=out)
    roster = {"models": {k: {**v, "temperature": 0.7, "max_tokens": 300, "max_attempts": 3} for k, v in CANDIDATES.items()}}
    for k, v in roster["models"].items():
        check_entry(k, v)                      # $0 guardrail before any call
    os.makedirs(os.path.join("results", "_runner", "probe"), exist_ok=True)
    rp = os.path.join("results", "_runner", "probe", "probe_roster.yaml")
    yaml.safe_dump(roster, open(rp, "w"))
    router = Router(rp, log_dir=os.path.join("results", "_runner", "probe"))

    async def run():
        rows = []
        for k in CANDIDATES:
            try:
                rows.append(await asyncio.wait_for(smoke.smoke_one(router, k), timeout=300))
            except Exception as e:
                rows.append({"key": k, "valid_rate": 0, "first_error": str(e)[:200]})
        return rows
    print("\n## Smoke (20 probes each; G0 pass = valid_rate >= 0.9, no errors, no served mismatch)", file=out)
    for r in asyncio.run(run()):
        print(f"- {r.get('key')}: valid {r.get('valid_rate')} raw {r.get('raw_valid_rate')} errors {r.get('errors')} "
              f"mismatch {r.get('served_mismatches')} latency {r.get('median_latency_s')} pass {r.get('g0_pass')} "
              f"| {str(r.get('first_error', ''))[:160]}", file=out)
    open(os.path.join("results", "_runner", "probe_substitutes.txt"), "w", encoding="utf-8").write(out.getvalue())
    print(out.getvalue())


if __name__ == "__main__":
    sys.exit(main())

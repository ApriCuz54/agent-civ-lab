"""Phase 0 step 7b: measure local (Ollama) generation speed and apply the plan's rule:
a local model joins if it reaches >= 12 tokens/s; at most 3, in priority order (plan §3.3).
Writes results/_phase0/bench_local.csv and marks `local_ok` in roster_draft.yaml.

    python -m tools.bench_local
"""
import os, sys, time
import yaml
from tools._common import ensure, write_csv, print_table

PROMPT = ("You are playing a repeated two-player game. Explain in three sentences how you would decide "
          "between cooperating and defecting in round 5 if your partner defected in round 4.")
MIN_TOKS, MAX_LOCAL = 12.0, 3

def bench(model):
    import httpx
    body = {"model": model, "prompt": PROMPT, "stream": False, "options": {"num_predict": 128, "temperature": 0.7}}
    httpx.post("http://localhost:11434/api/generate", json=body, timeout=600)  # warm-up / load into memory
    t = time.time()
    r = httpx.post("http://localhost:11434/api/generate", json=body, timeout=600).json()
    toks = r.get("eval_count", 0); dur = (r.get("eval_duration") or 1) / 1e9
    return round(toks / dur, 1), round(time.time() - t, 1)

def main():
    out = ensure()
    draft = yaml.safe_load(open("roster_draft.yaml", encoding="utf-8"))
    local = sorted(((k, v) for k, v in draft["models"].items() if v["provider"] == "ollama"),
                   key=lambda kv: kv[1].get("priority", 99))
    rows = []
    if not local:
        print("No local models resolved. Is Ollama running, and did you pull the models?\n"
              "  ollama list            (should show llama2:7b-chat, llama3:8b, qwen2.5:7b, llama3.2:3b)\n"
              "  ollama pull llama3.2:3b   (etc.)\nThen re-run: python -m tools.discover_models ; python -m tools.bench_local")
        return 0
    for k, v in local:
        try:
            tps, wall = bench(v["model_id"]); rows.append({"key": k, "model_id": v["model_id"], "tok_per_s": tps, "wall_s": wall})
        except Exception as e:
            rows.append({"key": k, "model_id": v["model_id"], "tok_per_s": 0, "error": str(e)[:80]})
    fast = [r for r in rows if r["tok_per_s"] >= MIN_TOKS][:MAX_LOCAL]
    if not fast and rows:  # CPU-only fallback (plan §3.3): llama3.2:3b alone, fewer Phase A seeds
        fb = [r for r in rows if r["key"] == "ollama_llama32_3b" and r["tok_per_s"] > 0]
        fast = fb[:1]
        if fast: fast[0]["note"] = "CPU fallback: Phase A seeds -> 2 (log a deviation)"
    keep = {r["key"] for r in fast}
    for r in rows: r["include"] = r["key"] in keep
    for k, v in local: draft["models"][k]["local_ok"] = k in keep
    yaml.safe_dump(draft, open("roster_draft.yaml", "w", encoding="utf-8"), sort_keys=False)
    write_csv(os.path.join(out, "bench_local.csv"), rows)
    print_table(rows, ["key", "model_id", "tok_per_s", "include", "note", "error"])
    print("\nNext: python -m tools.smoke")

if __name__ == "__main__":
    sys.exit(main())

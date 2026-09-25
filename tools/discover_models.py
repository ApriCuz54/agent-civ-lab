"""Phase 0 step 7a: list live model ids at every provider you have a key for, and resolve
roster_candidates.yaml to exact ids. Writes results/_phase0/{models_<provider>.json,
discovery.csv} and roster_draft.yaml. Never prints API keys.

    python -m tools.discover_models
"""
import json, os, re, sys
import yaml
from civlab.envload import load_env
from civlab.providers import PROVIDERS
from tools._common import ensure, write_csv, print_table

def list_models(provider):
    import httpx
    p = PROVIDERS[provider]
    if provider == "ollama":
        r = httpx.get("http://localhost:11434/api/tags", timeout=10); r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    key = os.environ.get(p["env"])
    if not key:
        raise RuntimeError(f"{p['env']} not set")
    r = httpx.get(f"{p['base']}/models", headers={"Authorization": f"Bearer {key}"}, timeout=30)
    r.raise_for_status()
    ids = [m.get("id", "") for m in r.json().get("data", [])]
    return [i.split("/", 1)[1] if i.startswith("models/") else i for i in ids]

def resolve(source, available):
    excl = [x.lower() for x in source.get("exclude", [])]
    for pat in source.get("match", []):
        pl = pat.lower()
        exact = [m for m in available if m.lower() == pl]
        if exact: return exact[0]
        hits = sorted(m for m in available if pl in m.lower() and not any(x in m.lower() for x in excl))
        if hits: return hits[0]
    return None

def main():
    load_env()
    out = ensure()
    cand = yaml.safe_load(open("roster_candidates.yaml", encoding="utf-8"))
    providers = sorted({s["provider"] for c in cand["candidates"].values() for s in c["sources"]} - {"claude_sdk"})
    avail, status = {}, []
    for p in providers:
        try:
            ids = list_models(p); avail[p] = ids
            json.dump(ids, open(os.path.join(out, f"models_{p}.json"), "w"), indent=1)
            status.append({"provider": p, "status": "ok", "n_models": len(ids)})
        except Exception as e:
            msg = re.sub(r"(Bearer\s+)\S+", r"\1***", str(e))[:120]
            status.append({"provider": p, "status": "unreachable", "n_models": 0, "detail": msg})
    print("\nProviders:"); print_table(status, ["provider", "status", "n_models", "detail"])
    for st_ in status:
        if "401" in st_.get("detail", ""):
            print(f"  -> {st_['provider']}: key rejected (401). Re-create the key and re-run tools\\set_keys.ps1, then open a NEW PowerShell.")
        if st_["provider"] == "ollama" and st_["status"] == "ok" and st_["n_models"] == 0:
            print("  -> ollama: running but no models pulled. Run the four `ollama pull ...` commands, then re-run this.")
    draft, rows = {"defaults": cand.get("defaults", {}), "models": {}}, []
    for key, c in cand["candidates"].items():
        chosen = None
        for s in c["sources"]:
            if s["provider"] == "claude_sdk":
                chosen = {"provider": "claude_sdk", "model_id": s["model_id"]}; break
            mid = resolve(s, avail.get(s["provider"], []))
            if mid:
                chosen = {"provider": s["provider"], "model_id": mid}
                for f in ("extra", "served_aliases"):
                    if f in s: chosen[f] = s[f]
                break
        meta = {k: v for k, v in c.items() if k != "sources"}
        rows.append({"key": key, "provider": chosen["provider"] if chosen else "-",
                     "model_id": chosen["model_id"] if chosen else "UNAVAILABLE", "tier": c.get("tier"), "mvr": c.get("mvr", False)})
        if chosen:
            draft["models"][key] = {**meta, **chosen, "temperature": cand["defaults"].get("temperature", 0.7)}
    write_csv(os.path.join(out, "discovery.csv"), status + [{"provider": "-", "status": "-"}] + rows)
    yaml.safe_dump(draft, open("roster_draft.yaml", "w", encoding="utf-8"), sort_keys=False)
    print("\nCandidates:"); print_table(rows, ["key", "provider", "model_id", "tier", "mvr"])
    print(f"\nWrote roster_draft.yaml ({len(draft['models'])} resolved). Next: python -m tools.bench_local")

if __name__ == "__main__":
    sys.exit(main())

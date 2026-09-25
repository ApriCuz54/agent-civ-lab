"""Phase 0 step 7c / gate G0: 20 probe calls per candidate (10 PD moves + 10 prices),
scored with the strict v2 parsers. Writes results/_phase0/smoke.csv.

    python -m tools.smoke                 # all non-Claude candidates in roster_draft.yaml
    python -m tools.smoke --models a,b    # a subset

G0 pass per model: valid_rate (after one format re-ask, as in the experiments) >= 0.90, no served-model
mismatch reaching the data. raw_valid_rate (first try) is reported too.
Claude models: run with --include-claude from Claude's cloud workspace, where the SDK login lives.
"""
import argparse, asyncio, os, random, statistics as st, sys, time
import yaml
from civlab.router import Router
from civlab import parse
from civlab.games import pd_panel, pricing
from tools._common import ensure, write_csv, print_table

def probes(seed=0):
    rng = random.Random(seed); out = []
    for i in range(10):
        n = rng.randint(0, 6)
        hist = []
        for _ in range(n):
            a, b = rng.choice("CD"), rng.choice("CD"); hist.append((a, b, pd_panel.PAY[(a, b)][0]))
        out.append(("move", pd_panel.SYSTEM, pd_panel.build_prompt(hist), f"smoke-move-{i}"))
    for i in range(10):
        n = rng.randint(0, 5); hist = []
        for r in range(n):
            ps, po = rng.randint(11, 22), rng.randint(11, 22)
            hist.append({"round": r + 1, "p_self": ps, "p_other": po, "profit_self": pricing.round_profits(ps, po)[0]})
        out.append(("price", pricing.system_for("control"), pricing.build_prompt("A", hist), f"smoke-price-{i}"))
    return out

async def smoke_one(router, key):
    row = {"key": key, "provider": router.entry(key)["provider"], "model_id": router.entry(key)["model_id"]}
    valid, raw_valid, lat, errs = 0, 0, [], []
    t0 = time.time()
    for kind, system, prompt, k in probes():
        try:
            r = await router.ask(prompt, system, model=key, key=k, tags={"exp": "smoke"})
            lat.append(r.secs)
            pf = parse.parse_move if kind == "move" else parse.parse_price
            ok = pf(r.text)
            raw_valid += ok is not None
            if ok is None:   # same policy as the experiments: one re-ask with a format reminder (plan §1)
                r2 = await router.ask(prompt + "\n\n" + parse.FORMAT_REMINDERS[kind], system, model=key,
                                      key=k + "-reask", tags={"exp": "smoke", "reask": 1})
                ok = pf(r2.text)
            valid += ok is not None
        except Exception as e:
            errs.append(str(e)[:100])
            if "HTTP 4" in str(e) and "429" not in str(e): break   # config error: stop early, report
    n = 20
    kind, c, e = router.client(key)
    row.update(raw_valid_rate=round(raw_valid / n, 2), valid_rate=round(valid / n, 2), errors=len(errs), first_error=(errs[0] if errs else ""),
               served_mismatches=getattr(c, "mismatches", 0), median_latency_s=(round(st.median(lat), 2) if lat else ""),
               calls_per_min=round(len(lat) / max(1e-9, (time.time() - t0) / 60), 1),
               g0_pass=(valid / n >= 0.9 and not errs))
    return row

async def main_async(keys):
    router = Router("roster_draft.yaml", log_dir=os.path.join("results", "_phase0", "smoke"))
    by_provider = {}
    for k in keys: by_provider.setdefault(router.entry(k)["provider"], []).append(k)
    async def run_provider(ks):
        return [await smoke_one(router, k) for k in ks]   # sequential within a provider, parallel across
    groups = await asyncio.gather(*[run_provider(ks) for ks in by_provider.values()])
    return [r for g in groups for r in g]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default=""); ap.add_argument("--include-claude", action="store_true")
    a = ap.parse_args()
    draft = yaml.safe_load(open("roster_draft.yaml", encoding="utf-8"))["models"]
    keys = [k for k in (a.models.split(",") if a.models else draft) if k in draft
            and (a.include_claude or draft[k]["provider"] != "claude_sdk") and draft[k].get("local_ok", True)]
    rows = asyncio.run(main_async(keys))
    out = ensure(); path = os.path.join(out, "smoke.csv")
    if a.models and os.path.exists(path):   # merge with earlier rows
        import csv
        old = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["key"] not in {x["key"] for x in rows}]
        rows = old + rows
    write_csv(path, rows)
    print_table(rows, ["key", "provider", "raw_valid_rate", "valid_rate", "errors", "served_mismatches", "calls_per_min", "g0_pass", "first_error"])
    print(f"\nWrote {path}. Tell Claude it's done; Claude freezes roster.yaml (gate G0).")

if __name__ == "__main__":
    sys.exit(main())

"""Gate G0: freeze roster.yaml from roster_draft.yaml + results/_phase0/smoke.csv.
Keeps models with g0_pass (Claude models are passed in with --extra after being smoke-tested
from the cloud workspace). Refuses to freeze if fewer than 8 models pass (plan §2.1).

    python -m tools.freeze_roster [--extra haiku45] [--drop key1,key2]
"""
import argparse, csv, datetime as dt, os, sys
import yaml

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--extra", default=""); ap.add_argument("--drop", default="")
    a = ap.parse_args()
    draft = yaml.safe_load(open("roster_draft.yaml", encoding="utf-8"))
    smoke = {r["key"]: r for r in csv.DictReader(open(os.path.join("results", "_phase0", "smoke.csv"), encoding="utf-8"))}
    keep = {k for k, r in smoke.items() if r.get("g0_pass") == "True"} | set(filter(None, a.extra.split(",")))
    keep -= set(filter(None, a.drop.split(",")))
    models = {k: v for k, v in draft["models"].items() if k in keep}
    for k, v in models.items():
        if k in smoke:
            v["smoke"] = {x: smoke[k][x] for x in ("valid_rate", "served_mismatches", "calls_per_min", "median_latency_s")}
    if len(models) < 8:
        print(f"G0 FAIL: only {len(models)} models pass (need >= 8). Substitute per plan §3.3, re-smoke."); return 1
    out = {"frozen": dt.date.today().isoformat(), "gate": "G0", "defaults": draft.get("defaults", {}), "models": models}
    yaml.safe_dump(out, open("roster.yaml", "w", encoding="utf-8"), sort_keys=False)
    print(f"G0 PASS: froze {len(models)} models -> roster.yaml: {', '.join(models)}"); return 0

if __name__ == "__main__":
    sys.exit(main())

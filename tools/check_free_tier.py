"""Audit that every model an agent could run is free-tier (civlab/free_tier.py rules).
    python -m tools.check_free_tier            # audits roster.yaml if present, else roster_draft.yaml
Exit code 1 on any violation — the runner refuses to start in that case.
"""
import os, sys
import yaml
from civlab.free_tier import audit

def main():
    path = "roster.yaml" if os.path.exists("roster.yaml") else "roster_draft.yaml"
    models = yaml.safe_load(open(path, encoding="utf-8"))["models"]
    bad = 0
    print(f"Free-tier audit of {path}:")
    for k, ok, msg in audit(models):
        print(f"  {'OK  ' if ok else 'FAIL'} {k:18s} {msg}"); bad += not ok
    print("RESULT:", "PASS" if not bad else f"FAIL ({bad} violations)")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())

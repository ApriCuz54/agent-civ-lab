"""DEVIATIONS #2 robustness: re-run the confirmatory analyses with every gptoss_20b cell that contains any
NVIDIA-served call removed (cells are matched to calls by the cell_id in each call record's `key`).

    python -m analysis.robust_nvidia [--B 5000] [--perm 10000]

Writes results/v2/_robust_nvidia_{everyday_effects,fingerprints,link2}.{json,md} and _robust_nvidia_cells.json
(per-experiment counts of dropped cells). Removed cells count as missing, so PREREG_B §7's > 20 %-missing rule
can exclude gptoss_20b from an experiment entirely (the conservative outcome).
"""
import argparse, functools, glob, json, os
from analysis import v2data as D

MODEL = "gptoss_20b"


def nvidia_cells(exp):
    bad, seen = set(), set()
    for f in glob.glob(os.path.join(D.ROOT, exp, "_calls", f"{MODEL}.calls*.jsonl")):
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            parts = str(r.get("key", "")).split("|")
            if len(parts) < 2:
                continue
            seen.add(parts[1])
            if r.get("provider") == "nvidia":
                bad.add(parts[1])
    return bad, seen


def bad_any(exp):
    for f in glob.glob(os.path.join(D.ROOT, exp, "_calls", f"{MODEL}.calls*.jsonl")):
        if '"provider": "nvidia"' in open(f, encoding="utf-8").read():
            return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=5000)
    ap.add_argument("--perm", type=int, default=10000)
    a = ap.parse_args(argv)
    drop, report = {}, {}
    for d in sorted(glob.glob(os.path.join(D.ROOT, "*", MODEL))):
        exp = os.path.basename(os.path.dirname(d))
        bad, seen = nvidia_cells(exp)
        cells = [os.path.basename(f)[:-5] for f in glob.glob(os.path.join(d, "*.json"))
                 if not f.endswith((".failed.json", ".attempts.json"))]
        unmatched = [c for c in cells if c not in seen]
        drop[exp] = {c for c in cells if c in bad}
        if unmatched and bad_any(exp):          # key carries no cell_id (a5): drop unmatched cells conservatively
            drop[exp] |= set(unmatched)
        report[exp] = {"cells": len(cells), "dropped_nvidia": len(drop[exp]), "unmatched_to_calls": len(unmatched)}
    orig_load = D.load          # keep the lru_cache: the uncached loader re-reads thousands of files per call

    @functools.lru_cache(maxsize=None)
    def load(exp, model):
        rows = orig_load(exp, model)
        if model != MODEL:
            return rows
        return tuple(r for r in rows if r.get("cell_id") not in drop.get(exp, set()))
    D.load = load
    from analysis import everyday_effects as EE, fingerprints as F, link2 as L2
    for mod in (EE, F, L2):
        if hasattr(mod, "D"):
            mod.D.load = load
    out = os.path.join(D.ROOT, "_robust_nvidia_")
    json.dump(report, open(out + "cells.json", "w"), indent=1)
    EE.main(["--B", str(a.B), "--out", out + "everyday_effects"])
    F.main(["--out", out + "fingerprints"])
    L2.main(["--perm", str(a.perm), "--out", out + "link2"])
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()

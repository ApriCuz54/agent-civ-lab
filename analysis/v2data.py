"""Shared loading + validity rules for the v2 confirmatory analysis (PREREG_B §6–§7, PREREG_A §5).

Only this module reads result files. Rules implemented here:
  * cells live in results/v2/<experiment>/<model>/<cell_id>.json; *.failed.json / *.attempts.json and every directory
    starting with "_" (e.g. _superseded_pilot_r1, _calls) are ignored (PREREG_B §7: superseded cells are never analysed);
  * robustness-only roster keys (temperature variants) are never part of a primary analysis;
  * a model is EXCLUDED from an experiment if its invalid-action rate there exceeds 10 %, or if more than 20 % of the
    experiment's cells are missing for it (PREREG_B §7). The expected cell set is the union of cell_ids produced by any
    primary model for that experiment (all models run the same cells() list), unless --expected is supplied.
No pandas; numpy only.
"""
import glob, json, os
from functools import lru_cache

import yaml

ROOT = os.path.join("results", "v2")
ROSTER = "roster.yaml"
PILOT_MODELS = ("ollama_llama31_8b", "haiku45")
# Interim runs only (never for confirmatory results): skip the ">20% of cells missing" exclusion.
ALLOW_INCOMPLETE = False


@lru_cache(maxsize=None)
def roster():
    return yaml.safe_load(open(ROSTER, encoding="utf-8"))["models"]


def primary_models():
    return [k for k, v in roster().items() if not v.get("robustness_only")]


def meta(model):
    return roster().get(model, {})


@lru_cache(maxsize=None)
def load(exp, model):
    """All completed cells of one model in one experiment, as a tuple of dicts (sorted by cell_id)."""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, exp, model, "*.json"))):
        if f.endswith((".failed.json", ".attempts.json")):
            continue
        out.append(json.load(open(f, encoding="utf-8")))
    return tuple(out)


def models_with_data(exp, include_robustness=False):
    d = os.path.join(ROOT, exp)
    if not os.path.isdir(d):
        return []
    ms = sorted(m for m in os.listdir(d) if not m.startswith("_") and os.path.isdir(os.path.join(d, m)))
    if not include_robustness:
        ms = [m for m in ms if m in roster() and not roster()[m].get("robustness_only")]
    return ms


# calls per cell when a cell has no "calls" field (T4 stores five samples per problem)
_DEFAULT_CALLS = {"t4_ensembles": 5}


def validity(exp, expected_ids=None):
    """{model: {"valid": bool, "reason": str, "cells": n, "expected": n, "invalid_rate": x}} for primary models with data."""
    ms = models_with_data(exp)
    if expected_ids is None:
        expected_ids = set()
        for m in ms:
            expected_ids |= {c["cell_id"] for c in load(exp, m)}
    n_exp = len(expected_ids) or 1
    res = {}
    for m in ms:
        cells = load(exp, m)
        have = {c["cell_id"] for c in cells} & set(expected_ids)
        inv = sum(c.get("invalid", 0) for c in cells)
        calls = sum(c.get("calls", _DEFAULT_CALLS.get(exp, 1)) for c in cells) or 1
        rate = inv / calls
        missing = 1 - len(have) / n_exp
        reason = []
        if rate > 0.10:
            reason.append(f"invalid-action rate {rate:.1%} > 10%")
        if missing > 0.20 and not ALLOW_INCOMPLETE:
            reason.append(f"{missing:.0%} of cells missing > 20%")
        res[m] = {"valid": not reason, "reason": "; ".join(reason) or "ok", "cells": len(have),
                  "expected": len(expected_ids), "invalid_rate": round(rate, 4)}
    return res


def valid_models(exp, exclude=()):
    return [m for m, v in validity(exp).items() if v["valid"] and m not in exclude]


def out_path(name, interim):
    """Confirmatory outputs go to results/v2/_<name>; interim ones to the git-ignored results/_runner/interim/."""
    if interim:
        d = os.path.join("results", "_runner", "interim"); os.makedirs(d, exist_ok=True)
        return os.path.join(d, name)
    return os.path.join(ROOT, "_" + name)

# Offline report reproduction

## What the command verifies

From the repository root, after installing `requirements-reproduce.txt` in a fresh Python 3.12 environment:

```text
python -B -m tools.reproduce --tests
```

The verifier removes credential-bearing environment variables, blocks Python socket connections, runs the mock/unit suite, reconstructs report audit point estimates/descriptive inventories, and creates three PNG figures plus report/article HTML in a separate empty output directory. Windows asyncio's standard-library internal socket pair is allowed; arbitrary loopback/model connections are blocked. This is an application guard for this Python process, not an operating-system network sandbox for arbitrary programs.

It compares every regenerated audit field against the committed `results/report_audit.json`, except historical `saved_input_hashes`. Those byte hashes depend on Git line endings and OS path separators. A canonical manifest independently checks v2 JSON values **and paths**, the roster, and the original root summary CSV rows (retry/failure markers and runner state excluded), before and after execution, so missing/changed episode files fail even if the headline estimate happens to be unchanged. JSON formatting and CRLF/LF changes do not fail that check. Raw episode values are never rewritten.

Numeric comparisons allow `1e-9` absolute or `1e-12` relative roundoff. Counts, dictionary keys, categorical values and list lengths must agree. Three figures must decode as valid PNGs; exact pixels and PNG bytes are not required across plotting/font/platform versions. The authored report Markdown is copied, then rendered with regenerated figures.

## Tested environment

- CPython 3.12.10, Windows x64; clean Git checkout, isolated venv with no system packages.
- All direct/transitive installed package versions are in `requirements-reproduce.txt`.
- Baseline commit `f7d337d`: 45 existing offline tests passed; headline contrasts and A/B totals matched. Phase C Gemini inventory reproduced 38, while the committed report expected 41.
- The discrepancy was three pre-existing, unchanged local result files absent from Git: `C5__s3.json`, `C5__s4.json`, `greedy1__s0.json` under `results/v2/c_dark_commons/gemini_flash_lite/`. They are included as original evidence, with no new model calls or value edits.
- Final clean-checkout validation and commit receipt are recorded in [VALIDATION.md](VALIDATION.md).

## Limits and remaining work

This reproduces the **report audit**, not every historical experiment or confirmatory bootstrap. Saved intervals, adjusted tail scores and Phase C inference are reused. The independent point-estimate checks already in `analysis/report_audit.py` remain intact. Full inference regeneration, Linux/macOS verification, a container/wheel archive and live provider replication remain additional work.

Pip installation requires package access and available wheels; version pins do not archive those packages. Provider keys, caches and local runner state are unnecessary for this workflow. Phase C remains incomplete (Gemini 41/64; gpt-oss 120B 50/64); this fix does not finish the study.

The saved audit reference was created before this verifier. Tests also exercise missing/changed evidence and rejected numerical mismatches; dispatch or successful script execution alone is not called reproduction.

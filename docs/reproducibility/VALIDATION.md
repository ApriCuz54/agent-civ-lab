# Validation worklog · October 13, 2026

Initial baseline: fresh local Git clone at `f7d337d`, isolated venv using Python 3.12.10 / Windows x64. Dependency installation used only the declared requirements. All 45 existing offline mock/unit tests passed. Headline raw contrasts and A/B inventories agreed with the saved audit; Gemini Phase C differed by three untracked pre-existing cells (38 vs 41).

Implementation check: `python -B -m tools.reproduce --tests` passed all 48 tests (three additional failure-path checks), regenerated three valid figures and report HTML, and matched all saved audit fields other than platform-dependent historical input byte hashes. No provider calls; the Python network guard was active. Saved intervals were reused. The manifest was subsequently expanded to cover the roster and root CSV summaries too; the final receipt below verifies that expanded manifest.

Vault worklog: `700 Research/Agent Civilizations/Research Worklog.md`. Seventeen notes reorganized, no deletions; typed evidence folders retained. Current note wiki links and anchors checked; one original ambiguous basename in an immutable raw report remains explicitly recorded. Protected question region SHA256: `365e2c1aad0658f853bce6e13594e330ba38435db7ceff40be9ff5f49911775d`.

The initial test guard incorrectly blocked Windows asyncio's internal socketpair, producing artificial test failures. It was corrected to permit the standard-library internal pair while blocking arbitrary connections; the suite then passed. This was a validation harness issue, not a provider or experiment failure.

## Final clean-checkout receipt

- Tested implementation commit: `b8a20d8c3ee4f2a87bc893671b7bbfd912eb38b5`.
- A second fresh Git clone and a second isolated venv installed **only** `requirements-reproduce.txt`.
- `python -B -m tools.reproduce --tests`: **48 passed**, all saved audit fields matched except documented platform-dependent historical byte hashes.
- Evidence manifest: **8,104 non-retry/non-failure v2 JSON files, 12 original root summary CSVs and roster**; SHA256 `9ac5b1a12b8ff387073702e94d0e48f5edfcad7f0b55fb2389449cfd38d02bbc`. The file count includes saved aggregates and historical/pilot records, not 8,104 independent episodes.
- Three valid PNGs, report/article/audit HTML, preserved raw values. `git status --short` after the clean run was empty. No API/model calls.
- Machine-readable [verification receipt](verification_receipt.json). Original session logs and pre-cleanup note backups are in ignored `_consolidation/2026-10-13/`.
- Implementation and validation changes are authorized for origin/main; push receipt is recorded in the Vault worklog after the actual push.

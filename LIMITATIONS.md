# Limitations & threats to validity

This project is a small, cheap, reproducible probe of LLM-agent social behavior, not a
finished paper. This document states honestly what the results do and do not support. It is
maintained alongside the code; a hostile-reviewer pass (2026-09-17) drove most of it, and a
rigor pass addressed the items marked **[fixed]** / **[measured]** below.

## Scope of the claims

**Every quantitative result is Claude Haiku 4.5**, on a small number of dates, with extended
thinking disabled. Read all findings as "Haiku 4.5, thinking off" — not "LLM agents" in
general. **Cross-model replication (Sonnet, and ideally a third family) is future work**: it
was attempted 2026-09-17 but Sonnet is rationed on the subscription used (the silent
Sonnet→Haiku fallback rate climbs with use), so no clean Sonnet arm exists yet. The harness
is ready for it (`--model sonnet`, strict model-family guard); see `CROSS_MODEL_RUN_LOG.md`.

## What the rigor pass fixed or measured (2026-09-17)

- **[fixed] GovSim reproducibility & data integrity.** Seeding used Python's per-process-salted
  `hash()`, so "seed 1" was not reproducible and produced conflicting duplicate rows; the
  "0/3 survived" headline had silently dropped a *thinking-ON* cached run that survived. Now:
  deterministic `hashlib` seeding, dedup-on-write, and a `think_enabled` column. Condition A
  is honestly **0/3 with thinking off; the one thinking-on run survived** — which is exactly
  why the thinking-off confound (below) matters.
- **[measured] Parse-fallback bias is latent, not real.** The move/answer parsers default to a
  pro-cooperation / last-integer value on unparseable output. Re-auditing every cached
  response: **0 / 3648 game moves, 0 / 840 answers, 0 / 1080 prices** ever hit the fallback.
  So this biases nothing in the current Haiku data, but is a real risk for noisier models and
  must be hardened (flag/drop, don't default) before cross-model runs.
- **[measured] Reproducible statistics.** CI code now lives in `civlab/stats.py` (cluster
  bootstrap + Holm–Bonferroni). Recomputing correctly changes two things:
  - The practical demo's CIs, clustered by problem, are much wider than the naive pooled
    ones shipped earlier (rushed [0.43,0.77], persona [0.53,0.86], vote3 [0.43,0.79]). The
    three no-reasoning conditions are **not** statistically distinguishable from each other;
    only the reasoning family (verify/plain ≈ 99%) separates cleanly.
  - Under Holm correction, the IPD defection triggers survive (p≈0.007). The pricing
    "avoid price wars" collusion effect did not survive at n=4 seeds (p=0.026, underpowered);
    **re-run at n=8 seeds it now survives** (mean 0.96 vs control 0.24, p<0.001, Holm thr 0.006).
    "Long-run profits" (0.41) remains n.s. — so the corrected claim is that *one* phrase reliably
    induces collusion, not two.
- **[quarantined] The Levers "Sonnet" arm is void** — 223 of 224 rows were served by Haiku
  under the old fallback bug (see `results/levers/CONTAMINATION_NOTE.txt`).

## Known limitations still open (future work)

- **"ESS" language.** The invasion/reputation/stealth results are single-episode payoff
  snapshots, not a dynamical stability test. A replicator/imitation driver (`run_replicator.py`,
  copy-the-richer over generations, anonymous vs reputation) is written and smoke-validated
  (a defector minority rises under anonymity, is contained under reputation) but the full run
  is pending model-call budget. Until it lands, prefer "single-episode invasion payoff
  advantage" over "ESS".
- **Idealized reputation.** The image score is truthful, global and noiseless. A
  recency-weighted / one-strike variant (`run_recency.py`, `civlab/games/reputation.py`
  `REP_MODES`) is written to test whether it closes the trust-then-betray hole; full run
  pending budget.
- **Ceilings & power.** Cooperation sits at 1.00 in many cells and coding pass-rate at ~95%,
  so several "seeds" carry little independent information and small effects are hidden. Higher
  temptation payoffs, larger populations, longer horizons, and more seeds are needed.
- **Thinking-off confound — partially demonstrated.** Nearly all runs disable extended
  thinking for cost. A `--think` factorial (`run_govsim.py`) now confirms this matters: the
  no-enforcement commons (condition A) collapses **0/3 with thinking off** but a **thinking-on
  run survived** (catch 240, lake intact). So "institutions don't emerge / the commons
  collapses" is confounded with disabling deliberation. Only n=1 on the thinking-on side —
  extended thinking throttles to ~2 calls/min on this subscription — so a powered factorial
  (API key / off-peak) is still owed. See `results/rigor_c4_thinking_govsim.txt`.
- **Practical demo construct validity — REBUILT (`run_practical2.py`).** The v1 demo had
  "rushed"/"persona" forbid showing work (a chain-of-thought ablation mislabeled as urgency),
  and its `vote3` fanned out the no-reasoning prompt (a stacked baseline). The rebuild adds the
  fair arms — persona and a 3-agent vote both *with reasoning allowed* — and clustered CIs.
  Result (Haiku 4.5, 96 attempts/condition): reasoning-off family ≈ 60–68%, reasoning-on family
  ≈ 99–100%. **Reasoning is the whole lever**: a verify pass (99%) adds nothing over plain
  reasoning (100%); a persona is null in both regimes; and a fair 3-reasoning-agent vote (99%)
  matches one reasoning agent at 3× cost. The item suite is disclosed as selected for a
  mid-difficulty band, so the *size* of the gap is a property of that choice; the *direction* is
  robust. The public one-pager was rewritten to match.
- **Single population design, short horizons, scripted (non-learned) invaders.**

## What is well-supported (Haiku 4.5)

Large, zero-variance, correctly-hedged effects: "avoid price wars" → monopoly pricing;
"trust no one" / "only this round matters" → immediate defection (survives correction); the
Axelrod fingerprint (nice, provocable, won't exploit AllC, loses to AllD); and, in the
practical demo, the clean separation between reasoning (~99%) and no-reasoning (~61–71%).

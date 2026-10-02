# Program v2 — study summary (goals, execution, findings, next steps)

**Status (2026-10-02):** Phase A (game battery) and Phase B (everyday tasks) are **complete** (6,460 / 6,460 cells) and the
pre-registered confirmatory analysis is **done and independently verified**. Phase C ("commons in the dark") has its
confirmatory 8-model result; the 4 free-tier cloud models are still running for the 12-model addendum (≈ 2026-10-08).
This file is the single entry point; every number below links to a generated result file. Live status: `RUNLOG.md`
(top block). Plan: `docs/v2/PROGRAM_PLAN.md`. Pre-registrations: `prereg/`.

## 1. Goal

**Q0.** Can what we learn from multi-agent systems, viewed through game theory, be turned into instructions and system
designs that measurably improve AI agents on everyday tasks, across models and not just on one?

v1 (one model, Claude Haiku 4.5) found striking game behaviours, e.g. "avoid price wars" → full collusion, "trust no
one" → early defection, lifetime reputation gamed by trust-then-betray. v2 asks whether those are general and useful.
Q0 is broken into four links, each with a pre-registered test:

| Link | Claim | Test |
|---|---|---|
| L1 Generality | The game behaviours appear across many models | Phase A battery, PREREG_A H-A1–H-A6 |
| L2 Prediction | A model's game "fingerprint" predicts its everyday behaviour | 6 capability-controlled partial correlations (PREREG_B §6.5) |
| L3 Transfer | Game-derived interventions improve everyday tasks, beat a length-matched placebo (and ideally a domain expert) | Phase B, H-B1–H-B10, E1–E3 |
| L4 Value | The gain is big enough to matter | Pre-registered practical thresholds (PREREG_B §6.4) |

Six principles are scored: P1 wording risk, P2 reciprocity/precedent, P3 recent environment-computed reputation,
P4 collective (universalization) framing, P5 ensemble diversity, P6 deliberation (positive control).

## 2. Design

- **Models (12, primary):** Claude Haiku 4.5; Qwen3.8-27B, gpt-oss-20b, gpt-oss-120b (Groq); Gemini 3.1 Flash Lite;
  Ministral 8B; Nemotron-3 Super 120B (NVIDIA); local Ollama Llama 2 7B, Llama 3 8B, Llama 3.1 8B, Llama 3.2 3B,
  Qwen2.5 7B. Six families, three size tiers, 2023–2026 generations. T = 0.7 for non-Claude models; temperature
  sensitivity copies (T = 0.3 / 1.0) of two models. Everything on free tiers (enforced by `civlab/free_tier.py`).
- **Phase A** (`experiments/v2/a*`): IPD phrases (A1), pricing duopoly (A2), Axelrod panel (A3), reputation /
  stealth / forgery (A4), naming game collective bias (A5), commons (A6), plus an LLM-counterpart robustness check (C1).
- **Phase B** (`experiments/v2/t*`): T1 negotiation, T2 choosing which worker agent to trust, T3 shared team budget,
  T4 ensembles (+ T4b answer-only), T5 refund desk with a sourced, pre-classified phrase panel. Arms: control, risky
  phrase, game-derived, length-matched placebo, domain expert, answer-only. All scoring is automatic; no LLM judges.
- **Phase C** (added 2026-09-28, `prereg/PREREG_C.md`): four agents share a regrowing source; an information ladder from
  a black box (C0) to full rules, others, transparency and talk (C5), plus greedy-agent, unequal-need, identity and
  known-end extensions and probe controls. A per-decision SAFE_TOTAL belief probe separates "doesn't understand the
  limit" from "understands and takes anyway".
- **Statistics:** hierarchical bootstrap (models, then seeds/cells), Holm–Bonferroni within families, sign
  consistency, pre-registered exclusion rules (invalid-action rate > 10 % or > 20 % cells missing).
- **Rigor trail:** pre-registrations committed before full runs (PREREG_A/B `de3f42b`, PREREG_C `611852f`);
  every post-registration change in `prereg/DEVIATIONS.md`; every implementation choice in `DECISIONS.md`.

## 3. Execution

- Runs executed unattended on the owner's Windows PC (scheduled runner every 15 min, autosync commit+push), with agent
  check-ins every ~10 h logged in `RUNLOG.md` (Sessions 0–34). Infrastructure and rules: `AGENT_HANDBOOK.md`.
- Free-tier daily caps were the binding constraint (Groq 200k tokens/day, Gemini ≈ 500 requests/day). Quota-parking,
  per-cell date checks and a 2 h process recycle kept the queue moving (harness fixes logged in `RUNLOG.md`; `tools/run_queue.py`, `civlab/providers.py`).
- Deviations: #1 Phase C confirmatory uses the 8 models that finished first (cloud 4 = addendum); #2/#2a gpt-oss-20b
  falls back to the same weights on NVIDIA's free tier after Groq's daily cap (120b retired on NVIDIA, stayed Groq).
- Timeline: plan 2026-09-23 → pilot gates 09-25 → full run 09-25 to 10-02 → confirmatory analysis + verification
  10-02 → Phase C addendum ≈ 10-08.

## 4. Findings (confirmatory)

**Scorecard** (`results/v2/_scorecard.md`):
`P1 partial · P2 no · P3 partial · P4 no · P5 no · P6 (pos. control) T · L1 2/6 general · L2 no`

**Answer to Q0 (so far): mostly no.** No game-derived intervention beat the length-matched placebo or the domain-expert
arm on any everyday task (H-B2, H-B3, H-B5, H-B6, H-B8 and E1–E3 null), and no practical-value threshold was met. What
transfers is the *warning* side of two principles, not their fixes:

| Test | Result | Models |
|---|---|---|
| H-B4 (P3) | Judging workers by **self-reported** records instead of a lifetime record cuts post-betrayal accuracy by 9.9 points (Holm p 0.002) | 12/12 same sign |
| H-B7 (P1) | **Harmful rubric phrasing** cuts refund-desk balanced accuracy by 11.7 points vs control (Holm p 0.002) | 8/11; gpt-oss ×2 and Nemotron unaffected |
| H-B10 (P1) | Harmful vs benign real-world phrases: −10.9 points (validates the phrase rubric) | 8/11 |
| H-B9 (P6, positive control) | Answer-only (no reasoning) is 28.4 points less accurate | 8/8 |
| H-B3 (P3 fix) | Recent, system-computed reputation vs lifetime: +3.1 points, Holm p 0.36 (not significant) | 8/12 |
| H-B5 (P4) | Shared-budget task collapsed in every arm (0/36 survive) — a floor, so P4 is untested rather than refuted; game_U delays the lock (2.25 vs 1.47 weeks, descriptive) | — |

- **L1 generality** (`results/v2/_fingerprints.md`): 2 of 6 v1 behaviours are general — "avoid price wars" raises
  collusion (10/12 models) and recency weakens the stealth defector while forgery restores it (12/12).
- **L2 prediction** (`results/v2/_link2.md`): no pair qualifies; game fingerprints don't predict everyday behaviour
  (low power with 8–12 models).
- **Reasoning models** (gpt-oss ×2, Qwen3.8) were immune to manipulation in T5 but were excluded from T4b for invalid
  answers (~28 %).
- **Verification** (`results/v2/_verification.txt`): an independent agent re-derived the exclusions, H-B4, H-B5, H-B7 and
  H-B9 from raw cells without the project's analysis code — all match.
- **Robustness** (`results/v2/_robust_nvidia_*`, DECISIONS #23): removing every gpt-oss-20b cell with an NVIDIA-served
  call changes no verdict.

**Phase C, confirmatory 8 models** (`results/v2/_phase_c.md`, verified by `analysis/verify_phase_c.py`):
- H-C6 supported: at C3–C4 agents request more than their *own* stated safe share in ~74 % of decisions (8/8 models) —
  they understand the limit and take anyway.
- H-C3 supported: learning that others share the source lowers the round-1 take (−1.33× sustainable share, Holm 0.028;
  not robust to dropping the pilot models or Haiku).
- H-C2 (+2.92×, Holm 0.072), H-C5 talk (+6.3 stock, Holm 0.15), H-C1 and H-C4 not significant; H-C7 not testable.
- In the black box, 7/8 models take almost nothing (stock 92); once the level is visible, groups crash (stock 17);
  9 of 447 crashed groups ever recovered. A needy agent gets more mainly because it asks for more (X3).

## 5. Limitations

Twelve models limit L2 power; free-tier hosting forced one host deviation; T3 hit a floor; Haiku ran at its SDK default
temperature; the Phase C confirmatory sample is 8 models (addendum pending). Full list: `LIMITATIONS.md` (v1) and the
per-task records in `docs/v2/records/`.

## 6. Next steps

1. Phase C 12-model addendum when qwen38_27b, gptoss_120b and gemini_flash_lite finish (≈ 2026-10-08):
   `python3 -m analysis.phase_c --models all --out-name phase_c_addendum` and the cloud-4 run; report with and without
   gptoss_20b (all its Phase C cells used NVIDIA).
2. Lab record v2 and paper v2 from the confirmatory outputs; the practical playbook (what to remove from prompts, how to
   pick trusted workers, when reasoning matters).
3. Owner's "explain it unaided" pass over `DECISIONS.md` (PROGRAM_PLAN §13.3), then article / LinkedIn drafts
   (publishing is the owner's decision).
4. Follow-ups worth a new pre-registration: a non-floored commons task for P4; larger model sets for L2.

## 7. File map

| What | Where |
|---|---|
| Plan, red-team review | `docs/v2/PROGRAM_PLAN.md`, `docs/v2/RED_TEAM_REVIEW.md` |
| Pre-registrations, deviations | `prereg/PREREG_A.md`, `PREREG_B.md`, `PREREG_C.md`, `DEVIATIONS.md` |
| Decisions, run log | `DECISIONS.md`, `RUNLOG.md` |
| Raw cells and call logs | `results/v2/<experiment>/<model>/`, `results/v2/<experiment>/_calls/` |
| Confirmatory outputs | `results/v2/_scorecard.md`, `_everyday_effects.md`, `_fingerprints.md`, `_link2.md`, `_phase_c.md` |
| Verification, robustness | `results/v2/_verification.txt`, `_phase_c_verification.txt`, `_robust_nvidia_*` |
| Analysis code, tests | `analysis/`, `tests/` (45 tests) |
| Task records | `docs/v2/records/` |

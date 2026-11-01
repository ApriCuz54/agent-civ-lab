# Experiment record: Phase E (e_axelrod, e_tasks)

## Goal and link
Which operator-controlled design choices improve outcomes for the user when an agent deals repeatedly with others?
Tests L3 and L4 for P2 and P3, plus forgiveness and exit as new design choices. Plan: docs/v2/PHASE_E_PLAN.md.

## Setup
- **Code:** civlab/everyday/e_repeated.py (rules, arms, counterparts), experiments/v2/e_tasks.py (Stage 1),
  experiments/v2/e_axelrod.py (Stage 0), tests/test_phase_e.py, analysis/phase_e_pilot.py.
- **Stage 1:** 4 task families × 8 arms × 4 counterparts × seeds × 10 rounds. Full design 512 cells per model at 4 seeds.
- **Stage 0:** 9 classic strategies × seeds × 10 rounds with neutral labels.
- **Pairing:** failed actions, names, records and evidence depend only on task, counterpart and seed, never arm or model.
- **Choices beyond the plan:** DECISIONS #30.

## Execution log
- 2026-10-31: built; suite 79/79. Local smoke on ollama_llama31_8b: 54 calls, 0 invalid, 4/4 comprehension correct.
- 2026-10-31: pilot queued as p1_ (1 seed; 137 cells on each of ollama_llama31_8b, ministral_8b, nemotron_ultra).
- 2026-11-01: p1_ complete (411 cells, 0 failed, 0 invalid). Noise and `serve` fixed (DECISIONS #31).
- 2026-11-01: p2_ complete (100 cells, 0 failed, 0 invalid). prereg/PREREG_E.md written; full run not started.

## Findings
None. Pilot cells are calibration only and are never analysed as results.

## Conclusion
Pending. prereg/PREREG_E.md must be in a pushed commit before any confirmatory cell runs.

## Deviations
None yet (no pre-registration exists).

# Experiment record: T3 Shared team budget

> Template: templates/EXPERIMENT_RECORD.md. Update every session that touches this experiment.

## 1. Goal and link to the north star
- **Tests:** L3/L4 for P4 (collective-consequence framing); L2 correlation C5 (with A6).
- **Pre-registered hypotheses (final wording goes in prereg/):** H-B5 (game_U > placebo, week-8 survival); E2 (game_U > expert).
- **The result that would change the scorecard:** a pooled effect in the predicted direction that survives Holm, beats placebo, and holds in ≥ 2/3 of valid models (plan §9.2); otherwise the principle is scored partial / does not transfer.

## 2. Setup
- **Code:** civlab/everyday/t3_budget.py, experiments/v2/t3_budget.py (built 2026-09-25; offline tests in tests/test_everyday.py incl. scripted-policy sanity tests).
- **Design:** arms control, game_U (universalization), game_T (transparency panel), expert, placebo × seeds 0–2; 4 agents × 8 weeks; pool 100, doubling, cap 100, lock < 10; rotating service order.
- **Metrics:** primary: pool unlocked at week 8; secondary: total credits used, Gini, week-1 over-request ratio (vs 12.5 per team).
- **Size:** 15 runs, ≤ 480 calls per model.
- **Calibration band (G3):** control survival in [0%, 70%] pooled over pilot models; knob: lock threshold 10 → 5 or pool 100 → 80.
- **Models:** frozen roster.yaml (gate G0). Temperature 0.7 (non-Claude); Haiku at SDK default.

## 3. Execution log
| Date | Agent/session | What was run | Cells done/total | Problems and fixes |
|---|---|---|---|---|
| 2026-09-25 | Claude (Cowork) session 5 | Module written and tested offline; pilot queued (ollama_llama31_8b on the PC; haiku45 from the cloud workspace) | – | – |

## 4. Findings
- None yet (no numbers are reported until produced by an analysis/ script).

## 5. Conclusion
- Pending.

## 6. Deviations
- None.
